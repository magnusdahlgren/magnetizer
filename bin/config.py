class Config:

    def __init__(self, filename):
        
        self.config = {}

        with open(filename, 'r') as f:
            raw_config = f.readlines()

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
        return self.config[key]
        


