
from configparser import RawConfigParser
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

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
        Initialize the Config object with or without sections.

        :param sections: A single section of the config
        :rtype sections: list or str
        :param uppercase: A boolean value to set the sections name to be all
            uppercase or not.
        :rtype uppercase: bool
        """
        if sections:
            self.add_section(sections, uppercase=uppercase)

    def __str__(self):
        """
        Sections in a Config object are simply other Config object. Detect if
        the current instance of Config has sections or not. If there is a
        section return a list of the sections and if it doesn't return a dict
        of the values as we will assume self to be a section

        :return: A str representation of the object
        """
        if self.has_section:
            list_section = [key for key in self.__dict__.keys()]
            return "<Sections: {}>".format(", ".join(list_section))
        else:
            list_entries = ["{}: {}, ".format(key, value)
                            for key, value in self.__dict__.items()]
            if list_entries:
                list_entries[-1] = "{}".format(list_entries[-1][:-2])
            return "<ENTRIES: {{{}}}>".format("".join(list_entries))

    @property
    def has_section(self):
        """
        Sections in a Config object are simply other Config object. Detect if
        the current instance of Config has sections or not. If the current
        instance doesn't have sections, it means it's the content of a section.

        :return: True if self has sections, False otherwise.
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
        :param uppercase: A boolean value to set the sections name to be all
            uppercase or not.
        :rtype uppercase: bool
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
        :rtype value: str
        :param uppercase: A boolean value to set the key to be all uppercase
            or not.
        :rtype uppercase: bool
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
    def parse_value(value, remove_quotes=True):
        """
        Take a config value and attempt to parse it from String to other python
        format that may be better suited. This function is used because
        everything read from the RawConfigParser is always considered as
        string.

        For specific rules on how to write values to be parsed correctly, see
        config/freespace_default.cfg

        :param: value: The value to be parsed.
        :rtype value: str
        :param remove_quotes: Some people are used to surround strings by
        single or dual quotes in a config file. Strings surrounded by quotation
        mark preserve those quotation in the resulting string. Setting
        remove_quotes to True will attempt to remove quotations surrounding
        strings if they are found.
        :rtype remove_quotes: boolean

        :return: The parsed value cast as a new type or the original value.
        """
        # Attempt to cast as Boolean True
        if value.lower() in ['true', 'yes']:
            return True

        # Attempt to cast as Boolean False
        if value.lower() in ['false', 'no']:
            return False

        # Attempt to cast as None
        if value.lower() in ['none', 'null']:
            return None

        # Attempt to cast as int
        try:
            return int(value)
        except ValueError:
            pass

        # Attempt to cast as float
        try:
            return float(value)
        except ValueError:
            pass

        # Attempt to cast as list
        if value.startswith("[") and value.endswith("]"):
            new_value = value[1:-1]
            try:
                return [Config.parse_value(part.strip())
                        for part in new_value.split(',')]
            except:
                pass

        # Removing quotes surrounding string value
        if (remove_quotes and value.startswith(("'", '"')) and
                value.endswith(("'", '"'))):
            value = value[1:-1]

        return value


def load_config():
    """
    Load the content of the different configuration files of the project in a
    global config object to be imported into other modules.
    """

    global config
    config = Config()

    # Set loading order of the possible configs. Order: increasing in priority
    load_order = [
        # Default config
        os.path.join(os.path.dirname(__file__), 'freespace_default.cfg'),
        # Local override
        os.path.join(os.path.dirname(__file__), 'freespace.cfg'),
        # Server override
        '/etc/freespace/freespace.cfg']

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
    """
    Load the different logging config as defined in the global config of the
    application.
    """
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
