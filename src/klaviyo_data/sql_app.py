import logging
import calendar
from pathlib import Path
from dateutil import parser
from datetime import date, timedelta as td
from configparser import SectionProxy
from typing import Optional
from sqlalchemy import create_engine, MetaData, Table, select, Column, inspect
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine as EngType
from pandas import DataFrame
from klaviyo_data.vars import (merge_str, MergeDict, SQLBuilder,
                               TableBuilder, DateDimension)

DEFAULT_DRIVER = 'ODBC Driver 17 for SQL Server'

logger = logging.getLogger()
logger.level = logging.DEBUG


class DBBuilder:
    def __init__(self, server, port,
                 sa_user: Optional[str] = None,
                 sa_password: Optional[str] = None,
                 windows_auth: bool = False,
                 driver: str = DEFAULT_DRIVER,) -> None:
        """_summary_

        Args:
            server (_type_): _description_
            port (_type_): _description_
            sa_user (Optional[str], optional): _description_. Defaults to None.
            sa_password (Optional[str], optional): _description_. Defaults to None.
            windows_auth (bool, optional): _description_. Defaults to False.
            driver (str, optional): _description_. Defaults to DEFAULT_DRIVER.
        """
        self.port = port
        self.server = server
        self.sa_user = sa_user
        self.sa_password = sa_password
        self.driver = driver
        self.windows_auth = windows_auth
        self.engine: Optional[EngType] = None
        self._script_path: Optional[Path] = None
        self.db_name: Optional[str] = None

    def get_engine(self, database: str = 'master') -> EngType:
        sql_conf = {
            'server': self.server,
            'port': self.port,
            'db_user': self.sa_user,
            'db_pass': self.sa_password,
            'driver': self.driver,
            'database': database,
            'windows_auth': self.windows_auth
        }
        self.engine = get_engine(sql_conf)
        try:
            if self.engine is not None:
                conn = self.engine.connect()
        except SQLAlchemyError as e:
            logger.error(f"Cannot connect to db - {e}")
            return False
        else:
            conn.close()
        return True

    def create_user(self, kv_user: str, kv_password: str,
                    db_name: Optional[str] = None) -> bool:
        if db_name is None and self.db_name is None:
            logger.debug("Klaviyo db_name needed to add user")
            return False
        if db_name is not None:
            self.db_name = db_name
        if self.engine is None:
            self.get_engine()
        if self.engine is None:
            logger.debug("Unable to connect to db")
            return False
        with self.engine.connect().execution_options(
                isolation_level='AUTOCOMMIT') as conn:
            with conn.begin():
                stmt = conn.execute(
                    f"SELECT * FROM [master].[sys].[server_principals]\
                        WHERE name = N'{kv_user}'")
                if stmt.scalar() is not None:
                    logger.debug(f"{kv_user} already exists")
                    return False
                conn.execute(f"CREATE LOGIN {kv_user} \
                    WITH PASSWORD = '{kv_password}'")
        kv_conf = {
            'server': self.server,
            'database': self.db_name,
            'db_user': self.sa_user,
            'db_pass': self.sa_password,
            'port': self.port,
            'windows_auth': self.windows_auth,
            'driver': self.driver
        }
        kv_engine = get_engine(kv_conf)
        if kv_engine is None:
            logger.debug("Unable to connect to Klaviyo db")
            return False
        with self.engine.connect().execution_options(
                isolation_level='AUTOCOMMIT') as conn:
            try:
                stmt = conn.execute(
                    f"SELECT * FROM sys.database_principals \
                        WHERE name = N'{kv_user}'")
                if stmt.scalar() is not None:
                    logger.debug(f"{kv_user} already exists")
                    return False
                with conn.begin():
                    conn.execute(f"CREATE USER [{kv_user}] FOR LOGIN\
                        [{kv_user}]")
                    conn.execute(f"EXEC sp_addrolemember N'db_owner',\
                        N'{kv_user}'")
            except SQLAlchemyError as e:
                logger.error(f"Cannot create user - {e}")
                return False
            else:
                return True

    def build_database(self, db_name: str = 'klaviyo',
                       schema: str = 'dbo') -> bool:
        self.db_name = db_name
        if not isinstance(self.engine, EngType):
            logger.debug("Error: engine not set")
            return False
        sql_obj = SQLBuilder(db_name)
        with self.engine.connect().execution_options(
                isolation_level='AUTOCOMMIT') as conn:
            with conn.begin():
                conn.execute(sql_obj.make_db())
                conn.execute(sql_obj.alter_db())
        return True

    def build_tables(self, db_name: Optional[str] = None,
                     date_start: Optional[str] = None) -> bool:
        if self.db_name and db_name is None:
            logger.debug("Please specify db_name")
            return False
        if db_name is not None:
            self.db_name = db_name
        kv_conf = {
            'server': self.server,
            'database': self.db_name,
            'db_user': self.sa_user,
            'db_pass': self.sa_password,
            'port': self.port,
            'windows_auth': self.windows_auth,
            'driver': self.driver
        }
        kv_engine = get_engine(kv_conf)

        with kv_engine.connect().execution_options(
                isolation_level='AUTOCOMMIT') as conn:
            tbl_class = TableBuilder()
            tbl_class.meta.create_all(bind=conn)
        if date_start is not None:
            build_date_dimension(kv_engine, date_start)
        tester = inspect(kv_engine)
        if tester.has_table("Metrics"):
            return True
        return False


def build_date_dimension(engine: EngType, date_str: str) -> bool:
    date_rows = date_row_builder(date_str)
    with engine.connect().execution_options(
            isolation_level='AUTOCOMMIT') as conn:
        conn.execute(DateDimension.create_table)
        conn.execute(DateDimension.create_index)
    meta = MetaData()
    tbl_meta = Table("DateDimension", meta, autoload_with=engine)
    with engine.connect().execution_options(
            isolation_level='AUTOCOMMIT') as conn:
        conn.execute(tbl_meta.insert(), date_rows)
    return True


def get_engine(sql_conf):
    server = sql_conf['server']
    database = sql_conf['database']
    driver = sql_conf.get('driver', 'ODBC Driver 17 for SQL Server')
    user = sql_conf['db_user']
    port = sql_conf.get('port', "1433")
    password = sql_conf['db_pass']
    if sql_conf.get('windows_auth', False) is True:
        con_url = URL(
            "mssql+pyodbc",
            host=server,
            port=port,
            database=database,
            query={
                "Driver": driver,
                "Trusted_Connection": "yes",
                "TrustedServerCertificate": "yes",
                "Encrypt": "no"
            }
        )
    elif user is not None and password is not None:
        con_url = URL(
            "mssql+pyodbc",
            username=user,
            password=password,
            host=server,
            port=port,
            database=database,
            query={
                "Driver": driver,
                "TrustedServerCertificate": "yes",
                "Encrypt": "no"
            }
        )
    else:
        raise Exception('Error connecting to database,'
                        'check user password and authentication method')
    engine = create_engine(con_url)
    return engine


def id_gen(engine, tbl: str):
    meta = MetaData()
    table = Table(tbl, meta, autoload_with=engine)
    s = select(table)
    with engine.connect() as con:
        result = con.execute(s)
        for row in result:
            yield row


def data_arrange(df: DataFrame) -> list:
    """Arrange dataFrame for inserting into SQL Server"""
    return df.to_dict(orient='records')


def data_qry(engine: EngType,
             config: SectionProxy,
             tbl: str,
             data: DataFrame) -> None:
    db = config['db']
    schema = config.get('schema', 'dbo')
    merge_dict = MergeDict[tbl]
    with engine.begin() as con:
        con.execute("DROP TABLE IF EXISTS #tmp")
        meta = MetaData()
        tbl_meta = Table(tbl, meta, autoload_with=engine)
        columns = []
        col_names = []
        for column in tbl_meta.c:
            col_names.append(column.name)
            columns.append(Column(column.name, column.type))
        tmp = Table('#tmp', meta, *columns)
        tmp.create(con)
        tbl_data = data_arrange(data)
        con.execute(tmp.insert(), tbl_data)
        merge_qry = merge_str(db, schema, tbl, col_names,
                              **merge_dict)  # type: ignore
        con.execute(merge_qry)
        con.execute("DROP TABLE IF EXISTS #tmp")


def get_week_of_month(cal_date) -> int:
    """Get the week of the month starting sunday."""
    cal = calendar.Calendar(6)
    weeks = cal.monthdayscalendar(cal_date.year, cal_date.month)
    for x in range(len(weeks)):
        if cal_date.day in weeks[x]:
            return x + 1
    return 0


def date_row_builder(start_str) -> list:
    """Build rows for DateDimension table."""
    try:
        start_date = parser.isoparse(start_str).date()
    except parser.ParserError:
        logger.debug("Error parsing start date, defaulting to 1/1/2019")
        start_date = date(2019, 1, 1)
    end_date = start_date + td(days=(30*365))
    row_array = []
    current_date = start_date
    while (current_date <= end_date):
        TheDate = current_date
        TheDay = current_date.day
        TheDaySuffix = 'tsnrhtdd'[TheDay % 5 * (
            TheDay % 100 ^ 15 > 4 > TheDay % 10)::4]
        TheDayName = TheDate.strftime('%A')
        TheDayOfWeek = int(TheDate.strftime('%w')) + 1
        TheDayOfWeekInMonth = (TheDay - 1) // 7 + 1
        TheDayOfYear = current_date.timetuple().tm_yday
        IsWeekend = 1 if TheDayOfWeek in [1, 7] else 0
        TheWeek = int(TheDate.strftime('%U')) + 1
        TheISOWeek = int(TheDate.isocalendar().week)
        TheFirstOfWeek = TheDate - td(days=TheDate.isoweekday() % 7)
        TheLastOfWeek = TheFirstOfWeek + td(days=6)
        TheWeekOfMonth = get_week_of_month(TheDate)
        TheMonth = int(TheDate.month)
        TheMonthName = TheDate.strftime('%B')
        TheFirstOfMonth = TheDate.replace(day=1)
        TheLastOfMonth = TheDate.replace(day=calendar.monthrange(
            TheDate.year, TheDate.month)[1])
        TheFirstOfNextMonth = TheLastOfMonth + td(days=1)
        TheLastOfNextMonth = TheFirstOfNextMonth.replace(
            day=calendar.monthrange(TheFirstOfNextMonth.year,
                                    TheFirstOfNextMonth.month)[1])
        TheQuarter = (TheMonth - 1) // 3 + 1
        TheFirstOfQuarter = date(TheDate.year, 3 * (
            (TheDate.month - 1) // 3) + 1, 1)
        TheLastOfQuarter = date(
                TheDate.year + 3 * TheQuarter // 12,
                3 * TheQuarter % 12 + 1, 1) \
            + td(days=-1)
        TheYear = TheDate.year
        TheISOYear = TheDate.isocalendar().year
        TheFirstOfYear = TheDate.replace(month=1, day=1)
        TheLastOfYear = TheDate.replace(month=12, day=31)
        IsLeapYear = (TheYear % 400 == 0) and (TheYear % 100 == 0)
        Has53Weeks = TheLastOfYear.strftime('%U') == '53'
        Has53ISOWeeks = TheLastOfYear.isocalendar().week == 53
        MMYYYY = TheDate.strftime('%m%Y')
        Style101 = TheDate.strftime('%m/%d/%Y')
        Style103 = TheDate.strftime('%d/%m/%Y')
        Style112 = TheDate.strftime('%Y%m%d')
        Style120 = TheDate.strftime('%Y-%m-%d')
        row_array.append(
            {
                'TheDate': TheDate,
                'TheDay': TheDay,
                'TheDaySuffix': TheDaySuffix,
                'TheDayName': TheDayName,
                'TheDayOfWeek': TheDayOfWeek,
                'TheDayOfWeekInMonth': TheDayOfWeekInMonth,
                'TheDayOfYear': TheDayOfYear,
                'IsWeekend': IsWeekend,
                'TheWeek': TheWeek,
                'TheISOWeek': TheISOWeek,
                'TheFirstOfWeek': TheFirstOfWeek,
                'TheLastOfWeek': TheLastOfWeek,
                'TheWeekOfMonth': TheWeekOfMonth,
                'TheMonth': TheMonth,
                'TheMonthName': TheMonthName,
                'TheFirstOfMonth': TheFirstOfMonth,
                'TheLastOfMonth': TheLastOfMonth,
                'TheFirstOfNextMonth': TheFirstOfNextMonth,
                'TheLastOfNextMonth': TheLastOfNextMonth,
                'TheQuarter': TheQuarter,
                'TheFirstOfQuarter': TheFirstOfQuarter,
                'TheLastOfQuarter': TheLastOfQuarter,
                'TheYear': TheYear,
                'TheISOYear': TheISOYear,
                'TheFirstOfYear': TheFirstOfYear,
                'TheLastOfYear': TheLastOfYear,
                'IsLeapYear': IsLeapYear,
                'Has53Weeks': Has53Weeks,
                'Has53ISOWeeks': Has53ISOWeeks,
                'MMYYYY': MMYYYY,
                'Style101': Style101,
                'Style103': Style103,
                'Style112': Style112,
                'Style120': Style120
            }
        )
        current_date = current_date + td(days=1)
    return row_array
