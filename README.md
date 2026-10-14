# Anas Mansour — Portfolio

Personal portfolio of **Anas Mansour**, AI Engineer and Backend AI Engineer Intern at FlyRank AI.

**Live site:** https://anasabdelmotelb.github.io/

## What's on the site

- **Homepage** (`/`): hero with positioning and links to LinkedIn, GitHub, a Cal.com booking page and the CV, followed by About, Technical Skills, Experience, Selected Projects, Graduation Project (SpotFake) and Writing & Technical Notes sections.
- **DNS walkthrough** (`/dns/`): a technical note explaining how DNS resolves this site, covering the recursive resolver, nameservers, DNS records, the response and TTL, and CNAME records.
- **CV download** (`/cv.pdf`): the public PDF CV, linked from the hero, navigation and footer.

## Stack

- [Astro](https://astro.build/) (static site generator, no client-side JavaScript)
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
│   └── favicon.svg
├── src/
│   ├── layouts/Layout.astro       # shared HTML shell, navigation, footer, meta tags, base styles
│   └── pages/
│       ├── index.astro            # homepage
│       └── dns.astro              # DNS walkthrough (/dns/)
└── astro.config.mjs
```
