import pytest
from webpage import *


def test_webpage_from_file():

    RESULT = 'This is a test'

    template = Template()
    template.template = '<!-- MAGNETIZER_CONTENT -->'

    webpage = Webpage(template)
    webpage.read('../content/my-post.md')

    assert webpage.html() == RESULT



def test_webpage_with_template():

    RESULT = '<html><body><h1>(Web page content)</h1></body></html>'

    template = Template()
    template.template = '<html><body><h1><!-- MAGNETIZER_CONTENT --></h1></body></html>'

    webpage = Webpage(template)
    webpage.md = '(Web page content)'

    assert webpage.html() == RESULT




# run the tests from bin with $ python -m pytest ../tests/