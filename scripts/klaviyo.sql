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
SET NOEXEC OFF
GO