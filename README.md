# Klaviyo Data

Pull Klaviyo Email Marketing KPI's for Flows and Campaign. The purpose of this library is to pull Klaviyo's campaign and flow performance into an SQL Server database. This is not meant as a replacement for Klaviyo's python SDK. Instead, this is a supplemental library to be able to programmatically integrate flow and campaign performance analysis into dashboards and reports.

Due the structure of Klaviyo's API, there is not simple way to pull this data in a single request. This library addresses that shortcoming by pulling all the necessary data into SQL Server tables that can be queried and integrated with other dashboards and platforms with ease.

The application is based on a specific SQL Server table structure that is outlined in the [Docs](#database-structure). The database can be set up via a SQLCMD based SQL script, command line or programmatically through helper functions.

## Table of Contents

- [Klaviyo Data](#klaviyo-data)
  - [Table of Contents](#table-of-contents)
  - [Metrics Tracked](#metrics-tracked)
  - [Installation](#installation)
    - [Installing ODBC Driver](#installing-odbc-driver)
  - [Configuring the Script](#configuring-the-script)
    - [config.ini](#configini)
    - [Config Dictionary](#config-dictionary)
  - [Running the Application](#running-the-application)
    - [Creating the Database](#creating-the-database)
      - [Creating Database Structure through Python Module](#creating-database-structure-through-python-module)
      - [Create Database via Command Line](#create-database-via-command-line)
    - [Running via Python Module](#running-via-python-module)
    - [Running via Command Line](#running-via-command-line)
  - [Database Structure](#database-structure)

## Metrics Tracked

Currently the following metrics are tracked:

- **Placed Order** J8wEZQ - Count & Value
- **Received email** K8EZcU - Count
- **Clicked email** Kdifyi - Count
- **Marked as Spam** KHctvU - Count
- **Ordered Product** LxXB8W - Count & Value
- **Unsubscribed** MvCm2p - Count
- **Opened Email** My7Vk2 - Count

## Installation

### Installing ODBC Driver

In order for `klaviyo_data` to function, the SQL Server ODBC driver is needed. This can be installed from the [SQL Server ODBC Driver](https://www.microsoft.com/en-us/download/details.aspx?id=44567)

Windows is a simple executable installation from the link above.

On Linux, `msodbc18` needs to be installed first, then `unixodbc` headers. This is an example on Ubuntu (only compatible with 18.04, 20.04 & 21.04):

```shell script
$ sudo su
# Install curl and gnupg2 if needed
$ apt update && apt install curl gnupg2 lsb_release
# Add Microsoft's Repository
$ curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
$ curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
# Install ODBC Driver and unixodbc-dev headers
$ apt update && apt install -y msodbcsql18 unixodbc-dev
```

Once the ODBC driver is installed, the library can be installed via pip:

```bash
pip install klaviyo_data
```

## Configuring the Script

The script can be configured through an `ini`-based file or a dictionary passed to the main `KlaviyoData` class during instantiation.

### config.ini

The `config.ini` template can be found [here](config.ini)

```ini
[klaviyo]
# Klaviyo Database Name, Schema, User & Password
database = klaviyo
schema = dbo
db_user = sa
db_pass = TheStrongestpassword1!
windows_auth = False
# Driver for pyodbc to use (The latest driver is 18)
driver = ODBC Driver 17 for SQL Server
# Database server & port - localhost if run inside docker container
server = localhost
port = 1433

# Pull last days of data
days = 30
# Pull data between start and end dates
# start = 20210101
# end = 20211231

# Klaviyo Public and Private Key
public_key = ****KLAVIYO PUBLIC KEY****
private_key = ****KLAVIYO PRIVATE KEY****
```

### Config Dictionary 

Configuration can also be passed during instantiation to `KlaviyoData`  as a dictionary of the following format:

```python
config_dict = {
    'klaviyo': {
        'private_key': '****KLAVIYO PRIVATE KEY****',
        'public_key': '****KLAVIYO PUBLIC KEY****',
        'items_per_page': 250,
        'days': 30,
        'db': 'klaviyo',
        'schema': 'dbo',
        'db_user': 'kv_user',
        'db_pass': 'StrongPassword1!',
        'windows_auth': False,
        'server': 'localhost',
        'port': 1433,
        'driver': 'ODBC Driver 17 for SQL Server',
    }
}
```

## Running the Application

The `klaviyo_data` application can be run as a python module or via command line application.


### Creating the Database

Before the application can be run, the database needs to be created, along with the tables and the optionally but recommended database user. This can be done through a command line script or programmatically.

#### Creating Database Structure through Python Module

There is a helper class that can be used to create the database, user and tables. The tables can be created in a separate database or built in an already existing database. The class must be instantiated with the administrative credentials.

```python
from klaviyo_data.sql_app import DBBuilder

builder = DBBuilder(server='localhost',
                    port=1433,
                    sa_user='sa',
                    sa_pass='TheStrongestpassword1!',
                    windows_auth=False,
                    driver='ODBC Driver 17 for SQL Server')

# Optionally, a separate database can be created to hold the tables
builder.build_database('klaviyo')

# Optionally but recommended, a separate user can be created with only access to the database
builder.create_user('klaviyo_user', 'StrongPassword1!')

# Create the table structure
builder.build_tables('klaviyo')
```

#### Create Database via Command Line

`klaviyo_data` includes a command line application that can automatically build the database and/or structure. The only shortcoming of this method is that it does not create a database user but this can be done manually via SQLCMD. The associated command is `build_klaviyo` with the following options.

```shell script
$ build_klaviyo --help
Usage: build_klaviyo [OPTIONS]

  Build Klaviyo Database.

Options:
  --server TEXT                   Server to connect to
  --port TEXT                     Port to connect to
  --sa_user TEXT                  SQL Server admin user
  --sa_pass TEXT                  SQL Server admin password
  --driver TEXT                   SQL Server driver
  --db TEXT                       SQL Server database
  --tables-only / --db-and-tables
                                  Only build tables
  --help                          Show this message and exit.

# Build klaviyo database and tables
$ build_klaviyo --server localhost --port 1433 \
    --sa_user sa --sa_pass TheStrongestpassword1! \
    --driver ODBC Driver 17 for SQL Server \
    --db klaviyo \

# Use the --only-tables flag to skip database creation and add tables to existing database
$ build_klaviyo --server localhost --port 1433 \
    --sa_user sa --sa_pass TheStrongestpassword1! \
    --driver ODBC Driver 17 for SQL Server \
    --db ExistingDB --tables-only
```

There is also an SQLCMD based [klaviyo.sql](scripts/klaviyo.sql) script in the [scripts](scripts/) folder that can be used to build the database, user and tables. The following variables must be set when executing the script:

- `DBName` - Database to create
- `Schema` - Schema to use
- `DBUser` - Database user to create
- `DBPass` - Password for the database user

```shell
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "SA_User_Password" -d master \
-v DBName="klaviyo" \
-v Schema="dbo" -v DBUser="kv_user" \
-v DBPassword="Strongerpassword1!" \
-i scripts/klaviyo.sql
```

### Running via Python Module

When running via python module, the database, username and password passed in the configuration must be already created on the SQL Server instance. There is no need to pass the server administrator user and pass if you plan to set up a separate database user.

```python
from klaviyo_data.klaviyo_app import KlaviyoData

# Config.ini located in the current working directory
app = KlaviyoData('config.ini')

# Instantiating with a configuration dictionary
config = {
    'klaviyo': {
        'private_key': '****KLAVIYO PRIVATE KEY****',
        'public_key': '****KLAVIYO PUBLIC KEY****',
        'items_per_page': 250,
        'days': 30,
        'db': 'klaviyo',
        'schema': 'dbo',
        'db_user': 'kv_user',
        'db_pass': 'StrongPassword1!',
        'windows_auth': False,
        'server': 'localhost',
        'port': 1433,
        'driver': 'ODBC Driver 17 for SQL Server',
    }
}

app = KlaviyoData(config_dict=config)

# Returns metric names and ids in addition to loading into Metrics table
metrics = app.pull_metrics()

# Pulls all campaign information and updates/inserts into CampaignList, CampaignIncludes & CampaignExcludes tables
app.pull_campaigns()


# Pulls all campaign data according to the configured dates/range and updates/inserts in CampaginMetrics table
app.campaign_metrics()

# Retreives all flow information and updates/inserts in FlowList table
app.pull_flows()

# Retrieves all flow performance based on date/range and updates/inserts in FlowMetrics table
app.flow_metrics()
```

### Running via Command Line

There is a command line application that allows the application to be run without having to create a python script.

```shell
$ klaviyo_cli --help
Usage: klaviyo_cli [OPTIONS]

  Run Klaviyo Data App CLI.

Options:
  -d, --days INTEGER     get days of history
  -b, --between TEXT...  get between 2 dates - yyyy-MM-dd, ex -b
                         2020-01-01 2020-01-02
  --config TEXT          Relative location of config.ini -
                         defaults to config.ini in currect directory
  --help                 Show this message and exit.

# Get 30 days of data with config.ini in current directory
$ klaviyo_cli -d 30 --config config.ini

```

## Database Structure

The database is structured with the following tables:

[](Tables) **Tables** _`7`_

|Name|Description|
|---|---|
|[dbo.Metrics](docs/Tables/dbo.Metrics.md)|All Metric Names and Metric ID's|
|[dbo.FlowList](docs/Tables/dbo.FlowList.md)|List of All Flows and Status|
|[dbo.FlowMetrics](docs/Tables/dbo.FlowMetrics.md)|Flow Metrics by Date, Metric ID and Measure|
|[dbo.CampaignList](docs/Tables/dbo.CampaignList.md)|All Campaigns|
|[dbo.CampaignMetrics](docs/Tables/dbo.CampaignMetrics.md)|Campaign Metrics by Date, Metric ID & Measure|
|[dbo.CampaignExcludes](docs/Tables/dbo.CampaignExcludes.md)|Segments and Lists Excluded on Campaigns|
|[dbo.CampaignIncludes](docs/Tables/dbo.CampaignIncludes.md)|Segments and Lists Included on Campaigns|
