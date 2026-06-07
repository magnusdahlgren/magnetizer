def render_sitemap(pages, config):
    site_url = config["site_url"].rstrip('/')
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url_path, lastmod in pages:
        lines.append('  <url>')
        lines.append(f'    <loc>{site_url}/{url_path}</loc>')
        if lastmod:
            lines.append(f'    <lastmod>{lastmod}</lastmod>')
        lines.append('  </url>')
    lines.append('</urlset>')
    return '\n'.join(lines)


def render_robots_txt(config):
    site_url = config["site_url"].rstrip('/')
    return f"User-agent: *\nAllow: /\n\nSitemap: {site_url}/sitemap.xml\n"
