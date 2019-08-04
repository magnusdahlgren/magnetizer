import pytest
from webpage import *


def test_webpage_from_file():

    RESULT = '<p>This is a test</p>'

    template = Template()
    template.template = '<!-- MAGNETIZER_CONTENT -->'

    webpage = Webpage(template)
    webpage.read('../content/my-post.md')

    assert webpage.html() == RESULT



def test_webpage_with_template():

    RESULT = '<html><body><p>(Web page content)</p></body></html>'

    template = Template()
    template.template = '<html><body><!-- MAGNETIZER_CONTENT --></body></html>'

    webpage = Webpage(template)
    webpage.md = '(Web page content)'

    assert webpage.html() == RESULT


def test_webpage_with_markdown():

    RESULT = '<h1>(Web page content)</h1>'

    template = Template()
    template.template = '<!-- MAGNETIZER_CONTENT -->'

    webpage = Webpage(template)
    webpage.md = '# (Web page content)'

    assert webpage.html() == RESULT




# run the tests from bin with $ python -m pytest ../tests/