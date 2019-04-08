import os
import sys
import json
from configparser import ConfigParser

# defaults
DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.ini')
try:
    os.path.exists(DEFAULT_CONFIG)
except OSError:
    print("Configuration file {} does not exit".format(DEFAULT_CONFIG))


class ConfigDict:
    # inspiration: https://gist.github.com/amitsaha/3065184

    def __init__(self, config=DEFAULT_CONFIG):
        self.config = config

    def parse(self):
        config = ConfigParser()
        config.read(self.config)

        config_dict = {}

        # get defaults
        defaults = config.defaults()
        if defaults:
            config_dict['default'] = { key : float(value)
                                        if value != 'True' and value != 'False'
                                        else config.getboolean('DEFAULT', key)
                                        for (key, value) in config.defaults().items()
                                       }


        # get sections
        if config.sections():
            for section in config.sections():
                config_dict[section] = { key : float(value)
                                         if value != 'True' and value != 'False'
                                         else config.getboolean(section, key)
                                         for (key, value) in config[section].items()
                                         }

        try:
            config_dict['default']
        except Exception:
            print("No configuration information parsed.")
            sys.exit()

        return config_dict

    def parse_to_config(self):
        config = ConfigParser()
        config.read(self.config)

        return config

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Please provide a single config file as argument")
        sys.exit(1)

    config_dict = ConfigDict(sys.argv[1]).parse()

    print(json.dumps(config_dict, indent=2))


