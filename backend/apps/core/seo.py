import json


def breadcrumb_jsonld(page, base_url, home_name):
    """BreadcrumbList structured data for a page below the homepage, as a JSON string safe inside <script>.

    No Review, Product or rating markup is ever produced (CLAUDE.md invariant 3).
    """
    base = base_url.rstrip('/')
    data = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': home_name, 'item': base + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': page.title, 'item': page.canonical_url(base)},
        ],
    }
    # Escape characters that could end the script element early.
    return json.dumps(data).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
