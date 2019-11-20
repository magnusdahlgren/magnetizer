import re

class MUtil:

    @staticmethod
    def link_h1(html, url):

        match = re.search(r"<h1>(.*?)<\/h1>", html)
            
        if match:
            h1 = match.group()
            h1_content = match.group(1)
            return html.replace(h1, "<h1>" + MUtil.wrap_it_in_a_link(h1_content, url) + "</h1>", 1)
        else:
            return html


    @staticmethod
    def link_first_tag_no_more(html, url):

        html_rows = html.split('\n',1)
        first_row = html_rows[0]

        if first_row.startswith('<img '):
            result = MUtil.wrap_it_in_a_link(first_row, url)
            return '\n'.join([result, html_rows[1] ])

        if first_row.startswith('<h1>') and first_row.endswith('</h1>'):
            result = '<h1>' + MUtil.wrap_it_in_a_link(first_row[4:-5], url) + '</h1>'
            return '\n'.join([result, html_rows[1] ])

        return html


    @staticmethod
    def wrap_it_in_a_link(html, url):

        return "<a href='" + url + "'>" + html + "</a>"


    @staticmethod
    def downgrade_headings(html):

        html = html.replace('<h3','<h4')
        html = html.replace('</h3','</h4')

        html = html.replace('<h2','<h3')
        html = html.replace('</h2','</h3')

        html = html.replace('<h1','<h2')
        html = html.replace('</h1','</h2')

        return html


    @staticmethod
    def abstract_from_html(html):

        s = MUtil.strip_tags_from_html(MUtil.strip_anything_before_h1_from_html(html)).strip()
        s = re.sub(r'\n', ' ', s)
        s = re.sub(r'\s\s+',' ', s)

        if len(s) > 300:
            s = s[0:300] + '…'
        return s


    @staticmethod
    def first_image_url_from_html(html):

        pattern = "<img .*?src=['\"](.*?)['\"].*?>"
        match = re.search(pattern, html)
        
        if match:
            return match.group(1)
        else:
            return None


    @staticmethod
    def strip_tags_from_html(html):

        tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
        return tag_re.sub('', html)


    @staticmethod
    def strip_anything_before_h1_from_html(html):

        s = html.strip()
        if '</h1>' in s:
            return s.split('</h1>', 1)[1]
        else:
            return html


    @staticmethod
    def filter_out_non_article_filenames(filenames):

        result = []

        for filename in filenames:
            # starts with a number and a dash, but not 000-
            if re.search(r'^\d+-\S+\.md$', filename) and not re.search(r'^0+-\S+\.md$', filename):
                result.append(filename)

        return result

class colours:
    OK      = '\033[92m'
    WARNING = '\033[93m'
    ERROR   = '\033[91m'
    END     = '\033[0m'