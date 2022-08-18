import configparser
import pathlib
import logging
from configparser import SectionProxy

logger = logging.getLogger()


class Config:
    def __init__(self, conf='config.ini', conf_dict: dict = {}):
        default_conf = {
            'klaviyo': {
                'items_per_page': 250,
                'days': 30,
                'windows_auth': True,
                'schema': 'dbo',
                'db': 'klaviyo',
            },
        }
        path_obj = pathlib.Path(conf)
        if path_obj.is_absolute():
            self.config_file = path_obj
        else:
            self.config_file = pathlib.Path.cwd().joinpath(conf)

        self.parser = configparser.ConfigParser()
        self.parser.read_dict(default_conf)

        if not self.config_file.exists():
            logger.debug("Config file not found")
        else:
            self.parser.read(str(self.config_file))

        self.parser.read(conf_dict)

    @property
    def klaviyo(self) -> SectionProxy:
        return self.parser['klaviyo']
