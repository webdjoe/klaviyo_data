from typing import List, Dict, Optional, Union
from sqlalchemy import (MetaData, Table, Column,
                        INTEGER, BIGINT, SMALLINT,
                        DATETIME, Boolean, NVARCHAR, DATE,
                        FLOAT)

list_cols = {
    'camp_lists': [
        'campaign_id',
        'object',
        'id',
        'name',
        'list_type',
        'folder',
        'person_count',
        'campaign_sent_at'
    ],
    'campaigns': [
        'id',
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

}

list_types = {
    'campaign_id': 'str',
    'object': 'str',
    'id': 'str',
    'person_count': 'int64'
}


class CampaignConfig:
    def __init__(self):
        self.cols = ['id',
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


class MetricConfig:
    @property
    def campaign_where(self):
        return {
            'LxXB8W': '$attributed_message',
            'J8wEZQ': '$attributed_message',
            'NSMgUE': '$attributed_message',
            'LZJ94M': '$attributed_message',
            'K8EZcU': '$message',
            'Kdifyi': '$message',
            'My7Vk2': '$message',
            'MvCm2p': '$message',
            'KHctvU': '$message'
        }

    @property
    def flow_where(self):
        return {
            'LxXB8W': '$attributed_flow',
            'J8wEZQ': '$attributed_flow',
            'NSMgUE': '$attributed_flow',
            'LZJ94M': '$attributed_flow',
            'K8EZcU': '$flow',
            'Kdifyi': '$flow',
            'My7Vk2': '$flow',
            'MvCm2p': '$flow',
            'KHctvU': '$flow'
        }

    @property
    def metric_ids(self):
        return {
            "Opened Ticket": "H29kaP",
            "Active on Site": "HqSn3P",
            "Placed Order": "J8wEZQ",
            "Resolved Ticket": "Jbyb4F",
            "Dropped Email": "JtangE",
            "Bounced Email": "K6bqTh",
            "Received Email": "K8EZcU",
            "Clicked Email": "Kdifyi",
            "Marked Email as Spam": "KHctvU",
            "Refunded Order": "KhVvTG",
            "Cancelled Order": "KUWywj",
            "Subscribed to List": "LjcKkh",
            "Subscribed to Back in Stock": "LtkkMy",
            "Ordered Product": "LxXB8W",
            "Viewed Product": "LZJ94M",
            "Unsubscribed": "MvCm2p",
            "Opened Email": "My7Vk2",
            "Checkout Started": "NSMgUE",
            "Updated Email Preferences": "PjVQsb",
            "Unsubscribed from List": "PSWxzc",
            "Fulfilled Order": "PvNjxh",
            "Received Push": "SCUqCS",
            "Clicked SMS": "SwjNUp",
            "Sent SMS": "TYnUtu",
            "Consented to Receive SMS": "UBpX67",
            "Received Automated Response SMS": "UjB9xu",
            "Filled Out Form": "UJx58b",
            "Merged Profile": "UzFzBz",
            "Unsubscribed from SMS": "V9MKmk",
            "Failed to Deliver SMS": "VLNMXX",
            "Received SMS": "XmdFaB",
            "Failed to deliver Automated Response SMS": "XUsUys"
        }

    @property
    def metric_measures(self):
        return {
            'HqSn3P': ['count'],
            'K6bqTh': ['count'],
            'KUWywj': ['count'],
            'NSMgUE': ['count'],
            'Kdifyi': ['count'],
            'SwjNUp': ['count'],
            'UBpX67': ['count'],
            'JtangE': ['count'],
            'XUsUys': ['count'],
            'VLNMXX': ['count'],
            'UJx58b': ['count'],
            'PvNjxh': ['count'],
            'KHctvU': ['count'],
            'UzFzBz': ['count'],
            'My7Vk2': ['count'],
            'H29kaP': ['count'],
            'LxXB8W': ['count', 'value'],
            'J8wEZQ': ['count', 'value'],
            'UjB9xu': ['count'],
            'K8EZcU': ['count'],
            'SCUqCS': ['count'],
            'XmdFaB': ['count'],
            'KhVvTG': ['count'],
            'Jbyb4F': ['count'],
            'TYnUtu': ['count'],
            'LjcKkh': ['count'],
            'MvCm2p': ['count'],
            'PSWxzc': ['count'],
            'V9MKmk': ['count'],
            'PjVQsb': ['count'],
            'LZJ94M': ['count']
        }

    @property
    def metric_measures1(self) -> dict:
        return {
            'value': 'value',
            'count': 'count',
            'recipients': 'count',
            'clicks': 'count',
            'opens': 'count',
            'unsubscribed': 'count',
            'spam': 'count'
        }

    @property
    def metric_ids1(self) -> dict:
        return {
            'value': 'J8wEZQ',
            'count': 'J8wEZQ',
            'recipients': 'K8EZcU',
            'clicks': 'Kdifyi',
            'opens': 'My7Vk2',
            'unsubscribed': 'MvCm2p',
            'spam': 'KHctvU'
        }

    @property
    def metric_type(self) -> dict:
        return {
            'count': 'int32',
            'recipients': 'int32',
            'clicks': 'int32',
            'opens': 'int32',
            'unsubscribed': 'int32',
            'spam': 'int32'
        }

    @property
    def measures(self) -> List[str]:
        return ['value', 'count']


def merge_str(db: str, schema: str, tbl_name: str, col_names: List[str],
              merge_cols: List[str], match_on: Optional[list] = None,
              update: bool = True) -> str:
    insert_list = ",".join(f"[{col}]" for col in col_names)
    source_list = ",".join(f"SOURCE.[{col}]" for col in col_names)
    merge_on = " AND ".join(f"TARGET.[{col}] = SOURCE.[{col}]"
                            for col in merge_cols)
    if update is True:
        if match_on is not None:
            match = " AND " + " AND".join(f"TARGET.[{col}] <> SOURCE.[{col}]"
                                          for col in match_on)
        else:
            match = ""
        if isinstance(match_on, list):
            update_cols = [col for col in col_names if col not in set(
                    merge_cols + match_on)]
        else:
            update_cols = [col for col in col_names if col not in merge_cols]
        update_list = ", ".join(f"TARGET.[{col}] = SOURCE.[{col}]"
                                for col in update_cols)
        return f"""
            MERGE {db}.{schema}.{tbl_name} TARGET
            USING #tmp SOURCE
            ON ({merge_on})
            WHEN MATCHED {match}
            THEN UPDATE SET {update_list}
            WHEN NOT MATCHED BY TARGET
            THEN INSERT ({insert_list})
            VALUES ({source_list});
        """
    return f"""
        MERGE {db}.{schema}.{tbl_name} TARGET
        USING #tmp SOURCE
        ON ({merge_on})
        WHEN NOT MATCHED BY TARGET
        THEN INSERT ({insert_list})
        VALUES ({source_list});
    """


MergeDict: Dict[str, Dict[str, Union[list, str, bool]]] = {
    'CampaignMetrics': {
        "merge_cols": ["campaign_id", "metric_id", "date", "measure"],
        "update": True
    },
    'FlowMetrics': {
            "merge_cols": ["flow_id", "metric_id", "date", "measure"],
            "update": True
    },
    'CampaignExcludes': {
        "merge_cols": ["campaign_id", "id"],
        "update": True
        },
    'CampaignIncludes': {
        "merge_cols": ["campaign_id", "id"],
        "update": True
        },
    'CampaignList': {
        "merge_cols": ["id"],
        "update": True
        },
    'FlowList': {
        "merge_cols": ["flow_id", "id"],
        "update": True
    }
}


class SQLBuilder:
    def __init__(self, db_name) -> None:
        self.db_name = db_name

    def make_db(self) -> str:
        return f"""CREATE DATABASE {self.db_name}"""

    def alter_db(self) -> str:
        return f"""
        ALTER DATABASE {self.db_name}
        SET
        ANSI_NULL_DEFAULT OFF,
        ANSI_NULLS OFF,
        ANSI_PADDING OFF,
        ANSI_WARNINGS OFF,
        ARITHABORT OFF,
        AUTO_CLOSE OFF,
        AUTO_CREATE_STATISTICS ON,
        AUTO_SHRINK OFF,
        AUTO_UPDATE_STATISTICS ON,
        AUTO_UPDATE_STATISTICS_ASYNC OFF,
        COMPATIBILITY_LEVEL = 150,
        CONCAT_NULL_YIELDS_NULL OFF,
        CURSOR_CLOSE_ON_COMMIT OFF,
        CURSOR_DEFAULT GLOBAL,
        DATE_CORRELATION_OPTIMIZATION OFF,
        DB_CHAINING OFF,
        HONOR_BROKER_PRIORITY OFF,
        MULTI_USER,
        NESTED_TRIGGERS = ON,
        NUMERIC_ROUNDABORT OFF,
        PAGE_VERIFY CHECKSUM,
        PARAMETERIZATION SIMPLE,
        QUOTED_IDENTIFIER OFF,
        READ_COMMITTED_SNAPSHOT OFF,
        RECOVERY FULL,
        RECURSIVE_TRIGGERS OFF,
        TRANSFORM_NOISE_WORDS = OFF,
        TRUSTWORTHY OFF
        WITH ROLLBACK IMMEDIATE
    """


class TableBuilder:
    def __init__(self, schema: str = "dbo") -> None:
        self.meta = MetaData()
        self.schema = schema
        self._CampaignLists = self.CampaignList()
        self._CampaignExcludes = self.CampaignExcludes()
        self._CampaignIncludes = self.CampaignIncludes()
        self._Metrics = self.Metrics()
        self._FlowList = self.FlowList()
        self._CampaignMetrics = self.CampaignMetrics()
        self._FlowMetrics = self.FlowMetrics()

    def CampaignList(self) -> Table:
        return Table(
            'CampaignList',
            self.meta,
            Column('id', NVARCHAR(length=255), primary_key=True,
                   nullable=False),
            Column('name', NVARCHAR(length=255)),
            Column('subject', NVARCHAR(length=255)),
            Column('status', NVARCHAR(length=255)),
            Column('status_label', NVARCHAR(length=255)),
            Column('status_id', INTEGER()),
            Column('num_recipients', BIGINT()),
            Column('is_segmented', SMALLINT()),
            Column('message_type', NVARCHAR(length=255)),
            Column('template_id', NVARCHAR(length=255)),
            Column('sent_at', DATETIME()),
            Column('send_time', DATETIME()))

    def FlowList(self) -> Table:
        return Table('FlowList', self.meta,
                     Column('id', NVARCHAR(length=255), primary_key=True,
                            nullable=False),
                     Column('name', NVARCHAR(length=255), nullable=False),
                     Column('object', NVARCHAR(length=255)),
                     Column('status', NVARCHAR(length=255)),
                     Column('archived', Boolean()),
                     Column('created', DATETIME(), nullable=False),
                     Column('updated', DATETIME()))

    def FlowMetrics(self) -> Table:
        return Table('FlowMetrics', self.meta,
                     Column('flow_id', NVARCHAR(length=255),
                            primary_key=True, nullable=False),
                     Column('date', DATE(), primary_key=True, nullable=False),
                     Column('metric_id', NVARCHAR(length=50),
                            primary_key=True, nullable=False),
                     Column('values', FLOAT(precision=53), nullable=False),
                     Column('measure', NVARCHAR(length=50),
                            primary_key=True, nullable=False))

    def CampaignExcludes(self) -> Table:
        return Table('CampaignExcludes', self.meta,
                     Column('campaign_id', NVARCHAR(length=255),
                            nullable=False),
                     Column('object', NVARCHAR(length=255), nullable=False),
                     Column('id', NVARCHAR(length=255), nullable=False),
                     Column('name', NVARCHAR(length=255)),
                     Column('list_type', NVARCHAR(length=255)),
                     Column('folder', NVARCHAR(length=255)),
                     Column('person_count', BIGINT()),
                     Column('campaign_sent_at', DATETIME()))

    def CampaignIncludes(self) -> Table:
        return Table('CampaignIncludes', self.meta,
                     Column('campaign_id', NVARCHAR(length=255),
                            nullable=False),
                     Column('object', NVARCHAR(length=255), nullable=False),
                     Column('id', NVARCHAR(length=255), nullable=False),
                     Column('name', NVARCHAR(length=255)),
                     Column('list_type', NVARCHAR(length=255)),
                     Column('folder', NVARCHAR(length=255)),
                     Column('person_count', BIGINT()),
                     Column('campaign_sent_at', DATETIME()))

    def CampaignMetrics(self) -> Table:
        return Table('CampaignMetrics', self.meta,
                     Column('campaign_id', NVARCHAR(length=255),
                            primary_key=True, nullable=False),
                     Column('date', DATE(), primary_key=True, nullable=False),
                     Column('metric_id', NVARCHAR(length=50),
                            primary_key=True, nullable=False),
                     Column('values', FLOAT(precision=53)),
                     Column('measure', NVARCHAR(length=50),
                            primary_key=True, nullable=False))

    def Metrics(self) -> Table:
        return Table('Metrics', self.meta,
                     Column('id', NVARCHAR(length=255),
                            primary_key=True, nullable=False),
                     Column('name', NVARCHAR(length=255)))

    def Templates(self) -> str:
        return f"""
        CREATE TABLE [{self.schema}].[Templates](
            [file_id] [uniqueidentifier] ROWGUIDCOL DEFAULT (newid()) NOT NULL,
            [id] [nvarchar](20) PRIMARY KEY NOT NULL,
            [updated] [datetime] NOT NULL,
            [created] [datetime] NOT NULL,
            [name] [nvarchar](255) NOT NULL,
            [image_path] [nvarchar](255) NULL,
            [html] [nvarchar](max) NOT NULL,
            [image_blob] [varbinary](max) NULL
        )
        GO
    """


class DateDimension:
    create_table = """
        CREATE TABLE dbo.DateDimension (
        TheDate DATE NULL
        ,TheDay INT NULL
        ,TheDaySuffix CHAR(2) NULL
        ,TheDayName NVARCHAR(30) NULL
        ,TheDayOfWeek INT NULL
        ,TheDayOfWeekInMonth TINYINT NULL
        ,TheDayOfYear INT NULL
        ,IsWeekend INT NOT NULL
        ,TheWeek INT NULL
        ,TheISOweek INT NULL
        ,TheFirstOfWeek DATE NULL
        ,TheLastOfWeek DATE NULL
        ,TheWeekOfMonth TINYINT NULL
        ,TheMonth INT NULL
        ,TheMonthName NVARCHAR(30) NULL
        ,TheFirstOfMonth DATE NULL
        ,TheLastOfMonth DATE NULL
        ,TheFirstOfNextMonth DATE NULL
        ,TheLastOfNextMonth DATE NULL
        ,TheQuarter INT NULL
        ,TheFirstOfQuarter DATE NULL
        ,TheLastOfQuarter DATE NULL
        ,TheYear INT NULL
        ,TheISOYear INT NULL
        ,TheFirstOfYear DATE NULL
        ,TheLastOfYear DATE NULL
        ,IsLeapYear BIT NULL
        ,Has53Weeks INT NOT NULL
        ,Has53ISOWeeks INT NOT NULL
        ,MMYYYY CHAR(6) NULL
        ,Style101 CHAR(10) NULL
        ,Style103 CHAR(10) NULL
        ,Style112 CHAR(8) NULL
        ,Style120 CHAR(10) NULL
        ) ON [PRIMARY]
    """
    create_index = """
        CREATE UNIQUE CLUSTERED INDEX PK_DateDimension
            ON dbo.DateDimension (TheDate)
            ON [PRIMARY]
    """
