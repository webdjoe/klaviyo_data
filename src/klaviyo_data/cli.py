""" Command Line Runner."""
import sys
import click
from klaviyo_data.klaviyo_app import KlaviyoData
from klaviyo_data.sql_app import DBBuilder


@click.command()
@click.option('-d', '--days', type=int, default=30,
              help='get days of history')
@click.option('-b', '--between', nargs=2, type=str,
              help='get between 2 dates - yyyy-MM-dd, ex -b\
                  2020-01-01 2020-01-02')
@click.option('--config', default='config.ini',
              help='Relative location of config.ini -\
                  defaults to config.ini in currect directory')
def cli_runner(days, between, config):
    """Run Klaviyo Data App CLI."""

    if between and len(between) == 2:
        start = between[0]
        end = between[1]
        kv_dict = {
            'klaviyo': {
                'start': start,
                'end': end
            }
        }
    elif days and isinstance(days, int):
        kv_dict = {
            'klaviyo': {
                'days': days,
            }
        }
    if kv_dict is not None:
        app = KlaviyoData(config, config_dict=kv_dict)
    else:
        app = KlaviyoData(config)

    app.pull_flows()
    app.flow_metrics()
    app.pull_campaigns()
    app.campaign_metrics()


@click.command()
@click.option('--server', type=str, default='localhost',
              help='Server to connect to')
@click.option('--port', type=str, default='1433',
              help='Port to connect to')
@click.option('--sa_user', type=str, default='sa',
              help='SQL Server admin user')
@click.option('--sa_pass', type=str,
              help='SQL Server admin password')
@click.option('--driver', type=str,
              default='ODBC Driver 17 for SQL Server',
              help='SQL Server driver')
@click.option('--db', type=str,
              default='klaviyo', help='SQL Server database')
@click.option('--tables-only/--db-and-tables', default=False,
              help='Only build tables')
def klaviyo_db_builder(server, port, sa_user, sa_pass,
                       driver, db, tables_only):
    """Build Klaviyo Database."""
    click.echo(f"tables_only: {tables_only}")
    click.echo(f"server: {server}")
    if tables_only:
        click.echo(f"Building tables only in {db}")
        dbbuilder = DBBuilder(server, port, sa_user, sa_pass,
                              driver=driver)
        db_exists = dbbuilder.get_engine(db)
        if db_exists is False:
            click.echo("Cannot use --tables-only switch with a database\
                that does not exist")
            return
        build = dbbuilder.build_tables(db)
        if build is True:
            click.echo("Tables built successfully")
            return
        else:
            click.echo("Unable to build tables")
            return

    dbbuilder = DBBuilder(server, port, sa_user, sa_pass, driver=driver)
    connect = dbbuilder.get_engine()
    if connect is False or dbbuilder.engine is None:
        click.echo("Unable to connect to SQL Server")
        return

    build = dbbuilder.build_database(db)
    if build is False:
        click.echo("Error building database")
        return
    build_tables = dbbuilder.build_tables(db)
    if build_tables is True:
        click.echo(f"Successfully built {db} database and Klaviyo tables")
        return
    click.echo("Error building tables")
    return
