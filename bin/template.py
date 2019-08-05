class Template:

    EMPTY_TEMPLATE = '<!-- MAGNETIZER_CONTENT -->'

    def __init__(self, filename):

        if filename is not None:

            with open('../templates/' + filename, 'r') as myfile:
                self.template = myfile.read()

        else:
            self.template = Template.EMPTY_TEMPLATE

 
    def clear(self):
        self.template = Template.EMPTY_TEMPLATE
