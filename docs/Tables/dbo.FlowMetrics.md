# ![logo](../Images/table64.svg) dbo.FlowMetrics

## [](#Description) Description

> Flow Metrics by Date, Metric ID and Measure

## [](#Columns) Columns

|Key|Name|Data Type|Length|Precision|Scale|Not Null|Identity|Rule|Default|Computed|Persisted|Description|
|:---:|---|---|---|---|---|---|---|---|---|---|---|---|
|[![Primary Key PK__FlowMetr__C5ECA2C206677CB1](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__FlowMetr__C5ECA2C206677CB1](../Images/Cluster.svg)](#Indexes)|flow_id|nvarchar|255|0|0|True||||False|False|Flow ID|
|[![Primary Key PK__FlowMetr__C5ECA2C206677CB1](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__FlowMetr__C5ECA2C206677CB1](../Images/Cluster.svg)](#Indexes)|date|date|3|10|0|True||||False|False|Date of Metric Data|
|[![Primary Key PK__FlowMetr__C5ECA2C206677CB1](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__FlowMetr__C5ECA2C206677CB1](../Images/Cluster.svg)](#Indexes)|metric_id|nvarchar|50|0|0|True||||False|False|Metric ID |
||values|float|8|53|0|True||||False|False|Metric Value|
|[![Primary Key PK__FlowMetr__C5ECA2C206677CB1](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__FlowMetr__C5ECA2C206677CB1](../Images/Cluster.svg)](#Indexes)|measure|nvarchar|50|0|0|True||||False|False|Metric Measure|

## [](#Indexes) Indexes

|Key|Name|Columns|Unique|Type|Description|
|:---:|---|---|---|---|---|
|[![Primary Key PK__FlowMetr__C5ECA2C206677CB1](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__FlowMetr__C5ECA2C206677CB1](../Images/Cluster.svg)](#Indexes)|PK__FlowMetr__C5ECA2C206677CB1|flow_id, date, metric_id, measure|True|||

## [](#SqlScript) SQL Script

```SQL
CREATE TABLE dbo.FlowMetrics (
  flow_id nvarchar(255) NOT NULL,
  date date NOT NULL,
  metric_id nvarchar(50) NOT NULL,
  [values] float NOT NULL,
  measure nvarchar(50) NOT NULL,
  PRIMARY KEY CLUSTERED (flow_id, date, metric_id, measure)
)
ON [PRIMARY]
GO
```
