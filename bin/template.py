class Template:

    def __init__(self, filename):
        with open('../templates/' + filename, 'r') as myfile:
            self.template = myfile.read()
 
    def clear(self):
        self.template = '<!-- MAGNETIZER_CONTENT -->'
