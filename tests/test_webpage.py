import pytest
from webpage import *
from random import *


def test_webpage_from_file():

    RESULT = '<p>This is a test</p>'

    template = Template('_test.html')
    template.clear()

    webpage = Webpage(template)
    webpage.read('123-this-is-my-file.md')

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
    webpage.filename = 'my-post.html'
    webpage.write()

    with open('../public/my-post.html', 'r') as myfile:
        assert myfile.read() == '<p>' + RESULT + '</p>'


def test_template_from_file():

    RESULT = '<html><body class="test"><h1>Web page content</h1></body></html>'

    template = Template('_test.html')

    webpage = Webpage(template)
    webpage.md = '# Web page content'

    assert webpage.html() == RESULT


def test_filename_should_be_generated_from_input_file():

    FILENAME = '123-this-is-my-file.md'
    RESULT = 'this-is-my-file.html'

    template = Template('_test.html')
    template.clear()

    webpage = Webpage(template)
    webpage.read(FILENAME)

    assert webpage.filename == RESULT


def test_blogpost_render_html():

    RESULT = '<h1>Example</h1>'

    template = Template(None)

    blogpost = Blogpost(template)
    blogpost.md = "# Example"

    assert blogpost.html() == RESULT


def test_blogpost_template():

    RESULT = '<article><h1>Example</h1></article>'

    template = Template(None)
    template.template = '<article><!-- MAGNETIZER_CONTENT --></article>'

    blogpost = Blogpost(template)
    blogpost.md = "# Example"

    assert blogpost.html() == RESULT


@pytest.mark.skip(reason="test not implemented")
def test_blogpost_template_from_file():

    assert True

# run the tests from bin with $ python -m pytest ../tests/