# ![logo](../Images/table64.svg) dbo.FlowList

## [](#Description) Description

> List of All Flows and Status

## [](#Columns) Columns

|Key|Name|Data Type|Length|Precision|Scale|Not Null|Identity|Rule|Default|Computed|Persisted|Description|
|:---:|---|---|---|---|---|---|---|---|---|---|---|---|
|[![Primary Key PK__FlowList__3213E83F6DD55AFB](../../../../../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__FlowList__3213E83F6DD55AFB](../../../../../Images/Cluster.svg)](#Indexes)|id|nvarchar|255|0|0|True||||False|False|Flow ID|
||name|nvarchar|255|0|0|True||||False|False|Flow Name|
||object|nvarchar|255|0|0|False||||False|False|Object Type|
||status|nvarchar|255|0|0|False||||False|False|Flow Status|
||archived|bit|1|1|0|False||||False|False|Flow Archived?|
||created|datetime|8|23|3|True||||False|False|Date Flow Created|
||updated|datetime|8|23|3|False||||False|False|Date Flow Updated|

## [](#Indexes) Indexes

|Key|Name|Columns|Unique|Type|Description|
|:---:|---|---|---|---|---|
|[![Primary Key PK__FlowList__3213E83F6DD55AFB](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__FlowList__3213E83F6DD55AFB](../Images/Cluster.svg)](#Indexes)|PK__FlowList__3213E83F6DD55AFB|id|True|||

## [](#SqlScript) SQL Script

```SQL
CREATE TABLE dbo.FlowList (
  id nvarchar(255) NOT NULL,
  name nvarchar(255) NOT NULL,
  object nvarchar(255) NULL,
  status nvarchar(255) NULL,
  archived bit NULL,
  created datetime NOT NULL,
  updated datetime NULL,
  PRIMARY KEY CLUSTERED (id)
)
ON [PRIMARY]
GO
```

||||
|---|---|---|
|Author: |Copyright © All Rights Reserved|Created: 17/08/2022|