# ![logo](../Images/table64.svg) dbo.CampaignExcludes

## [](#Description) Description

> Segments and Lists Excluded on Campaigns

## [](#Columns) Columns

|Key|Name|Data Type|Length|Precision|Scale|Not Null|Description|
|:---:|---|---|---|---|---|---|---|
||campaign_id|nvarchar|255|0|0|True|Campaign ID|
||object|nvarchar|255|0|0|True|Object type|
||id|nvarchar|255|0|0|True|Exclude list ID|
||name|nvarchar|255|0|0|False|Exclude list/segment name|
||list_type|nvarchar|255|0|0|False|List/segment type|
||folder|nvarchar|255|0|0|False|List/segment folder|
||person_count|bigint|8|19|0|False|People in list/segment|
||campaign_sent_at|datetime|8|23|3|False|Campaign Sent Datetime|

## [](#SqlScript) SQL script

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
