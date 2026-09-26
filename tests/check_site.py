"""Check the generated single-page site using only the Python standard library."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.sections = []
        self.links = []
        self.nav_links = []
        self.feeds = []
        self.in_nav = False
        self.elements = []
        self.stack = []
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        node = {'tag': tag, 'attrs': attrs, 'ancestors': list(self.stack), 'text': []}
        self.elements.append(node)
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                       'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append(node)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'nav':
            self.in_nav = True
        if tag == 'section':
            self.sections.append(attrs.get('aria-labelledby'))
        if tag == 'a':
            href = attrs.get('href', '')
            self.links.append(href)
            if self.in_nav and 'navbar-brand' not in attrs.get('class', ''):
                self.nav_links.append(href)
        if tag == 'link' and attrs.get('type') == 'application/rss+xml':
            self.feeds.append(attrs)

    def handle_endtag(self, tag):
        if tag == 'nav':
            self.in_nav = False
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]['tag'] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        for node in self.stack:
            node['text'].append(data)

    def by_class(self, name):
        return [node for node in self.elements
                if name in node['attrs'].get('class', '').split()]


def text(node):
    return ' '.join(''.join(node['text']).split())


def inside(node, parent):
    return any(ancestor is parent for ancestor in node['ancestors'])


def check_profile(page):
    assert len([node for node in page.elements if node['tag'] == 'main']) == 1
    assert len([node for node in page.elements if node['tag'] == 'h1']) == 1
    intro = page.by_class('profile-intro')[0]
    assert 'Douyin Search' in text(intro) and 'ByteDance' in text(intro)
    portraits = page.by_class('profile-photo')
    assert len(portraits) == 1 and portraits[0]['tag'] == 'img'
    portrait = portraits[0]
    assert inside(portrait, intro), 'Photo must appear in the opening profile'
    assert portrait['attrs'].get('alt') == 'Jingyue Gao'
    assert portrait['attrs'].get('width') == '255' and portrait['attrs'].get('height') == '256'
    bio = page.by_class('profile-bio')[0]
    assert bio['attrs'].get('lang') == 'en'
    paragraphs = [node for node in page.elements if node['tag'] == 'p' and inside(node, bio)]
    assert len(paragraphs) == 2, 'The bio must separate team responsibilities and research focus'
    emphasis = [node for node in page.elements if node['tag'] == 'strong' and inside(node, bio)]
    assert len(emphasis) == 1 and text(emphasis[0]) == 'retrieval and query understanding'
    identity = page.by_class('profile-identity')[0]
    assert inside(identity, intro)
    assert not inside(bio, identity), 'Mobile biography must span the full intro width'
    assert all(term in text(bio) for term in (
        'Douyin Search', 'query understanding', 'R&D', 'LLMs', 'contextualized query understanding'
    ))
    descriptions = [node['attrs']['content'] for node in page.elements
                    if node['tag'] == 'meta' and (
                        node['attrs'].get('name') in ('description', 'twitter:description')
                        or node['attrs'].get('property') == 'og:description')]
    assert len(descriptions) == 3, 'Expected page, Open Graph, and Twitter descriptions'
    assert all(value == text(bio) for value in descriptions), (
        'Homepage bio and metadata differ: update index.html meta-description to match both bio paragraphs'
    )
    contact = page.by_class('profile-contact')[0]
    assert inside(contact, intro), 'Contact links must be in the opening profile'
    assert [text(node) for node in page.elements if node['tag'] == 'a' and inside(node, contact)] == [
        'Email', 'GitHub', 'Google Scholar'
    ], 'Contact labels must have equal visual weight'
    assert not page.by_class('contact-address'), 'The standalone email address must not be displayed'
    assert 'gaojingyuepku@gmail.com' not in text(intro)
    contact_links = [node['attrs']['href'] for node in page.elements
                     if node['tag'] == 'a' and inside(node, contact)]
    assert 'mailto:gaojingyuepku@gmail.com' in contact_links, 'Keep the Email link functional'
    assert 'https://github.com/jygao97' in contact_links
    scholar_url = 'https://scholar.google.com/citations?user=R1gfGdQAAAAJ&hl=en'
    assert scholar_url in contact_links
    scholar_links = [node for node in page.elements
                     if node['tag'] == 'a' and node['attrs'].get('href') == scholar_url]
    assert len(scholar_links) == 2, 'Scholar must appear in both the introduction and footer'
    assert all(text(node) == 'Google Scholar' for node in scholar_links)
    assert [text(node) for node in page.by_class('background-heading')] == ['Experience', 'Education']
    assert [text(node) for node in page.elements if node['tag'] == 'h2'] == [
        'Experience', 'Education', 'Publications'
    ]
    assert all(node['tag'] == 'h2' for node in page.by_class('background-heading'))
    about_anchor = next(node for node in page.elements if node['attrs'].get('id') == 'aboutme')
    assert text(about_anchor) == 'Experience'
    assert about_anchor['attrs'].get('tabindex') == '-1'
    grid = page.by_class('background-grid')[0]
    assert len([node for node in page.elements if node['tag'] == 'li' and inside(node, grid)]) == 4
    internships = page.by_class('earlier-experience')[0]
    assert len([node for node in page.elements if node['tag'] == 'li' and inside(node, internships)]) == 4
    assert not page.by_class('publication-year'), 'Year grouping headings must be removed'
    assert len(page.by_class('publication-list')) == 1, 'Publications must form one continuous list'
    assert not any(re.fullmatch(r'\d{4}', text(node)) for node in page.elements
                   if node['tag'] in ('h2', 'h3', 'h4')), 'Standalone year heading remains'
    assert [text(node) for node in page.by_class('publication-venue')] == [
        'CIKM 2026', 'CIKM 2023', 'CIKM 2023', 'SIGKDD 2023', 'IJCAI 2021',
        'AAAI 2021', 'CIKM 2020', 'AAAI 2019', 'CIKM 2019', 'ICDM 2019',
        'IJCAI 2019', 'PAKDD 2018'
    ]
    papers = page.by_class('publication')
    assert len(papers) == 12, 'A publication is missing'
    for paper in papers:
        title = [node for node in page.by_class('publication-title') if inside(node, paper)]
        meta = [node for node in page.by_class('publication-meta') if inside(node, paper)]
        authors = [node for node in page.by_class('publication-authors') if inside(node, paper)]
        assert len(title) == len(meta) == len(authors) == 1
        assert title[0]['tag'] == 'h3'
        assert page.elements.index(title[0]) < page.elements.index(meta[0]) < page.elements.index(authors[0])
        assert 'Jingyue Gao' in text(authors[0])
        for link in page.elements:
            if link['tag'] == 'a' and inside(link, meta[0]):
                assert text(link) in ('Paper', 'Code')
                assert text(title[0]) in link['attrs'].get('aria-label', '')
    assert len(page.by_class('contribution-note')) == 3
    assert not page.by_class('award-name') and 'awards' not in page.ids, 'Awards must be removed'
    for details in [node for node in page.elements if node['tag'] == 'details']:
        assert 'open' not in details['attrs'], 'Secondary information should start collapsed'
        assert len([node for node in page.elements if node['tag'] == 'summary' and inside(node, details)]) == 1
    viewport = next(node['attrs']['content'] for node in page.elements
                    if node['tag'] == 'meta' and node['attrs'].get('name') == 'viewport')
    assert 'maximum-scale' not in viewport and 'user-scalable=no' not in viewport


def check_site(destination, baseurl):
    html = (destination / 'index.html').read_text()
    page = Page(html)
    sections = ['aboutme', 'publications']
    assert page.sections == sections, page.sections
    assert page.nav_links == ['#' + section for section in sections], page.nav_links
    assert len(page.ids) == len(set(page.ids)), 'Duplicate HTML IDs'
    assert not page.feeds, 'RSS discovery link is still present'
    assert not any(marker in html for marker in [
        '{{', '{%', 'posts-list', 'post-preview', 'Older Posts', 'Curriculum Vitae'
    ]), 'Homepage contains templates or removed blog/CV content'
    assert 'LEMUR: Large scale End-to-end MUltimodal Recommendation' in html
    assert 'Peking University Award for Excellent Graduate' not in html
    assert not any('awards' in href.lower() for href in page.links), 'Awards link remains'
    check_profile(page)
    portrait = page.by_class('profile-photo')[0]
    assert portrait['attrs'].get('src') == baseurl + '/img/self.jpeg'
    assert (destination / 'img/self.jpeg').is_file(), 'Profile photo was not copied into the build'

    for href in page.links:
        url = urlsplit(href)
        if url.scheme and url.scheme not in ('http', 'https'):
            continue
        if url.netloc and url.netloc != 'jygao97.github.io':
            continue
        if url.fragment and not url.path:
            assert unquote(url.fragment) in page.ids, 'Missing anchor: ' + href
            continue
        path = unquote(url.path)
        if baseurl and path.startswith(baseurl + '/'):
            path = path[len(baseurl):]
        local = destination / path.lstrip('/')
        assert local.exists(), 'Missing local link target: ' + href

    for section in sections:
        redirect = (destination / section / 'index.html').read_text()
        expected = baseurl + '/#' + section
        assert 'content="0; url=' + expected + '"' in redirect
        assert 'href="' + expected + '"' in redirect
        assert 'profile-section' not in redirect, 'Legacy page duplicates content'

    for name in ['awards', 'awards.html', 'cv', 'cv.html', 'feed.xml', 'tags', 'tags.html', 'page2', '_posts', 'tests']:
        assert not (destination / name).exists(), 'Removed/internal route was built: ' + name
    assert not list(destination.glob('20??-??-??-*')), 'Article routes were built'

    sitemap = ET.parse(destination / 'sitemap.xml')
    locations = [node.text for node in sitemap.iter() if node.tag.endswith('}loc')]
    for location in locations:
        assert not any('/' + name in urlsplit(location).path for name in [
            'aboutme', 'publications', 'awards', 'cv', 'tags', 'page2', '20'
        ]), 'Sitemap includes a removed/redirected page: ' + location

    error_page = Page((destination / '404.html').read_text())
    assert error_page.nav_links == [baseurl + '/#' + section for section in sections]
    print('PASS: profile/photo/contact, 12 publications, awards removed, 4 internships, disclosures, '
          'anchors, local links, redirects, removed routes, sitemap, 404 navigation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', nargs='?', default='_site', type=Path)
    parser.add_argument('--baseurl', default='')
    args = parser.parse_args()
    check_site(args.destination, args.baseurl.rstrip('/'))
