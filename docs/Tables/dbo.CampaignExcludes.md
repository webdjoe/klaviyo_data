[Project](../../../../../startpage.md)>[Servers](../../../../Servers.md)>[192.168.1.202,14333](../../../192.168.1.202,14333.md)>[User databases](../../UserDatabases.md)>[klaviyo123](../klaviyo123.md)>[Tables](Tables.md)>dbo.CampaignExcludes


# ![logo](../../../../../Images/table64.svg) dbo.CampaignExcludes

## <a name="#Description"></a>Description
> Segments and Lists Excluded on Campaigns
## <a name="#Columns"></a>Columns
|Key|Name|Data Type|Length|Precision|Scale|Not Null|Identity|Rule|Default|Computed|Persisted|Description|
|:---:|---|---|---|---|---|---|---|---|---|---|---|---|
||campaign_id|nvarchar|255|0|0|True||||False|False|Campaign ID|
||object|nvarchar|255|0|0|True||||False|False|Object type|
||id|nvarchar|255|0|0|True||||False|False|Exclude list ID|
||name|nvarchar|255|0|0|False||||False|False|Exclude list/segment name|
||list_type|nvarchar|255|0|0|False||||False|False|List/segment type|
||folder|nvarchar|255|0|0|False||||False|False|List/segment folder|
||person_count|bigint|8|19|0|False||||False|False|People in list/segment|
||campaign_sent_at|datetime|8|23|3|False||||False|False|Campaign Sent Datetime|

## <a name="#SqlScript"></a>SQL Script
```SQL
CREATE TABLE dbo.CampaignExcludes (
  campaign_id nvarchar(255) NOT NULL,
  object nvarchar(255) NOT NULL,
  id nvarchar(255) NOT NULL,
  name nvarchar(255) NULL,
  list_type nvarchar(255) NULL,
  folder nvarchar(255) NULL,
  person_count bigint NULL,
  campaign_sent_at datetime NULL
)
ON [PRIMARY]
GO
```

||||
|---|---|---|
|Author: |Copyright © All Rights Reserved|Created: 17/08/2022|