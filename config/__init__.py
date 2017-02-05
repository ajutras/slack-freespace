
from configparser import RawConfigParser
import os
import logging
import sys
from logging.handlers import RotatingFileHandler

config = None


class Config:
    """
    Usage:

    config = Config('myapp')
    config.MYAPP.add('name', 'MyFirstApp')

    ---

    from <yourpath>.config import config
    print("my app is named: {}".format(config.MYAPP.NAME))
    """

    def __init__(self, sections=None, uppercase=True):
        """

        :param sections: A single section of the config
        :rtype sections: list or str
        """
        if sections:
            self.add_section(sections, uppercase=uppercase)

    def __str__(self):
        if self.has_section:
            list_section = [key for key in self.__dict__.keys()]
            return "<Sections: {}>".format(", ".join(list_section))
        else:
            list_entries = ["{}: {}, ".format(key, value)
                            for key, value in self.__dict__.items()]
            if list_entries:
                list_entries[-1] = "{}}}".format(list_entries[-1][:-2])
            return "<ENTRIES: {{{}>".format("".join(list_entries))

    @property
    def has_section(self):
        """

        :return:
        """

        for value in self.__dict__.values():
            if isinstance(value, Config):
                return True
        else:
            return False

    def add_section(self, section_names, uppercase=True):
        """
        Add one or more section(s) to the config object

        :param section_names: The name(s) of the section to add to the config
        :rtype section_names: str or list
        """
        if not isinstance(section_names, list):
            section_names = [section_names]

        for section_name in section_names:
            if uppercase:
                section_name = section_name.upper()

            if section_name not in self.__dict__:
                self.__dict__[section_name] = Config()

    def add(self, data, value=None, uppercase=True):
        """
        Add one or more key(s)/value(s) to the config object

        :param data: Either a dict containing one or more key(s)/value(s) to
            put in a section of the config or a single key in the form of a
            string
        :rtype data: dict or str

        :param value: If data is a string representing a single key, value
            must be set to the desired value for this key.
        """

        if isinstance(data, dict):
            for key, value in data.items():
                if uppercase:
                    key = key.upper()
                self.__dict__[key] = self.parse_value(value)
        # Only insert a single key/value if a value was passed
        elif value:
            if uppercase:
                data = data.upper()
            self.__dict__[data] = self.parse_value(value)

    @staticmethod
    def parse_value(value):
        """

        """
        if value.lower() in ['true', 'yes']:
            return True

        if value.lower() in ['false', 'no']:
            return False

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        return value


def load_config():
    """
    Load the content of the different configuration files of the project in a
    global config object to be imported into other modules.
    """
    print("I AM LOADING THE CONFIG!")

    global config
    config = Config()

    # Define where to get the different configs
    default_path = os.path.join(os.path.dirname(__file__),
                                'freespace_default.cfg')
    local_override_path = os.path.join(os.path.dirname(__file__),
                                       os.path.pardir, 'freespace.cfg')
    server_override_path = '/etc/freespace/freespace.cfg'

    # Set loading order. In order of increasing priority
    load_order = [default_path, local_override_path, server_override_path]

    # Load conf files and set the sections and values in the config object
    for conf_path in load_order:
        if os.path.isfile(conf_path):
            config_parser = RawConfigParser()
            config_parser.read(conf_path)
            config.add_section(config_parser.sections())
            for section in config_parser.sections():
                config.add_section(section)
                for section_key, section_value in config_parser.items(section):
                    getattr(config, section).add(section_key, section_value)

    load_logging_config()


def load_logging_config():
    print("routine de logging")
    logger = logging.getLogger()
    logger.setLevel(config.LOGGING.LOGGER_MIN_LEVEL)

    formatter = logging.Formatter(config.LOGGING.LOGGER_FORMAT,
                                  style=config.LOGGING.LOGGER_FORMATTER_STYLE,
                                  datefmt=config.LOGGING.LOGGER_DATE_FORMAT)

    # Create terminal channel
    if config.LOGGING.LOGGER_TERMINAL:
        channel_terminal = logging.StreamHandler(sys.stdout)
        channel_terminal.setLevel(config.LOGGING.LOGGER_TERMINAL_MIN_LEVEL)
        channel_terminal.setFormatter(formatter)
        logger.addHandler(channel_terminal)

    # Create file channel
    if config.LOGGING.LOGGER_FILE:
        channel_file = RotatingFileHandler(
            config.LOGGING.LOGGER_FILE_PATH,
            encoding=config.FREESPACE.ENCODING,
            backupCount=config.LOGGING.LOGGER_FILE_MAX_ROTATION,
            maxBytes=config.LOGGING.LOGGER_FILE_MAX_SIZE)
        channel_file.setLevel(config.LOGGING.LOGGER_FILE_MIN_LEVEL)
        channel_file.setFormatter(formatter)
        logger.addHandler(channel_file)