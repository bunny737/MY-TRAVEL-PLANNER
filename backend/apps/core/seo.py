import json


def breadcrumb_jsonld(page, base_url, home_name, parent=None):
    """BreadcrumbList structured data for a page below the homepage, as a JSON string safe inside <script>.

    `parent` is an optional (name, path) between the homepage and the page, e.g. ('Blog', '/blog/').
    No Review, Product, Offer or rating markup is ever produced (CLAUDE.md invariant 3).
    """
    base = base_url.rstrip('/')
    trail = [(home_name, base + '/')]
    if parent:
        trail.append((parent[0], base + parent[1]))
    trail.append((page.title, page.canonical_url(base)))
    data = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': name, 'item': url} for i, (name, url) in enumerate(trail, start=1)
        ],
    }
    # Escape characters that could end the script element early.
    return json.dumps(data).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
