import pytest
from webpage import *


def test_webpage_hardcoded_html():

    RESULT = '<html><body><h1>This is a test</h1></body></html>'

    webpage = Webpage('../content/my-post.md')

    assert webpage.html == RESULT


# run the tests from bin with $ python -m pytest ../tests/