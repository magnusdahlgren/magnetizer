from re import sub, search, compile, findall

class MUtil:

    @staticmethod
    def link_h1(html, url):

        match = search(r"<h1>(.*?)<\/h1>", html)
            
        if match:
            h1 = match.group()
            h1_content = match.group(1)
            return html.replace(h1, "<h1>" + MUtil.wrap_it_in_a_link(h1_content, url) + "</h1>", 1)
        else:
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
        s = sub(r'\n', ' ', s)
        s = sub(r'\s\s+',' ', s)

        if len(s) > 300:
            s = s[0:300] + '…'
        return s


    @staticmethod
    def first_image_url_from_html(html):

        pattern = "<img .*?src=['\"](.*?)['\"].*?>"
        match = search(pattern, html)
        
        if match:
            return match.group(1)
        else:
            return None


    @staticmethod
    def strip_tags_from_html(html):

        tag_re = compile(r'(<!--.*?-->|<[^>]*>)')
        return tag_re.sub('', html)


    @staticmethod
    def strip_anything_before_h1_from_html(html):

        s = html.strip()
        if '</h1>' in s:
            return s.split('</h1>', 1)[1]
        else:
            return html


    @staticmethod
    def purge_non_article_filenames(filenames):

        result = []

        for filename in filenames:
            if search(r'^\d+-\S+\.md$', filename):
                result.append(filename)

        return result

class colours:
    OK      = '\033[92m'
    WARNING = '\033[93m'
    ERROR   = '\033[91m'
    END     = '\033[0m'