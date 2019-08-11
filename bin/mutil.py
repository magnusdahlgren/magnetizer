class MUtil:

    @staticmethod
    def link_first_tag(html, url):

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