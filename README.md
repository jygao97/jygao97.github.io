# Jingyue Gao's homepage

A single-page academic homepage built with Jekyll and the Beautiful Jekyll theme.
The homepage contains experience, education, and publications, with About Me and
Publications navigation links. Awards, blog posts, pagination, RSS, tags, and the
CV page have been removed.

## Edit content

- `index.html`: all experience, education, and publication content, section order,
  anchor IDs, and homepage title/subtitle.
- `_config.yml`: site name, navigation, colors, and contact links.
- `css/main.css`: shared styles and single-page section spacing.

All content and semantic HTML live directly in `index.html`; there are no separate
section content files. The opening profile includes the current team, a short bio,
contact links, and `img/self.jpeg`. The photo remains 200px wide on desktop; on mobile
it sits next to the name and team at 96px, with an 88px stacked fallback below 375px.
The image retains its original aspect ratio without cropping. The bio uses two
paragraphs below the mobile identity row. Email, GitHub, and Google Scholar share
the same link treatment. The email address is used by the Email link but is not
displayed as a separate line of text.

The navigation uses the same content width and gutters as the homepage, with a fixed
64px desktop height and a smaller mobile bar. `js/main.js` marks the currently viewed
section using `aria-current="location"`, including after resizing or opening details.
Experience and Education have main section headings, with earlier
internships in a native `details` disclosure. There is no separate About Me heading;
the About Me navigation link targets Experience through the preserved `#aboutme` anchor.

Publications form one continuous list without year grouping headings. Each entry
shows its title, venue/resource links (including the conference year), then authors.
Long author lists can be expanded without JavaScript. Use `Paper` for
paper links (including abstract pages), `Code` for repositories, and `site.baseurl`
for local PDFs in `papers/`. Keep full author names and equal-contribution notes.

The old `/aboutme/` and `/publications/` addresses redirect to their
homepage sections. The root Markdown files now contain only this redirect metadata;
edit `index.html` rather than adding content to those redirect pages.

## Local preview

Use a Ruby/Bundler environment compatible with the versions in `Gemfile.lock`:

```sh
bundle install
bundle exec jekyll serve
```

The existing lockfile targets the older GitHub Pages 193 / Jekyll 3.7.4 stack and a
Windows platform. A dependency/runtime upgrade is separate from this content change.

## Validate a build

```sh
bundle exec jekyll build
python3 tests/check_site.py _site
node tests/check_navigation.js
```

The check verifies the two content sections, profile/contact information, publication
structure, four internships, anchor and local file links, legacy redirects, sitemap
entries, and removal of awards/blog/CV routes.

To check a project-site prefix as well:

```sh
bundle exec jekyll build --baseurl /preview --destination /tmp/jygao97-preview
python3 tests/check_site.py /tmp/jygao97-preview --baseurl /preview
```

## Credits

Based on Beautiful Jekyll by Dean Attali, distributed under the MIT license.
The theme attribution is retained in the site footer and `LICENSE`.
