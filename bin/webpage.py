class Webpage:

    def __init__(self, filename):
        with open(filename, 'r') as myfile:
            self.html = myfile.read()