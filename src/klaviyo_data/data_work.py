import pandas as pd
from pandas import DataFrame
from typing import Type, Union, List, Tuple
from klaviyo_data.vars import list_cols, list_types


def campaign_lists(data: List[dict]):
    data_df = pd.DataFrame(columns=list_cols.get('campaigns'))

    cols = ['id',
            'name',
            'subject',
            'status',
            'status_label',
            'status_id',
            'num_recipients',
            'is_segmented',
            'message_type',
            'template_id',
            'sent_at',
            'send_time'
            ]

    includes_list = pd.json_normalize(data,
                                      record_path='lists',
                                      meta=['id', 'sent_at'],
                                      meta_prefix='campaign_',
                                      errors='ignore'
                                      )
    if len(includes_list) > 0:
        includes_list = includes_list.astype(list_types)
    else:
        includes_list = None
    excludes_list = pd.json_normalize(data,
                                      record_path='excluded_lists',
                                      meta=['id', 'sent_at'],
                                      meta_prefix='campaign_',
                                      errors='ignore'
                                      )
    if len(excludes_list) > 0:
        excludes_list = excludes_list.astype(list_types)
    else:
        excludes_list = None
    data_df = pd.DataFrame.from_records(data)
    data_df = data_df[cols]
    return data_df, includes_list, excludes_list


def flow_lists(data: List[dict]) -> DataFrame:
    data_df = pd.DataFrame(data)
    return data_df


def metric_parse(data):
    """Parse Klaviyo metric response."""
    if data is None or not data:
        raise ValueError("Error in metric results")
    if len(data) > 1:
        print('results - %s', data.length)
        raise ValueError("Error in result structure")
    everyone = data[0].get('data')
    if everyone is None or len(everyone) < 1:
        raise ValueError("No values found in data key")
    everyone_df = pd.json_normalize(everyone, max_level=2)
    everyone_df['values'] = everyone_df['values'].apply(lambda x: x[0])

    everyone_df = everyone_df[everyone_df['values'] > 0]
    if len(everyone_df) == 0:
        raise ValueError("No data in partial df")
    return everyone_df
