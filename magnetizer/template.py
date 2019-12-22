""" A module to provide simple html templates

"""
class Template:
    """ Template

    Parameters:
    content_tag - the tag used in the template to show where the content should go
    filename - the name of the file to read the template from
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, content_tag, filename):

        self.content_tag = content_tag

        if filename is not None:
            with open(filename, 'r') as myfile:
                self.template = myfile.read()
        else:
            self.template = self.content_tag

    def render(self, html):
        """ Renders a page or partial by inserting the given html into the template

        Parameters:
        html - The html block to insert into the template

        Returns:
        The html of the template with the given html content inserted at the appropriate place
        """

        return self.template.replace(self.content_tag, html, 1)
