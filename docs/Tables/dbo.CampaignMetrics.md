# ![logo](../Images/table64.svg) dbo.CampaignMetrics

## [](#Description) Description

> Campaign Metrics by Date, Metric ID & Measure

## [](#Columns) Columns

|Key|Name|Data Type|Length|Precision|Scale|Not Null|Description|
|:---:|---|---|---|---|---|---|---|---|---|---|---|---|
|[![Primary Key PK__Campaign__4869F27D5F286B07](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Campaign__4869F27D5F286B07](../Images/Cluster.svg)](#Indexes)|campaign_id|nvarchar|255|0|0|True|Campaign ID|
|[![Primary Key PK__Campaign__4869F27D5F286B07](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Campaign__4869F27D5F286B07](../Images/Cluster.svg)](#Indexes)|date|date|3|10|0|True|Campaign Metric Date|
|[![Primary Key PK__Campaign__4869F27D5F286B07](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Campaign__4869F27D5F286B07](../Images/Cluster.svg)](#Indexes)|metric_id|nvarchar|50|0|0|True|Metric ID|
||values|float|8|53|0|False|Metric value|
|[![Primary Key PK__Campaign__4869F27D5F286B07](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Campaign__4869F27D5F286B07](../Images/Cluster.svg)](#Indexes)|measure|nvarchar|50|0|0|True|Metric Measure|

## [](#Indexes) Indexes

|Key|Name|Columns|Unique|Type|Description|
|:---:|---|---|---|---|---|
|[![Primary Key PK__Campaign__4869F27D5F286B07](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Campaign__4869F27D5F286B07](../Images/Cluster.svg)](#Indexes)|PK__Campaign__4869F27D5F286B07|campaign_id, date, metric_id, measure|True|||

## [](#SqlScript) SQL Script

```SQL
CREATE TABLE dbo.CampaignMetrics (
  campaign_id nvarchar(255) NOT NULL,
  date date NOT NULL,
  metric_id nvarchar(50) NOT NULL,
  [values] float NULL,
  measure nvarchar(50) NOT NULL,
  PRIMARY KEY CLUSTERED (campaign_id, date, metric_id, measure)
)
ON [PRIMARY]
GO
```
