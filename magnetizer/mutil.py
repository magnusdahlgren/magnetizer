""" Helper methods for Magnetizer
"""

from re import sub, search, compile as re_compile

COLOUR_OK = '\033[92m'
COLOUR_WARNING = '\033[93m'
COLOUR_ERROR = '\033[91m'
COLOUR_END = '\033[0m'


def link_h1(html, url):
    """Add a link to the first <h1> in the provided html

    Parameters:
    html - the html pontentially containing the <h1>
    url - the URL to link to

    Returns:
    The same html but with a link in the first <h1>
    """

    match = search(r"<h1>(.*?)<\/h1>", html)

    if match:
        heading = match.group()
        heading_content = match.group(1)
        return html.replace(heading, "<h1>" + wrap_it_in_a_link(heading_content, url) + "</h1>", 1)

    return html


def wrap_it_in_a_link(html, url):
    """ Wrap a link around some arbitrary html

    Parameters:
    html - the html around which to wrap the link
    url - the URL to link to

    Returns:
    The same html but with a link around it
    """

    return "<a href='" + url + "'>" + html + "</a>"


def downgrade_headings(html):
    """ 'Downgrade' headings one step, so that <h3> becomes <h4>, <h2> becomes <h3> etc

    Parameters:
    html - the html potentially containing <h1>, <h2> etc tags

    Returns:
    The same html but with h1, h2 and h3 downgraded one step
    """

    html = html.replace('<h3', '<h4')
    html = html.replace('</h3', '</h4')

    html = html.replace('<h2', '<h3')
    html = html.replace('</h2', '</h3')

    html = html.replace('<h1', '<h2')
    html = html.replace('</h1', '</h2')

    return html


def abstract_from_html(html):
    """ Creates a Twitter card-friendly abstract from some html

    Parameters:
    html - the html to create an abstract from

    Returns:
    The first 300 characters from the html that are not html tags
    """

    abstract = strip_tags_from_html(strip_anything_before_h1_from_html(html)).strip()
    abstract = sub(r'\n', ' ', abstract)
    abstract = sub(r'\s\s+', ' ', abstract)

    if len(abstract) > 300:
        abstract = abstract[0:300] + '…'
    return abstract


def first_image_url_from_html(html):
    """ Find the first image url in some html

    Parameters:
    html - html potentially containing <img> tags

    Returns:
    The URL from the first image in the html (or None if none)
    """

    pattern = "<img .*?src=['\"](.*?)['\"].*?>"
    match = search(pattern, html)

    if match:
        return match.group(1)

    return None


def strip_tags_from_html(html):
    """ Remove html tags from html

    Parameters:
    html - the html to remove tags from

    Returns:
    The html with all tags stripped

    todo: make better so that text between < and > isn't removed
    """

    tag_re = re_compile(r'(<!--.*?-->|<[^>]*>)')
    return tag_re.sub('', html)


def strip_anything_before_h1_from_html(html):
    """ Strip everything before the first <h1> tag in the html

    Parameters:
    html - the html potentially containing a <h1>

    Returns:
    The same html, but without anything before the first <h1> tag (if there is one)
    """

    stripped_html = html.strip()
    if '</h1>' in stripped_html:
        return stripped_html.split('</h1>', 1)[1]

    return html


def purge_non_article_filenames(filenames):
    """ Removes filenames not ending with .md from a list of filenames

    Parameters:
    filenames - list of filenames

    Returns:
    The list of filenames but with any filenames not ending with .md removed
    """

    result = []

    for filename in filenames:
        if search(r'^\d+-\S+\.md$', filename):
            result.append(filename)

    return result


def md_footnotes(source):
    """ Adds footnote anchor links to a block of markdown, linking from [^nn] to [^nn]:

    Parameters:
    source - a block of markdown

    Returns:
    Markdown with footnote anchor links added
    """

    result = source

    # replace references [^nn] with "<a href='#nn'>[nn]</a>"
    reference_re = re_compile(r'\[\^(\d+?)\](?!:)')
    result = reference_re.sub(r"<a href='#\1'>[\1]</a>", result)

    # replace footnotes [^nn]: with "<a id='nn'>[nn]:"
    footnote_re = re_compile(r'\[\^(\d+?)\]:')
    result = footnote_re.sub(r"<a id='\1'></a>[\1]:", result)

    return result
