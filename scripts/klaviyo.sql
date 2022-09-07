USE master
GO

IF DB_NAME() <> N'master' SET NOEXEC ON

CREATE DATABASE $(DBName)
GO

ALTER DATABASE $(DBName)
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
GO

ALTER DATABASE $(DBName)
  SET DISABLE_BROKER
GO



ALTER DATABASE $(DBName)
  SET QUERY_STORE = OFF
GO

CREATE LOGIN [$(DBUser)] WITH PASSWORD=N'$(DBPassword)'

USE $(DBName)
GO

IF DB_NAME() <> N'$(DBName)' SET NOEXEC ON
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = N'$(DBUser)')
BEGIN
	CREATE USER [$(DBUser)] FOR LOGIN [$(DBUser)]
	EXEC sp_addrolemember N'db_owner', N'$(DBUser)'
END;
GO


SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE $(Schema).Metrics (
  [id] nvarchar(255) NOT NULL,
  [name] nvarchar(255) NULL,
  CONSTRAINT PK_metrics_id PRIMARY KEY CLUSTERED (id)
)
ON [PRIMARY]
GO

CREATE TABLE $(Schema).FlowMetrics (
  [flow_id] nvarchar(255) NOT NULL,
  [date] date NOT NULL,
  [metric_id] varchar(50) NOT NULL,
  [values] float NOT NULL,
  [measure] nvarchar(50) NOT NULL,
  CONSTRAINT PK_flow_metrics PRIMARY KEY CLUSTERED (flow_id, date, metric_id, measure)
)
ON [PRIMARY]
GO

CREATE TABLE $(Schema).FlowList (
  [id] nvarchar(255) NOT NULL,
  [name] nvarchar(255) NOT NULL,
  [object] nvarchar(255) NULL,
  [status] nvarchar(255) NULL,
  [archived] bit NULL,
  [created] datetime NOT NULL,
  [updated] datetime NULL,
  CONSTRAINT PK_flow_list_id PRIMARY KEY CLUSTERED (id)
)
ON [PRIMARY]
GO

CREATE TABLE $(Schema).CampaignMetrics (
  [campaign_id] nvarchar(255) NOT NULL,
  [date] date NOT NULL,
  [metric_id] varchar(50) NOT NULL,
  [values] float NULL,
  [measure] nvarchar(50) NOT NULL,
  CONSTRAINT PK_campaign_metrics PRIMARY KEY CLUSTERED (campaign_id, date, metric_id, measure)
)
ON [PRIMARY]
GO

CREATE TABLE $(Schema).CampaignList (
  [id] nvarchar(255) NOT NULL,
  [name] nvarchar(255) NULL,
  [subject] nvarchar(255) NULL,
  [status] nvarchar(255) NULL,
  [status_label] nvarchar(255) NULL,
  [status_id] int NULL,
  [num_recipients] bigint NULL,
  [is_segmented] smallint NULL,
  [message_type] nvarchar(255) NULL,
  [template_id] nvarchar(255) NULL,
  [sent_at] datetime NULL,
  [send_time] datetime NULL,
  CONSTRAINT PK_campaign_list_id PRIMARY KEY CLUSTERED (id)
)
ON [PRIMARY]
GO

CREATE TABLE $(Schema).CampaignIncludes (
  [campaign_id] nvarchar(255) NOT NULL,
  [object] nvarchar(255) NOT NULL,
  [id] nvarchar(255) NOT NULL,
  [name] nvarchar(255) NULL,
  [list_type] nvarchar(255) NULL,
  [folder] nvarchar(255) NULL,
  [person_count] bigint NULL,
  [campaign_sent_at] datetime NULL
)
ON [PRIMARY]
GO

CREATE TABLE $(Schema).CampaignExcludes (
  [campaign_id] nvarchar(255) NOT NULL,
  [object] nvarchar(255) NOT NULL,
  [id] nvarchar(255) NOT NULL,
  [name] nvarchar(255) NULL,
  [list_type] nvarchar(255) NULL,
  [folder] nvarchar(255) NULL,
  [person_count] bigint NULL,
  [campaign_sent_at] datetime NULL
)
ON [PRIMARY]
GO
DECLARE @StartDate  date = '$(StartDate)';

DECLARE @CutoffDate date = DATEADD(DAY, -1, DATEADD(YEAR, 30, @StartDate));

;WITH seq(n) AS
(
  SELECT 0 UNION ALL SELECT n + 1 FROM seq
  WHERE n < DATEDIFF(DAY, @StartDate, @CutoffDate)
),
d(d) AS
(
  SELECT DATEADD(DAY, n, @StartDate) FROM seq
),
src AS
(
  SELECT
    TheDate         = CONVERT(date, d),
    TheDay          = DATEPART(DAY,       d),
    TheDayName      = DATENAME(WEEKDAY,   d),
    TheWeek         = DATEPART(WEEK,      d),
    TheISOWeek      = DATEPART(ISO_WEEK,  d),
    TheDayOfWeek    = DATEPART(WEEKDAY,   d),
    TheMonth        = DATEPART(MONTH,     d),
    TheMonthName    = DATENAME(MONTH,     d),
    TheQuarter      = DATEPART(Quarter,   d),
    TheYear         = DATEPART(YEAR,      d),
    TheFirstOfMonth = DATEFROMPARTS(YEAR(d), MONTH(d), 1),
    TheLastOfYear   = DATEFROMPARTS(YEAR(d), 12, 31),
    TheDayOfYear    = DATEPART(DAYOFYEAR, d)
  FROM d
),
dim AS
(
  SELECT
    TheDate,
    TheDay,
    TheDaySuffix        = CONVERT(char(2), IIF(TheDay / 10 = 1, 'th', CASE RIGHT(TheDay, 1)
                                                                          WHEN '1' THEN 'st'
                                                                          WHEN '2' THEN 'nd'
                                                                          WHEN '3' THEN 'rd'
                                                                          ELSE 'th' END)),
    TheDayName,
    TheDayOfWeek,
    TheDayOfWeekInMonth = CONVERT(tinyint, ROW_NUMBER() OVER
                            (PARTITION BY TheFirstOfMonth, TheDayOfWeek ORDER BY TheDate)),
    TheDayOfYear,
    IsWeekend           = IIF(TheDayOfWeek IN (CASE @@DATEFIRST WHEN 1 THEN 6 WHEN 7 THEN 1 END, 7), 1, 0),
    TheWeek,
    TheISOweek,
    TheFirstOfWeek      = DATEADD(DAY, 1 - TheDayOfWeek, TheDate),
    TheLastOfWeek       = DATEADD(DAY, 6, DATEADD(DAY, 1 - TheDayOfWeek, TheDate)),
    TheWeekOfMonth      = CONVERT(tinyint, DENSE_RANK() OVER
                            (PARTITION BY TheYear, TheMonth ORDER BY TheWeek)),
    TheMonth,
    TheMonthName,
    TheFirstOfMonth,
    TheLastOfMonth      = MAX(TheDate) OVER (PARTITION BY TheYear, TheMonth),
    TheFirstOfNextMonth = DATEADD(MONTH, 1, TheFirstOfMonth),
    TheLastOfNextMonth  = DATEADD(DAY, -1, DATEADD(MONTH, 2, TheFirstOfMonth)),
    TheQuarter,
    TheFirstOfQuarter   = MIN(TheDate) OVER (PARTITION BY TheYear, TheQuarter),
    TheLastOfQuarter    = MAX(TheDate) OVER (PARTITION BY TheYear, TheQuarter),
    TheYear,
    TheISOYear          = TheYear - CASE WHEN TheMonth = 1 AND TheISOWeek > 51 THEN 1
                            WHEN TheMonth = 12 AND TheISOWeek = 1  THEN -1 ELSE 0 END,
    TheFirstOfYear      = DATEFROMPARTS(TheYear, 1,  1),
    TheLastOfYear,
    IsLeapYear          = CONVERT(bit, IIF((TheYear % 400 = 0)
                                               OR (TheYear % 4 = 0 AND TheYear % 100 <> 0), 1, 0)),
    Has53Weeks          = IIF(DATEPART(WEEK, TheLastOfYear) = 53, 1, 0),
    Has53ISOWeeks       = IIF(DATEPART(ISO_WEEK, TheLastOfYear) = 53, 1, 0),
    MMYYYY              = CONVERT(char(2), CONVERT(char(8), TheDate, 101))
                          + CONVERT(char(4), TheYear),
    Style101            = CONVERT(char(10), TheDate, 101),
    Style103            = CONVERT(char(10), TheDate, 103),
    Style112            = CONVERT(char(8),  TheDate, 112),
    Style120            = CONVERT(char(10), TheDate, 120)
  FROM src
)
SELECT * INTO $(SchemaName).DateDimension FROM dim
  ORDER BY TheDate
  OPTION (MAXRECURSION 0);
GO

CREATE UNIQUE CLUSTERED INDEX PK_DateDimension ON $(SchemaName).DateDimension(TheDate);
GO
SET NOEXEC OFF
GO