import logging
from typing import Optional
import pathlib
from datetime import datetime as dt
import requests
from configparser import SectionProxy
from sqlalchemy.types import TypeEngine
from sqlalchemy.orm import sessionmaker
import klaviyo_sdk
from sqlalchemy import MetaData, Table, select, update, delete

logger = logging.getLogger()


class TemplateFactory:
    def __init__(self, kv_conf: SectionProxy,
                 engine: TypeEngine) -> None:
        self.built_templates: list = []
        self.engine = engine
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.meta = MetaData()
        self.temp_table = Table('Templates', self.meta,
                                autoload_with=self.engine)
        self.kv_conf = kv_conf
        self.priv_key: str = kv_conf.get('private_key')
        self.client = klaviyo_sdk.Client(self.priv_key)
        self.existing_html: list = self.get_existing_html()
        self.template_id_rows: list = []
        self.get_built_templates()

    def get_built_templates(self) -> None:
        bad_templates = []
        stmt = self.session.execute("SELECT [id], [updated], [image_path] \
                            FROM [dbo].[Templates] WHERE \
                            [image_path] is not null or \
                            [image_blob] is not null")
        self.built_templates = []
        for row in stmt:
            row_dict = row._asdict()
            if row_dict.get('image_path') is not None and \
                    not pathlib.Path(row_dict.get('image_path')).exists():
                bad_templates.append(row_dict.get('id'))
            else:
                self.built_templates.append(row_dict)
        self.session.close()
        if len(bad_templates) > 0:
            self.clean_template_table(bad_templates)

    def clean_template_table(self, bad_templates):
        """Remove templates with an invalid file path."""
        with self.session.begin():
            for template_id in bad_templates:
                self.session.execute(
                    update(self.temp_table)
                    .where(self.temp_table.c.id == template_id)
                    .values({'image_path': None}))
                self.session.commit()
        self.session.close()

    def get_existing_html(self) -> list:
        """Get templates with existing html in DB."""
        stmt = self.session.execute("SELECT [id], [updated] \
                FROM [dbo].[Templates] WHERE \
                    [html] is not null")
        existing_html = []
        for row in stmt:
            existing_html.append(row._asdict())
        self.session.close()
        return existing_html

    def pull_all_templates(self) -> bool:
        page: int = 0
        end: int = 1
        total: int = 2
        while end < total:
            templates = self.client.Templates.get_templates(
                page=page, count=100)
            page = int(templates.get('page', 0)) + 1
            end = templates.get('end')
            total = templates.get('total')
            data = templates.get('data', [])
            if len(data) == 0:
                break
            self.insert_templates(data)
        return True

    def insert_templates(self, data: list) -> bool:
        """Upload template info to SQL Server."""
        column_names = ['id', 'name', 'updated', 'created', 'html']
        tbl_list = []
        bad_templates = []
        for row in data:
            exists = False
            for exist_html in self.existing_html:
                if exist_html.get('id') == row.get('id'):
                    if dt.strftime(exist_html['updated'],
                                   "%Y-%m-%d %H:%M:%S") == row['updated']:
                        exists = True
                        break
                    else:
                        bad_templates.append(exist_html.get('id'))
                        exists = False
                        break
            if not exists:
                tbl_data = {x: row[x] for x in column_names}
                tbl_list.append(tbl_data)
        if len(bad_templates) > 0:
            self.remove_old_templates(bad_templates)
        if len(tbl_list) > 0:
            with self.session.begin():
                self.session.execute(self.temp_table.insert(), tbl_list)
                self.session.commit()
            self.session.close()
            self.get_existing_html()
        self.session.close()
        return True

    def remove_old_templates(self, id_list) -> None:
        """Delete old templates that have been updated."""
        with self.session.begin():
            for id in id_list:
                self.session.execute(delete(self.temp_table)
                                     .where(self.temp_table.c.id == id))
                self.session.commit()
        self.session.close()

    def get_template_image(self, template_id: str,
                           to_sql: bool = False,
                           to_return: bool = False,
                           to_file: bool = False,
                           file_path: Optional[str] = None,
                           api_options: Optional[dict] = None
                           ) -> Optional[bytes]:
        """Get template image from Klaviyo."""
        if to_file is False and to_sql is False:
            logger.debug("Specify a destination for the image.")
            return None
        if self.kv_conf.get('pspdfkit_api') is None:
            logger.debug("Need to specify psdpdfkit_api in config")
            return None
        temp_ids = [x.get('id') for x in self.existing_html]
        if template_id not in temp_ids:
            self.pull_all_templates()
            if template_id not in temp_ids:
                logger.debug(f'Template {template_id} not found.')
                return None
        result = self.session.execute(
            select(self.temp_table.c.html)
            .where(self.temp_table.c.id == template_id)).scalar()
        if result is None:
            logger.debug(f"Html for {template_id} not found in DB.")
        html = result
        self.session.close()
        logger.debug(f'Getting image for {template_id}')
        image = self.get_image_api(html, api_options)
        if image is None:
            return None
        if to_file is True:
            logger.debug(f'Writing image file for {template_id}')
            self.write_image_file(image, template_id, file_path)
        if to_sql is True:
            self.insert_image_sql(template_id, image)
        if to_return is True:
            return image
        return None

    def get_image_api(self, html: str,
                      api_options: Optional[dict] = None) -> Optional[bytes]:
        """Get image from pspdfkit API."""
        auth = requests.auth.HTTPBasicAuth(
            self.kv_conf.get('htmlcsstoimage_user'),
            self.kv_conf.get('htmlcsstoimage_api'))
        options = {
                'full_screen': 'true',
                'html': html
            }
        if api_options is not None:
            options.update(api_options)
        response = requests.post(
            'https://hcti.io/v1/image',
            auth=auth,
            data=options,
        )
        if response.status_code != 200:
            logger.debug(f"Status code {response.status_code} with \
                error {response.text}")
        resp_json = response.json()
        if resp_json is None or resp_json.get('url') is None:
            logger.debug('No image found for template')
            return None
        logger.debug(f'Getting image from {resp_json.get("url")}')
        image = requests.get(resp_json.get('url') + ".jpg")
        image.raise_for_status()
        return image.content

    def write_image_file(self, image: bytes, template_id: str,
                         file_path: str = None) -> None:
        """Write image bytes to file"""
        self.session.close()
        if file_path is None:
            if self.kv_conf.get('image_path') is not None:
                file_path = self.kv_conf.get('image_path')
        if file_path is not None:
            path_obj = pathlib.PurePath(file_path)
            if path_obj.is_absolute() is False:
                cwd = pathlib.Path.cwd()
                path_obj = pathlib.Path(cwd, file_path)
            else:
                path_obj = pathlib.Path(file_path)
        else:
            path_obj = pathlib.Path(pathlib.Path.cwd(), 'templates')
        path_obj.mkdir(parents=True, exist_ok=True)
        f_path = pathlib.Path(path_obj, f'{template_id}.jpg')
        with f_path.open('wb') as file_obj:
            file_obj.write(image)
        with self.session.begin():
            self.session.execute(
                update(self.temp_table)
                .values({'image_path': str(f_path.resolve())})
                .where(self.temp_table.c.id == template_id))
            self.session.commit()
        self.session.close()

    def insert_image_sql(self, template_id: str, image: bytes) -> None:
        """Insert binary image data to SQL Server."""
        logger.debug(f"Writing image to SQL for {template_id}")
        self.session.execute(
            update(self.temp_table)
            .values({'image_blob': image})
            .where(self.temp_table.c.id == template_id))
        self.session.commit()
        self.session.close()
