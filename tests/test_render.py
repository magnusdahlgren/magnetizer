"""Tests for magnetizer/render.py — all HTML generation functions"""

import pytest
from magnetizer.content import Post
from magnetizer.render import (
    render_archive_page_content,
    render_article,
    render_index_page_content,
    render_page_title,
    render_post_page_content,
    render_template,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_post(
    id=1,
    date="2026-05-24",
    date_uk="24 May 2026",
    title="My Post",
    body_html="<p>Hello</p>",
    images=None,
):
    return Post(
        id=id,
        date=date,
        date_uk=date_uk,
        title=title,
        url=f"{id}.html",
        body_html=body_html,
        images=images or [],
    )


# ---------------------------------------------------------------------------
# render_article — structure
# ---------------------------------------------------------------------------

class TestRenderArticleStructure:

    def test_article_element_present(self):
        html = render_article(make_post(), on_index_page=False)
        assert "<article" in html
        assert "</article>" in html

    def test_article_id_attribute(self):
        html = render_article(make_post(id=7), on_index_page=False)
        assert 'id="post-7"' in html

    def test_article_has_single_post_class_on_post_page(self):
        html = render_article(make_post(), on_index_page=False)
        assert 'class="single-post"' in html

    def test_article_has_multiple_posts_class_on_index_page(self):
        html = render_article(make_post(), on_index_page=True)
        assert 'class="multiple-posts"' in html

    def test_post_body_present(self):
        html = render_article(make_post(body_html="<p>Hello</p>"), on_index_page=False)
        assert "<p>Hello</p>" in html

    def test_post_body_inside_div(self):
        html = render_article(make_post(body_html="<p>Hello</p>"), on_index_page=False)
        assert '<div class="post-body">' in html

    def test_footer_present(self):
        html = render_article(make_post(), on_index_page=False)
        assert "<footer>" in html

    def test_footer_omitted_when_no_date(self):
        post = Post(id=1, date=None, date_uk=None, title="About",
                    url="about.html", body_html="<p>Hi</p>", images=[])
        html = render_article(post, on_index_page=False)
        assert "<footer>" not in html

    def test_time_element_with_datetime_attribute(self):
        html = render_article(make_post(date="2026-05-24"), on_index_page=False)
        assert '<time datetime="2026-05-24">' in html

    def test_time_element_contains_uk_date(self):
        html = render_article(make_post(date_uk="24 May 2026"), on_index_page=False)
        assert "24 May 2026" in html


# ---------------------------------------------------------------------------
# render_article — title
# ---------------------------------------------------------------------------

class TestRenderArticleTitle:

    def test_h1_present_when_post_has_title(self):
        html = render_article(make_post(title="My Title"), on_index_page=False)
        assert "<h1>" in html or '<h1 ' in html

    def test_h1_contains_title_text(self):
        html = render_article(make_post(title="My Title"), on_index_page=False)
        assert "My Title" in html

    def test_h1_absent_when_no_title(self):
        html = render_article(make_post(title=None), on_index_page=False)
        assert "<h1>" not in html and "<h1 " not in html


# ---------------------------------------------------------------------------
# render_article — links on index vs post page
# ---------------------------------------------------------------------------

class TestRenderArticleLinks:

    def test_h1_contains_link_on_index_page(self):
        html = render_article(make_post(id=3, title="My Title"), on_index_page=True)
        assert '<h1><a href="3.html">My Title</a></h1>' in html

    def test_h1_has_no_link_on_post_page(self):
        html = render_article(make_post(id=3, title="My Title"), on_index_page=False)
        assert '<h1>My Title</h1>' in html

    def test_time_contains_link_on_index_page(self):
        html = render_article(make_post(id=3, date="2026-05-24", date_uk="24 May 2026"), on_index_page=True)
        assert '<a href="3.html">24 May 2026</a>' in html

    def test_time_has_no_link_on_post_page(self):
        html = render_article(make_post(id=3, date_uk="24 May 2026"), on_index_page=False)
        assert "24 May 2026" in html
        assert '<a href="3.html">24 May 2026</a>' not in html


# ---------------------------------------------------------------------------
# render_article — images
# ---------------------------------------------------------------------------

class TestRenderArticleImages:

    def test_no_images_block_when_post_has_no_images(self):
        html = render_article(make_post(images=[]), on_index_page=False)
        assert "post-images" not in html
        assert "<figure>" not in html

    def test_images_block_present_when_post_has_images(self):
        html = render_article(make_post(images=["1-image-01.jpg"]), on_index_page=False)
        assert '<div class="post-images">' in html

    def test_figure_element_per_image(self):
        html = render_article(make_post(images=["1-image-01.jpg", "1-image-02.png"]), on_index_page=False)
        assert html.count("<figure>") == 2

    def test_img_src_uses_resized_filename(self):
        html = render_article(make_post(images=["1-image-01.jpg"]), on_index_page=False)
        assert 'src="1-image-01-resized.jpg"' in html

    def test_resized_filename_for_png(self):
        html = render_article(make_post(images=["1-image-01.png"]), on_index_page=False)
        assert 'src="1-image-01-resized.png"' in html

    def test_images_in_order(self):
        html = render_article(
            make_post(images=["1-image-01.jpg", "1-image-02.jpg"]),
            on_index_page=False,
        )
        assert html.index("1-image-01-resized.jpg") < html.index("1-image-02-resized.jpg")

    def test_images_block_before_h1_and_body(self):
        html = render_article(
            make_post(title="T", images=["1-image-01.jpg"], body_html="<p>B</p>"),
            on_index_page=False,
        )
        images_pos = html.index("post-images")
        h1_pos = html.index("<h1>")
        body_pos = html.index("post-body")
        assert images_pos < h1_pos < body_pos

    def test_images_wrapped_in_link_on_index_page(self):
        html = render_article(make_post(id=1, images=["1-image-01.jpg"]), on_index_page=True)
        assert '<a href="1.html"><img src="1-image-01-resized.jpg"></a>' in html

    def test_images_not_wrapped_in_link_on_post_page(self):
        html = render_article(make_post(id=1, images=["1-image-01.jpg"]), on_index_page=False)
        assert '<a href="1.html"><img' not in html
        assert '<img src="1-image-01-resized.jpg">' in html


# ---------------------------------------------------------------------------
# render_post_page_content
# ---------------------------------------------------------------------------

class TestRenderPostPageContent:

    def test_article_wrapped_in_main(self):
        html = render_post_page_content(make_post(), index_page_url="index.html")
        assert "<main>" in html
        assert "</main>" in html

    def test_article_inside_main(self):
        html = render_post_page_content(make_post(id=1), index_page_url="index.html")
        main_start = html.index("<main>")
        article_start = html.index("<article")
        main_end = html.index("</main>")
        assert main_start < article_start < main_end

    def test_nav_present(self):
        html = render_post_page_content(make_post(), index_page_url="index.html")
        assert "<nav>" in html

    def test_back_link_url_includes_index_page_and_anchor(self):
        html = render_post_page_content(make_post(id=5), index_page_url="index-2.html")
        assert 'href="index-2.html#post-5"' in html

    def test_back_link_text(self):
        html = render_post_page_content(make_post(), index_page_url="index.html")
        assert "Back to homepage" in html

    def test_back_link_has_house_symbol(self):
        html = render_post_page_content(make_post(), index_page_url="index.html")
        assert "⌂ Back to homepage" in html

    def test_article_rendered_without_links(self):
        html = render_post_page_content(make_post(id=1, title="T"), index_page_url="index.html")
        assert '<h1>T</h1>' in html

    def test_back_link_in_separate_nav_from_post_navigation(self):
        html = render_post_page_content(make_post(), index_page_url="index.html",
                                        newer_url="2.html", older_url="1.html")
        back_pos = html.index("Back to homepage")
        older_pos = html.index("Older post")
        last_nav_before_back = html.rindex("<nav>", 0, back_pos)
        assert last_nav_before_back > older_pos


class TestRenderPostPageNavigation:

    def test_no_post_nav_when_only_post(self):
        html = render_post_page_content(make_post(), index_page_url="index.html")
        assert "Newer post" not in html
        assert "Older post" not in html

    def test_newer_link_present_when_newer_exists(self):
        html = render_post_page_content(make_post(), index_page_url="index.html",
                                        newer_url="2.html")
        assert "← Newer post" in html

    def test_older_link_present_when_older_exists(self):
        html = render_post_page_content(make_post(), index_page_url="index.html",
                                        older_url="1.html")
        assert "Older post →" in html

    def test_newer_link_href(self):
        html = render_post_page_content(make_post(), index_page_url="index.html",
                                        newer_url="5.html")
        assert 'href="5.html"' in html

    def test_older_link_href(self):
        html = render_post_page_content(make_post(), index_page_url="index.html",
                                        older_url="3.html")
        assert 'href="3.html"' in html

    def test_newer_link_has_newer_class(self):
        html = render_post_page_content(make_post(), index_page_url="index.html",
                                        newer_url="2.html")
        assert 'class="newer"' in html

    def test_older_link_has_older_class(self):
        html = render_post_page_content(make_post(), index_page_url="index.html",
                                        older_url="1.html")
        assert 'class="older"' in html

    def test_newer_link_omitted_when_no_newer_post(self):
        html = render_post_page_content(make_post(), index_page_url="index.html",
                                        older_url="1.html")
        assert "Newer post" not in html

    def test_older_link_omitted_when_no_older_post(self):
        html = render_post_page_content(make_post(), index_page_url="index.html",
                                        newer_url="2.html")
        assert "Older post" not in html

    def test_post_nav_appears_before_back_link(self):
        html = render_post_page_content(make_post(), index_page_url="index.html",
                                        newer_url="2.html", older_url="1.html")
        assert html.index("Newer post") < html.index("Back to homepage")


# ---------------------------------------------------------------------------
# render_index_page_content
# ---------------------------------------------------------------------------

class TestRenderIndexPageContent:

    def test_articles_wrapped_in_main(self):
        posts = [make_post(id=1), make_post(id=2)]
        html = render_index_page_content(posts, page_num=1, total_pages=1)
        assert "<main>" in html
        assert html.count("<article") == 2

    def test_all_posts_rendered(self):
        posts = [make_post(id=i) for i in range(1, 6)]
        html = render_index_page_content(posts, page_num=1, total_pages=1)
        assert html.count("<article") == 5

    def test_articles_rendered_with_links(self):
        posts = [make_post(id=1, title="T")]
        html = render_index_page_content(posts, page_num=1, total_pages=1)
        assert '<h1><a href="1.html">T</a></h1>' in html

    def test_nav_present_when_multiple_pages(self):
        posts = [make_post()]
        html = render_index_page_content(posts, page_num=2, total_pages=3)
        assert "<nav>" in html

    def test_no_nav_when_single_page(self):
        posts = [make_post()]
        html = render_index_page_content(posts, page_num=1, total_pages=1)
        assert "<nav>" not in html

    def test_newer_posts_link_absent_on_first_page(self):
        html = render_index_page_content([make_post()], page_num=1, total_pages=3)
        assert "Newer posts" not in html

    def test_older_posts_link_absent_on_last_page(self):
        html = render_index_page_content([make_post()], page_num=3, total_pages=3)
        assert "Older posts" not in html

    def test_both_links_present_on_middle_page(self):
        html = render_index_page_content([make_post()], page_num=2, total_pages=3)
        assert "Newer posts" in html
        assert "Older posts" in html

    def test_newer_posts_link_points_to_previous_page(self):
        html = render_index_page_content([make_post()], page_num=3, total_pages=4)
        assert 'href="index-2.html"' in html

    def test_newer_posts_link_on_page_2_points_to_index(self):
        html = render_index_page_content([make_post()], page_num=2, total_pages=3)
        assert 'href="index.html"' in html

    def test_older_posts_link_points_to_next_page(self):
        html = render_index_page_content([make_post()], page_num=2, total_pages=4)
        assert 'href="index-3.html"' in html

    def test_newer_posts_li_has_newer_class(self):
        html = render_index_page_content([make_post()], page_num=2, total_pages=3)
        assert '<li class="newer">' in html

    def test_older_posts_li_has_older_class(self):
        html = render_index_page_content([make_post()], page_num=1, total_pages=2)
        assert '<li class="older">' in html

    def test_newer_posts_link_has_left_arrow(self):
        html = render_index_page_content([make_post()], page_num=2, total_pages=3)
        assert '← Newer posts' in html

    def test_older_posts_link_has_right_arrow(self):
        html = render_index_page_content([make_post()], page_num=1, total_pages=2)
        assert 'Older posts →' in html


# ---------------------------------------------------------------------------
# render_page_title
# ---------------------------------------------------------------------------

class TestRenderPageTitle:

    def test_index_page_1_is_just_site_title(self):
        assert render_page_title("My Blog", None, page_num=1) == "My Blog"

    def test_index_page_2_includes_page_number(self):
        assert render_page_title("My Blog", None, page_num=2) == "My Blog - Page 2"

    def test_index_page_3_includes_page_number(self):
        assert render_page_title("My Blog", None, page_num=3) == "My Blog - Page 3"

    def test_post_with_title_is_title_dash_site(self):
        assert render_page_title("My Blog", "A Great Post", page_num=None) == "A Great Post - My Blog"

    def test_post_without_title_is_just_site_title(self):
        assert render_page_title("My Blog", None, page_num=None) == "My Blog"


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

class TestRenderTemplate:

    TEMPLATE = "<title>MAGNETIZER_TITLE</title><body>MAGNETIZER_CONTENT</body>"

    def test_title_placeholder_replaced(self):
        html = render_template(self.TEMPLATE, title="My Page", content="<p>hi</p>")
        assert "MAGNETIZER_TITLE" not in html
        assert "My Page" in html

    def test_content_placeholder_replaced(self):
        html = render_template(self.TEMPLATE, title="T", content="<main>stuff</main>")
        assert "MAGNETIZER_CONTENT" not in html
        assert "<main>stuff</main>" in html

    def test_rest_of_template_preserved(self):
        html = render_template(self.TEMPLATE, title="T", content="C")
        assert "<title>" in html
        assert "<body>" in html


# ---------------------------------------------------------------------------
# render_article — read more
# ---------------------------------------------------------------------------

class TestRenderArticleReadMore:

    def _post_with_excerpt(self):
        return Post(id=1, date="2026-05-24", date_uk="24 May 2026", title="My Post",
                    url="1.html", body_html="<p>Intro.</p><p>Rest.</p>",
                    excerpt_html="<p>Intro.</p>", images=[])

    def test_index_page_shows_excerpt_not_full_body(self):
        html = render_article(self._post_with_excerpt(), on_index_page=True)
        assert "<p>Intro.</p>" in html
        assert "<p>Rest.</p>" not in html

    def test_index_page_shows_read_more_link(self):
        html = render_article(self._post_with_excerpt(), on_index_page=True)
        assert "Read more →" in html

    def test_index_page_read_more_link_points_to_post(self):
        html = render_article(self._post_with_excerpt(), on_index_page=True)
        assert 'href="1.html"' in html
        assert 'class="read-more"' in html

    def test_index_page_no_read_more_when_no_excerpt(self):
        html = render_article(make_post(), on_index_page=True)
        assert "Read more" not in html

    def test_post_page_shows_full_body_when_excerpt_present(self):
        html = render_article(self._post_with_excerpt(), on_index_page=False)
        assert "<p>Intro.</p>" in html
        assert "<p>Rest.</p>" in html

    def test_post_page_no_read_more_link(self):
        html = render_article(self._post_with_excerpt(), on_index_page=False)
        assert "Read more" not in html


# ---------------------------------------------------------------------------
# render_archive_page_content
# ---------------------------------------------------------------------------

def make_dated_post(id, date, title=None):
    return Post(id=id, date=date, date_uk="", title=title,
                url=f"{id}.html", body_html="", images=[])


class TestRenderArchivePageContent:

    def test_has_main_element(self):
        html = render_archive_page_content([make_dated_post(1, "2026-05-24")])
        assert "<main>" in html and "</main>" in html

    def test_has_back_link_to_homepage(self):
        html = render_archive_page_content([make_dated_post(1, "2026-05-24")])
        assert 'href="index.html"' in html
        assert "Back to homepage" in html

    def test_month_heading(self):
        html = render_archive_page_content([make_dated_post(1, "2026-05-24")])
        assert "<h2>May 2026</h2>" in html

    def test_multiple_months_in_reverse_order(self):
        posts = [
            make_dated_post(2, "2026-05-24"),
            make_dated_post(1, "2026-04-10"),
        ]
        html = render_archive_page_content(posts)
        assert html.index("May 2026") < html.index("April 2026")

    def test_titled_post_shows_day_dash_title(self):
        html = render_archive_page_content([make_dated_post(1, "2026-05-24", title="Sunny day")])
        assert "24 - Sunny day" in html

    def test_untitled_post_shows_day_only(self):
        html = render_archive_page_content([make_dated_post(1, "2026-05-03")])
        assert ">3<" in html

    def test_day_has_no_leading_zero(self):
        html = render_archive_page_content([make_dated_post(1, "2026-05-03")])
        assert ">03<" not in html

    def test_each_entry_is_a_link_to_post(self):
        html = render_archive_page_content([make_dated_post(5, "2026-05-24", title="Hello")])
        assert 'href="5.html"' in html

    def test_posts_within_month_in_reverse_order(self):
        posts = [
            make_dated_post(3, "2026-05-30"),
            make_dated_post(1, "2026-05-10"),
        ]
        html = render_archive_page_content(posts)
        assert html.index("30") < html.index("10")

    def test_post_without_date_excluded(self):
        posts = [
            make_dated_post(2, "2026-05-24"),
            Post(id=1, date=None, date_uk=None, title="No date",
                 url="1.html", body_html="", images=[]),
        ]
        html = render_archive_page_content(posts)
        assert "No date" not in html

    def test_empty_posts_list(self):
        html = render_archive_page_content([])
        assert "<main>" in html
