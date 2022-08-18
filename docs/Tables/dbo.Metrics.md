# ![logo](../Images/table64.svg) dbo.Metrics

## [](Description) Description

> All Metric Names and Metric ID's

## [](Columns) Columns

|Key|Name|Data Type|Length|Precision|Scale|Not Null|Description|
|:---:|---|---|---|---|---|---|---|---|---|---|---|---|
|[![Primary Key PK__Metrics__3213E83FF2515B3E](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Metrics__3213E83FF2515B3E](../Images/Cluster.svg)](#Indexes)|id|nvarchar|255|0|0|True|Metric ID|
||name|nvarchar|255|0|0|False|Metric Name|

## [](Indexes) Indexes

|Key|Name|Columns|Unique|Type|Description|
|:---:|---|---|---|---|---|
|[![Primary Key PK__Metrics__3213E83FF2515B3E](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Metrics__3213E83FF2515B3E](../Images/Cluster.svg)](#Indexes)|PK__Metrics__3213E83FF2515B3E|id|True|||

## [](SqlScript) SQL Script

```SQL
CREATE TABLE dbo.Metrics (
  id nvarchar(255) NOT NULL,
  name nvarchar(255) NULL,
  PRIMARY KEY CLUSTERED (id)
)
ON [PRIMARY]
GO
```
