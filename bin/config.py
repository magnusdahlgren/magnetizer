class Config:

    def __init__(self, filename):
        
        self.config = {}

        with open(filename, 'r') as f:
            raw_config = f.readlines()

        for line in raw_config:

            parts = line.split('=', 1)

            if len(parts) == 2:

                key = parts[0].strip()
                value = parts[1].strip()

                self.config[key] = value
        


