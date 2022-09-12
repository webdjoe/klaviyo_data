# ![logo](../Images/table64.svg) dbo.Templates

## [](#Description) Description

> Store campaign templates, html and optionally images. Adding a filestream to store images is recommended.

## [](#Columns) Columns

|Key|Name|Data Type|Length|Precision|Scale|Not Null|Identity|Rule|Default|Computed|Persisted|Description|
|:---:|---|---|---|---|---|---|---|---|---|---|---|---|
|[![Primary Key PK__Template__3213E83FA2F59BBA](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Template__3213E83FA2F59BBA](../Images/Cluster.svg)](#Indexes)|id|nvarchar|20|0|0|True||||False|False|Template ID|
||file_id|UNIQUEIDENTIFIER|8|53|0|True|||NEWID()|True|False|GUID for filestream|
||updated|datetime|8|23|3|True||||False|False|Templates last updated date|
||created|datetime|8|23|3|True||||False|False|Templates creation date|
||name|nvarchar|255|0|0|True||||False|False|Template name|
||image_path|nvarchar|255|0|0|False||||False|False|Path where generated template image is stored|
||html|nvarchar|max|0|0|False||||False|False|HTML of template|
||image_blob|varbinary|max|0|0|False||||False|False|Image stored in binary|

## [](#Indexes) Indexes

|Key|Name|Columns|Unique|Type|Description|
|:---:|---|---|---|---|---|
|[![Primary Key PK__Template__3213E83FA2F59BBA](../Images/primarykey.svg)](#Indexes)[![Cluster Key PK__Template__3213E83FA2F59BBA](../Images/Cluster.svg)](#Indexes)|PK__Template__3213E83FA2F59BBA|id|True|||

## [](#SqlScript) SQL Script

```SQL
CREATE TABLE [dbo].[Templates](
	[file_id] [uniqueidentifier] ROWGUIDCOL DEFAULT (newid()) NOT NULL,
	[id] [nvarchar](20) PRIMARY KEY NOT NULL,
	[updated] [datetime] NOT NULL,
	[created] [datetime] NOT NULL,
	[name] [nvarchar](255) NOT NULL,
	[image_path] [nvarchar](255) NULL,
	[html] [nvarchar](max) NOT NULL,
	[image_blob] [varbinary](max) NULL
)
GO
```
