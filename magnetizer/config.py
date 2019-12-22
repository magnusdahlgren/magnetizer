""" Magnetizer Config

Reads a config file with key-value pairs (two strings separated by a dash) and
lets user use the key to retrieve the value.
"""

class Config:
    """
    Parameters:
    filename - filname of the config file to read

    Example file format:
    output_path     = tests/public/
    website_name    = Test website name
    """

    def __init__(self, filename):

        self.config = {}

        with open(filename, 'r') as file_contents:
            raw_config = file_contents.readlines()

        for line in raw_config:

            parts = line.split('=', 1)

            if len(parts) == 2 and not parts[0].startswith('#'):

                key = parts[0].strip()
                value = parts[1].strip()

                if value.startswith('[') and value.endswith(']'):
                    value = value[1:-1].split(',')
                    value = [element.strip() for element in value]

                self.config[key] = value


    def value(self, key):
        """ Look up key

        Parameters:
        key

        Returns:
        value of key
        """
        return self.config[key]


    def set(self, key, value):
        """ Sets value of key (used for tests only)

        Parameters:
        key
        value
        """

        self.config[key] = value
