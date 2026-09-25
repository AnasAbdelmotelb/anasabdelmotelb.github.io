# Anas Mansour — Portfolio

Personal portfolio of **Anas Mansour**, Computer Science Graduate & AI Enthusiast.

**Live site:** https://anasabdelmotelb.github.io/

## Stack

- [Astro](https://astro.build/) (static site generator)
- Hosted free on **GitHub Pages**
- Deployed automatically by **GitHub Actions** on every push to `main` (`.github/workflows/deploy.yml`)

## Status

Week 4, *Empty but Live*: a near-blank page is live. Projects, screenshots and case studies will be added in the following weeks.

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
├── public/                        # static assets (favicon)
├── src/
│   ├── layouts/Layout.astro       # shared HTML shell, meta tags, base styles
│   └── pages/index.astro          # home page
└── astro.config.mjs
```
