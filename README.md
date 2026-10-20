# Anas Mansour — Portfolio

Personal portfolio of **Anas Mansour**, AI Engineer and Backend AI Engineer Intern at FlyRank AI.

**Live site:** https://anasabdelmotelb.github.io/

## What's on the site

- **Homepage** (`/`): hero with positioning and links to LinkedIn, GitHub, a Cal.com booking page and the CV, followed by About, Technical Skills, Experience, Selected Projects, Graduation Project (SpotFake), Writing & Technical Notes and Contact (a Formspree form) sections.
- **Tech Docs case study** (`/projects/tech-docs/`): how the Tech Docs Research Workflow works, one real run (HTTP caching) with what review caught, and the results of all five recorded test runs.
- **DNS walkthrough** (`/dns/`): a technical note explaining how DNS resolves this site, covering the recursive resolver, nameservers, DNS records, the response and TTL, and CNAME records.
- **CV download** (`/cv.pdf`): the public PDF CV, linked from the hero, navigation and footer.
- **Not-found page** (`/404.html`): GitHub Pages shows it for any address that does not exist, with links back to the real pages. It is marked `noindex`.

## Findability

- Every page has a title, a description and a canonical URL.
- Social-share preview: Open Graph and Twitter card tags with a 1200×630 image (`public/og-image.png`), all as absolute URLs.
- `robots.txt` allows all crawlers and points to the sitemap.
- The sitemap (`sitemap-index.xml`, `sitemap-0.xml`) is generated at build time by `@astrojs/sitemap` from the real pages (the 404 page is left out).
- The homepage includes Person structured data (JSON-LD) with only facts shown on the page.

These help search engines find and describe the site; they do not guarantee that it is indexed or ranked.

## Contact form and JavaScript

The site is static HTML and CSS. The only JavaScript is a small script for the contact form, and the form also
works without it:

- **Without JavaScript**, the form posts directly to Formspree, and the visitor is taken to Formspree's page.
  The browser checks that every field is filled in, that the email looks like an email and that the name is not only spaces.
- **With JavaScript**, the form is sent in the background and the visitor stays on the page. The script:
  - refuses a name or message made only of spaces;
  - sends only once, even on a fast double click;
  - shows "Thanks, your message was sent" on success;
  - shows a clear error with other ways to get in touch if the message cannot be sent;
  - gives up after 15 seconds if Formspree does not answer, so the button never stays on "Sending…".

### Known limitations

- Formspree's protection (Cloudflare) can refuse messages that contain code or HTML, for example a `<script>` tag.
  With JavaScript the visitor now sees an error and other ways to get in touch; the site cannot change Formspree's filter.
- Without JavaScript, a message made only of spaces is still sent, and a fast double click can send twice in some browsers (seen in Firefox).
- An address like `a@b` passes the browser's email check: it is valid under the HTML rules, and no form can confirm that a mailbox exists.
- GitHub Pages caches files for 10 minutes and the site cannot change that.

## Stack

- [Astro](https://astro.build/) (static site generator) with `@astrojs/sitemap`
- Hosted free over HTTPS on **GitHub Pages**
- Deployed automatically by **GitHub Actions** on every push to `main` (`.github/workflows/deploy.yml`)

## Run locally

Requires Node.js 22.12 or newer.

```sh
npm install
npm run dev      # http://localhost:4321
npm run build    # outputs static site to dist/
npm run preview  # serve the built site locally
```

## Project structure

```text
.
├── .github/workflows/deploy.yml   # build + deploy to GitHub Pages
├── public/
│   ├── cv.pdf                     # downloadable CV
│   ├── favicon.svg
│   ├── og-image.png               # 1200×630 social-share preview image
│   └── robots.txt
├── src/
│   ├── layouts/Layout.astro       # shared HTML shell, navigation, footer, meta and share tags, base styles
│   └── pages/
│       ├── index.astro            # homepage (and the contact form script)
│       ├── 404.astro              # not-found page
│       ├── dns.astro              # DNS walkthrough (/dns/)
│       └── projects/tech-docs.astro  # Tech Docs case study (/projects/tech-docs/)
└── astro.config.mjs               # site URL and the sitemap integration
```
