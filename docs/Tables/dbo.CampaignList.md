[Project](../../../../../startpage.md)>[Servers](../../../../Servers.md)>[192.168.1.202,14333](../../../192.168.1.202,14333.md)>[User databases](../../UserDatabases.md)>[klaviyo123](../klaviyo123.md)>[Tables](Tables.md)>dbo.CampaignList


# ![logo](../../../../../Images/table64.svg) dbo.CampaignList

## <a name="#Description"></a>Description
> All Campaigns
## <a name="#Columns"></a>Columns
|Key|Name|Data Type|Length|Precision|Scale|Not Null|Identity|Rule|Default|Computed|Persisted|Description|
|:---:|---|---|---|---|---|---|---|---|---|---|---|---|
|[![Primary Key PK__Campaign__3213E83F92524746](../../../../../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Campaign__3213E83F92524746](../../../../../Images/Cluster.svg)](#Indexes)|id|nvarchar|255|0|0|True||||False|False|Campaign ID|
||name|nvarchar|255|0|0|False||||False|False|Campaign Name|
||subject|nvarchar|255|0|0|False||||False|False|Campaign Subject|
||status|nvarchar|255|0|0|False||||False|False|Campaign Status|
||status_label|nvarchar|255|0|0|False||||False|False|Campaign Status Label|
||status_id|int|4|10|0|False||||False|False|Campaign Status ID|
||num_recipients|bigint|8|19|0|False||||False|False|Total Number of Recipients|
||is_segmented|smallint|2|5|0|False||||False|False|Is Campaign Segmented?|
||message_type|nvarchar|255|0|0|False||||False|False|Message Type|
||template_id|nvarchar|255|0|0|False||||False|False|Template ID|
||sent_at|datetime|8|23|3|False||||False|False|Datetime Sent at|
||send_time|datetime|8|23|3|False||||False|False|Send Datetime|

## <a name="#Indexes"></a>Indexes
|Key|Name|Columns|Unique|Type|Description|
|:---:|---|---|---|---|---|
|[![Primary Key PK__Campaign__3213E83F92524746](../../../../../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Campaign__3213E83F92524746](../../../../../Images/Cluster.svg)](#Indexes)|PK__Campaign__3213E83F92524746|id|True|||

## <a name="#SqlScript"></a>SQL Script
```SQL
CREATE TABLE dbo.CampaignList (
  id nvarchar(255) NOT NULL,
  name nvarchar(255) NULL,
  subject nvarchar(255) NULL,
  status nvarchar(255) NULL,
  status_label nvarchar(255) NULL,
  status_id int NULL,
  num_recipients bigint NULL,
  is_segmented smallint NULL,
  message_type nvarchar(255) NULL,
  template_id nvarchar(255) NULL,
  sent_at datetime NULL,
  send_time datetime NULL,
  PRIMARY KEY CLUSTERED (id)
)
ON [PRIMARY]
GO
```

||||
|---|---|---|
|Author: |Copyright © All Rights Reserved|Created: 17/08/2022|