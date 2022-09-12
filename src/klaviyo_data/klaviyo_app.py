import sys
import requests
import logging
import pandas as pd
from time import sleep
from sqlalchemy.engine import Engine as EngType
from sqlalchemy import Table, MetaData, insert
from datetime import timedelta, datetime as dt
from dateutil import parser
from pandas import DataFrame
from typing import List, Tuple, Optional, Generator
from configparser import ConfigParser, SectionProxy
import klaviyo_sdk
from klaviyo_data.sql_app import get_engine, id_gen, data_qry
from klaviyo_data.vars import MetricConfig, CampaignConfig
from klaviyo_data.data_work import campaign_lists, flow_lists, metric_parse
from klaviyo_data.configure import Config
from klaviyo_data.templates import TemplateFactory


logger = logging.getLogger()
output_file = logging.FileHandler('klaviyo.log')
output_stdout = logging.StreamHandler(sys.stdout)

logger.addHandler(output_file)
logger.addHandler(output_stdout)
logger.level = logging.DEBUG

uri = 'https://a.klaviyo.com'

DEFAULT_METRICS = {
    "Placed Order": "J8wEZQ",
    "Received Email": "K8EZcU",
    "Clicked Email": "Kdifyi",
    "Marked Email as Spam": "KHctvU",
    "Ordered Product": "LxXB8W",
    "Unsubscribed": "MvCm2p",
    "Opened Email": "My7Vk2",
}

BACKOFF_FACTOR = 1.3
TOTAL_RETRIES = 10


class KlaviyoData:
    def __init__(self, config_dir: str = 'config.ini', config_dict: dict = {}):
        if config_dir is not None:
            self.configuration = Config(config_dir, conf_dict=config_dict)
        else:
            self.configuration = Config(conf_dict=config_dict)
        self.call_limit_s = 60
        self.config_parser: ConfigParser = self.configuration.parser
        self.klaviyo_conf: SectionProxy = self.configuration.klaviyo
        self.engine: EngType = get_engine(self.klaviyo_conf)
        self.priv_key: str = self.klaviyo_conf['private_key']
        self.pub_key: str = self.klaviyo_conf['public_key']
        self.metric_config = MetricConfig()
        self.campaign_config = CampaignConfig()
        self.db: Optional[str] = self.klaviyo_conf['database']
        self.start_date: Optional[dt] = None
        self.end_date: Optional[dt] = None
        self.pspdfkit_api: Optional[str] = self.klaviyo_conf.get(
            'pspdfkit_api')
        self.start_str, self.end_str = self.date_config()
        if not self.start_date or not self.end_date:
            raise ValueError

    def templates_factory(self) -> TemplateFactory:
        return TemplateFactory(self.klaviyo_conf, self.engine)

    def date_config(self) -> Tuple[str, str]:
        """Get dates from configuration."""
        btw = []
        start_date = ''
        end_date = ''
        if self.klaviyo_conf.get('start', '') != '' \
                and self.klaviyo_conf.get('end', '') != '':
            btw = [parser.parse(self.klaviyo_conf.get('start')),
                   parser.parse(self.klaviyo_conf.get('end'))]
            start_date, end_date = self.btw_config(btw)
            return start_date, end_date

        days = self.klaviyo_conf.getint('days', 30)
        start = dt.now() - timedelta(days=days)
        self.start_date = start
        start_date = start.strftime("%Y-%m-%d")
        end = dt.now()
        self.end_date = end
        end_date = end.strftime("%Y-%m-%d")
        return start_date, end_date

    def btw_config(self, btw: List[dt]) -> Tuple[str, str]:
        """Parse between dates configuration."""
        if btw[0] < btw[1]:
            self.start_date = btw[0]
            self.end_date = btw[1]
            start_date = btw[0].strftime("%Y-%m-%d")
            end_date = btw[1].strftime("%Y-%m-%d")
        else:
            self.start_date = btw[1]
            self.end_date = btw[0]
            start_date = btw[0].strftime("%Y-%m-%d")
            end_date = btw[1].strftime("%Y-%m-%d")
        return start_date, end_date

    def pull_metrics(self) -> pd.DataFrame:
        client = klaviyo_sdk.Client(self.priv_key)
        cols = ['id', 'name']
        tbl = 'metrics'
        metrics = client.Metrics.get_metrics()
        metrics_df = pd.DataFrame.from_records(metrics.get('data'))
        metrics_df = metrics_df[cols]
        self.sql_replace(tbl, metrics_df.to_dict(orient='records'))
        return metrics_df

    def pull_campaigns(self) -> None:
        endpoint = '/api/v1/campaigns'
        tbl = 'CampaignList'
        total_df = pd.DataFrame()
        includes_df = pd.DataFrame()
        excludes_df = pd.DataFrame()

        for resp in self.paginator(endpoint):
            data_df, includes_list, excludes_list = campaign_lists(resp)
            if isinstance(includes_list, DataFrame) and len(includes_list) > 0:
                includes_df = pd.concat([includes_df, includes_list],
                                        ignore_index=True)
            if isinstance(excludes_list, DataFrame) and len(excludes_list) > 0:
                excludes_df = pd.concat([excludes_df, excludes_list],
                                        ignore_index=True)
            total_df = pd.concat([total_df, data_df], ignore_index=True)

        data_qry(self.engine, self.klaviyo_conf, tbl, total_df)
        if isinstance(includes_df, pd.DataFrame) and len(includes_df) > 0:
            data_qry(self.engine, self.klaviyo_conf, "CampaignIncludes",
                     includes_df)
        if isinstance(excludes_df, pd.DataFrame) and len(excludes_df) > 0:
            data_qry(self.engine, self.klaviyo_conf, "CampaignExcludes",
                     excludes_df)
        return

    def sql_replace(self, tbl: str, data: List[dict]) -> None:
        meta = MetaData()
        tbl_obj = Table(tbl, meta, autoload_with=self.engine)
        with self.engine.begin() as con:
            con.execute(f"TRUNCATE TABLE {tbl}")
            con.execute(insert(tbl_obj), data)

    def pull_flows(self) -> None:
        flow_endpoint = '/api/v1/flows'
        tbl = 'FlowList'
        full_df = pd.DataFrame()
        for resp in self.paginator(flow_endpoint):
            data_list = flow_lists(resp)
            if not isinstance(data_list, DataFrame) or len(data_list) < 1:
                raise Exception("Error converting flow list to dataframe")
            full_df = pd.concat([full_df, data_list], ignore_index=True)
        self.sql_replace(tbl, full_df.to_dict(orient='records'))
        return

    def call_klaviyo(self, endpoint: str, params,
                     headers=None, body='', method='GET') -> dict:
        if headers is None:
            headers = {}
        url = uri + endpoint
        param = {'api_key': self.priv_key}
        head = {"Accept": "application/json"}
        param.update(params)
        if headers is not None:
            head.update(headers)
        call_num = 0
        while call_num < TOTAL_RETRIES:
            call_num += 1
            resp = requests.request(method, url, headers=head, params=param)
            if resp.status_code == 200:
                self.call_limit_s = 1
                break
            elif resp.status_code == 429:
                self.call_limit_s = self.call_limit_s * 2
                sleep(self.call_limit_s)
            elif resp.status_code in [400, 401, 403, 404]:
                raise Exception(f"Error {resp.status_code}")
        if resp:
            return resp.json()
        else:
            return {}

    def paginator(self, endpoint: str,
                  data_key: str = 'data', params: Optional[dict] = None
                  ) -> Generator:
        page: int = 0
        end: int = 0
        total: int = 2
        if params is None:
            params = {}
        params.update(
            {
                'page': page,
                'count': 100,
            }
        )
        while end < total - 1:

            response = self.call_klaviyo(endpoint, params)
            if response.get(data_key) is None:
                print('no data found')
                raise Exception('Error in dictionary response %s not found',
                                data_key)
            data_list = response.get(data_key)
            yield data_list
            if not isinstance(response, dict):
                break
            end = response.get('end', 0)
            total = response.get('total', 0)
            page = response.get('page', 0)
            if end == 0 or total == 0:
                break
            total = total - 1
            page += 1
            params = {
                'page': page,
                'count': 100,
            }

    def metric_data(self,
                    id: str,
                    start_dt: dt,
                    where_keys: dict,
                    default_where: str,
                    end_dt=None
                    ) -> DataFrame:

        start = dt.strftime(start_dt, "%Y-%m-%d")
        if end_dt is not None:
            end = dt.strftime(end_dt, "%Y-%m-%d")
        else:
            end = dt.strftime(start_dt + timedelta(days=30), "%Y-%m-%d")

        full_df = pd.DataFrame(columns=['id', 'date', 'metric_id',
                                        'values', 'measure'])
        measures: dict = {**self.metric_config.metric_measures}
        metrics = DEFAULT_METRICS
        for metric_name, metric_id in metrics.items():
            for measure in measures.get(metric_id, []):
                where = {'where': '[["' +
                         where_keys.get(metric_id, default_where) +
                         '","=","' + id + '"]]'}
                endpoint = '/api/v1/metric/' + metric_id + '/export'
                query = {
                    'unit': 'day',
                    'measurement': measure,
                    'count': 100,
                    'start_date': start,
                    'end_date': end
                }
                query.update(where)
                for results in self.paginator(endpoint, 'results', query):
                    if len(results) == 0:
                        logger.debug(f"No results found for \
                                     {measure} with id - {id}")
                        break
                    try:
                        partial_df = metric_parse(results)
                    except ValueError:
                        continue

                    partial_df.insert(0, 'id', id)
                    partial_df.insert(len(partial_df.columns)-1,
                                      'metric_id', metric_id)
                    partial_df.insert(len(partial_df.columns),
                                      'measure', measure)
                    full_df = pd.concat([full_df, partial_df],
                                        ignore_index=True)

        if not full_df.empty:
            full_df['values'] = full_df['values'].astype('float')
            full_df['date'] = pd.to_datetime(full_df['date'])
        return full_df

    def campaign_metrics(self):
        metric_where = self.metric_config.campaign_where
        today = dt.today().date()
        if self.start_str is None:
            start_date = today - timedelta(days=30)
        else:
            start_date = dt.strptime(self.start_str, '%Y-%m-%d').date()
        if self.end_str is None:
            end_date = today
        else:
            end_date = dt.strptime(self.end_str, '%Y-%m-%d').date()

        logger.debug(
            'Pulling campaign data from - ' + start_date.strftime(
                '%Y-%m-%d'))
        camp_list = id_gen(self.engine, 'CampaignList')

        for row in camp_list:
            if row.sent_at is None or \
                    row.sent_at.date() < (start_date - timedelta(days=2)) or \
                    (row.sent_at.date() - end_date).days > 7:
                continue
            data = self.metric_data(row.id,
                                    (row.sent_at - timedelta(days=2)),
                                    metric_where,
                                    '$message')
            if len(data.index) == 0:
                continue
            data.rename(columns={'id': 'campaign_id',
                                 'num_recipients': 'recipients'},
                        inplace=True)
            data_qry(self.engine, self.klaviyo_conf, "CampaignMetrics",
                     data)

    def flow_metrics(self):
        flow_where = self.metric_config.flow_where
        flow_list = id_gen(self.engine, 'FlowList')
        current_date = dt.today()
        thirty_days = timedelta(days=30)
        current_date -= thirty_days
        end_dt = self.end_date
        date_list = []
        days = (self.end_date - self.start_date).days
        if days > 30:
            start = self.start_date
            end = self.start_date + timedelta(days=30)
            while end <= end_dt:
                date_list.append({'start': start, 'end': end})
                if end == end_dt:
                    break
                start = end + timedelta(days=1)
                end = start + timedelta(days=30)
                if start == end_dt:
                    end = end_dt
                    continue
                if end > end_dt:
                    end = end_dt
        else:
            date_list.append({'start': self.start_date, 'end': end_dt})

        logger.debug('Pulling flow data from - '
                     + current_date.strftime('%Y-%m-%d'))
        for row in flow_list:
            for dt_item in date_list:
                if row.created > dt_item['start'] or \
                        (row.status.lower() in ['draft', 'archived']
                         and row.updated <= dt_item['start']):
                    continue
                data = self.metric_data(row.id, dt_item['start'], flow_where,
                                        '$flow', dt_item['end'])
                if len(data) == 0:
                    continue
                data = data.rename(columns={'id': 'flow_id'})
                data_qry(self.engine, self.klaviyo_conf, "FlowMetrics", data)
