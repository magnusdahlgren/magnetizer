import pytest
from webpage import *
from random import *


def test_webpage_from_file():

    RESULT = '<p>This is a test</p>'

    template = Template('_test.html')
    template.clear()

    webpage = Webpage(template)
    webpage.read('../content/my-post.md')

    assert webpage.html() == RESULT



def test_webpage_with_template():

    RESULT = '<html><body><p>(Web page content)</p></body></html>'

    template = Template('_test.html')
    template.template = '<html><body><!-- MAGNETIZER_CONTENT --></body></html>'

    webpage = Webpage(template)
    webpage.md = '(Web page content)'

    assert webpage.html() == RESULT


def test_webpage_with_markdown():

    RESULT = '<h1>(Web page content)</h1>'

    template = Template('_test.html')
    template.clear()

    webpage = Webpage(template)
    webpage.md = '# (Web page content)'

    assert webpage.html() == RESULT


def test_webpage_write():

    RESULT = 'TEST-' + str(randint(1, 1000000))

    template = Template('_test.html')
    template.clear()

    webpage = Webpage(template)
    webpage.md = RESULT
    webpage.write()

    with open('../public/my-post.html', 'r') as myfile:
        assert myfile.read() == '<p>' + RESULT + '</p>'


def test_template_from_file():

    RESULT = '<html><body class="test"><h1>Web page content</h1></body></html>'

    template = Template('_test.html')

    webpage = Webpage(template)
    webpage.md = '# Web page content'

    assert webpage.html() == RESULT

    

# run the tests from bin with $ python -m pytest ../tests/