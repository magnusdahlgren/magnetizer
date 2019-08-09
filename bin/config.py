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

                self.config[key] = value


    def value(self, key):
        return self.config[key]

        # if key in self.config:
        #    return self.config[key]
        #else:
        #    return None
        


