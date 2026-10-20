# FlyRank AI Fluency, Week 7: Break Your Own Site

| | |
|---|---|
| **Portfolio** | https://anasabdelmotelb.github.io/ |
| **Repository** | https://github.com/AnasAbdelmotelb/anasabdelmotelb.github.io |
| **Test dates** | First pass 18 October 2026 (fixes in commit `d64cc96`); full re-test, new fixes and this report **20 October 2026** |
| **Author** | Anas Mansour, with Claude Code (AI assistant) running the automated tests |

## 1. Scope and testing environment

**In scope:** every public page:
- `/`, the homepage, including the contact form;
- `/dns/`;
- `/projects/tech-docs/`;
- the 404 page;
- `/cv.pdf` and the Tech Docs PDF;
- every link on these pages;
- the share/SEO metadata, `robots.txt` and the sitemap;
- speed, and whether the site can be found in search.

**Environment (20 October 2026):**

| Tool | Version / detail |
|---|---|
| Playwright (Python) | 1.64.0 |
| Browser engines | Chromium 156.0.8078.4 · Firefox 157.0 · WebKit 27.2 (Safari's engine) |
| Viewports | Mobile 375×812, desktop 1280×800, plus Playwright's **iPhone 13** device profile on WebKit |
| Targets | Live site (GitHub Pages) before the fixes; local `astro preview` of the fixed build; live site again after deploy |
| Other | curl (HTTP status, redirects, headers), `xmllint` with the official sitemaps.org XSD files, Google PageSpeed Insights (web UI), Google Search (browser) |
| Site | Astro 7.3.5, `@astrojs/sitemap` 3.7.4, GitHub Pages via GitHub Actions |

**Safety rules followed:**
- **No real messages today.** In every automated form test, Playwright intercepts the request to Formspree and answers it with a local mock, so nothing is delivered. **No real form messages were sent on 20 October 2026.**
- **Earlier real messages.** Before today, 5 real test messages were sent on 18 October, each approved by me. On 19 October I sent one more by hand from my phone ("Its a phone test"), and it arrived in the Formspree inbox.
- **No sign-ins.** The automation signed in to no account.
- **Search Console.** The Search Console checks below were done by me, signed in.

## 2. Where It Breaks

Severity:
- **High:** loses a visitor's message or blocks contact;
- **Medium:** a visible failure in a realistic situation;
- **Low:** a minor defect;
- **Info:** works as intended.

"Pass" means the case was actually run, in all three engines unless the row says otherwise.

### 2a. Re-test on 20 October 2026 (live site, before today's fixes)

| # | Test case | Actual result | Severity | Evidence |
|---|---|---|---|---|
| 1 | Submit the form empty | Blocked by the browser on every required field; **0 requests** | Pass | `live-before/summary.md` |
| 2 | Malformed emails: `notanemail`, `a@`, `@example.com`, `a b@example.com` | All 4 blocked with the browser's email message; 0 requests | Pass | same |
| 3 | Edge email `a@b` | Accepted and sent (valid under the HTML email rules) | Low, known (K1) | same |
| 4 | Whitespace-only name; whitespace-only message (spaces, tab, newline) | Both blocked, 0 requests ("Please match the requested format" / "Please write your message") | Pass | same |
| 5 | JavaScript off: empty; whitespace-only name; whitespace-only message | Empty and spaces-only name blocked. **A spaces-only message is posted** | Low, known (K2) | same |
| 6 | Garbage input (`%%%$$$###`, `asdfghjkl;'[]\=-0987 ~~~`) | Sent; success message shown | Pass | same |
| 7 | Unusually long message (3,040 characters) | Cut at the 2,000-character `maxlength`; 1,999 characters sent after trimming | Pass | same, `sent_message_length` in `results.json` |
| 8 | Adversarial strings: `<script>alert('xss')</script>`, `"><img src=x onerror=alert(1)>`, SQL-style `'; DROP TABLE …` | **No script ran**: no dialog and no page error. The status line uses fixed text only, so input is never echoed into the page | Pass | `dialogs: []`, `page_errors: []` in `results.json` |
| 9 | Unicode, Arabic, right-to-left override, emoji | Sent; success message | Pass | same |
| 10 | Double-click "Send message" | **1 request** | Pass | same |
| 11 | Click, then Enter twice while the first request is in flight | **1 request** | Pass | same |
| 12 | Loading state (observed 300 ms into a held request) | Button disabled, text "Sending…" | Pass | `state_while_in_flight` in `results.json` |
| 13 | Success state (mock 200) | "Thanks, your message was sent. I will reply by email."; form cleared; still on the site | Pass | same |
| 14 | Failure: mock 422, Cloudflare-style 403 (HTML, no CORS header) and network failure | Error message with Book a Call and LinkedIn links; **visitor's text kept**; still on the site; button usable again | Pass | same |
| 15 | **Stalled request: Formspree never answers** | Button stuck on **"Sending…" (disabled) for the whole 25 s test, with no message**. The visitor cannot retry or tell what happened | **Medium, fixed (F9)** | `live-before/hang_test.json` |
| 16 | Wording of the error message for timeouts or network errors | Always said "If it contains code or HTML, remove it", even when the cause was the network | **Low, fixed (H1)** | found in the hardening review (section 6) |
| 17 | Spam honeypot `_gotcha` | Hidden (`display:none`, `aria-hidden`), `tabindex=-1`, never reached by Tab, and **sent empty** with every legitimate message, so it does not block real visitors. Formspree's server-side filtering of a *filled* honeypot was not tested, because that would mean a real submission | Pass (client side) | `honeypot` in `results.json` |
| 18 | Internal links and assets (15) | All return 200 with the right type: pages are `text/html`, `cv.pdf` and the Tech Docs PDF are `application/pdf`, plus the favicon and CSS. Every in-page `#anchor` has a matching target | Pass | `link-check-live.tsv`, `missing_fragment_targets: []` |
| 19 | External destinations, fetched and checked by page title | Cal.com "15-Minute Intro Call with Anas"; GitHub profile `AnasAbdelmotelb`; repo `SpotFake_Project`; MDN "HTTP caching" | Pass | `link-check-live.tsv` |
| 20 | MDN Cache-Control link (Tech Docs page) | **HTTP 301** redirect to `/Web/HTTP/Reference/Headers/Cache-Control`. Works, but the link is out of date | **Low, fixed (F10)** | curl in `link-check-live.tsv` |
| 21 | LinkedIn profile link | curl gets HTTP 999 (bot block). A logged-out browser is sent to LinkedIn's sign-in wall, with a redirect back to the same profile | Low, known (K3) | browser check, 20 Oct |
| 22 | CV PDF | 200, `application/pdf`, 1 page, **byte-identical** to `public/cv.pdf` in the repo | Pass | curl + `cmp` |
| 23 | All 4 pages × 3 engines × mobile and desktop | **No horizontal overflow**, no failed requests, no JS errors. Only one console line, on the 404 page: the browser reporting the page's own 404 status, which is expected | Pass | `live-before/summary.md`, `live-before/screenshots/` |
| 24 | iPhone 13 profile (WebKit) | No overflow. Two targets are under 24 px on one side: the header "CV" link (21×44 px) and an inline text link. Both meet WCAG 2.5.8 (spacing exception / inline links), and PageSpeed's tap-target audit passes | Info | `webkit-iphone13-*.png` |
| 25 | Keyboard (Chromium, Firefox) | "Skip to content" is the first Tab stop; every stop has a visible focus outline; Enter on the skip link jumps to `#main`; Enter on nav "Contact" scrolls to `#contact` | Pass | `keyboard` in `results.json` |
| 26 | Keyboard (WebKit) | Tab moves only between form fields | Info, known (K4) | same |
| 27 | Missing page `/this-page-does-not-exist` | HTTP 404, custom page in the site layout, `noindex`, no canonical link | Pass | same |
| 28 | Sitemap and robots.txt | Both 200, no redirects, `application/xml` and `text/plain`; valid against the official XSD; all 3 URLs return 200 with matching canonicals and no `noindex`. **Search Console still reports "Couldn't fetch"** | Medium (reporting only), known (K5) | `sitemap-check.txt` |
| 29 | Google search | Homepage is indexed and ranks #1 for two name searches. `site:` shows **only the homepage**: `/dns/` and the case study are not indexed yet | Low, known (K6) | section 5 |

### 2b. First pass, 18 October 2026 (fixed and deployed in commit `d64cc96`)

| # | Test case | Result before the fix | Severity | Status |
|---|---|---|---|---|
| F1 | Share the homepage link | No `og:image`, `og:site_name` or Twitter card, so share previews had no picture | Medium | Fixed |
| F2 | Look for `robots.txt` and a sitemap | Both 404 | Medium | Fixed |
| F3 | Open a missing page | GitHub's generic 404 page, with no way back; on phones it scrolled sideways | Medium | Fixed |
| F4 | Search for the site | Not found by a non-Google search engine; no sitemap | Medium | Fixed (sitemap, JSON-LD); indexing confirmed later |
| F5 | Spaces-only name and message | Accepted and sent in all three engines | Medium | Fixed (JS on) |
| F6 | Fast double-click | **Firefox sent 2 messages** (confirmed in the inbox) | High | Fixed (JS on) |
| F7 | Message containing `<script>` (real, approved) | Formspree's Cloudflare protection blocked it. The visitor was taken to "Sorry, you have been blocked" and **the message was lost** | High | Fixed on my side: the visitor stays, sees an error with other contact links and keeps their text. Formspree's filter itself is K7 |
| F8 | Lighthouse accessibility | "(PDF, 92 KB)" label at 4.11:1 contrast, below 4.5:1 | Low | Fixed (5.0:1) |

Evidence for F6–F7: `earlier-2026-10-18/F7-cloudflare-block-after-submit.png`, `live-form-sent.png` and
`live-form-script-refused.png`, plus `form-tests-3-engines.json`.

## 3. Fixed

| # | Fix | Commit | Verification |
|---|---|---|---|
| F1–F8 | See 2b. Main changes:<br>• share image and Open Graph/Twitter tags (F1);<br>• `robots.txt` and `@astrojs/sitemap` (F2);<br>• custom `404.astro` with `noindex` (F3);<br>• Person JSON-LD (F4);<br>• form script: trimming, single send, background send with status messages (F5–F7);<br>• contrast fix (F8) | `d64cc96` (18 Oct) | Verified live on 18 October in all three engines. Two approved real messages: the plain one arrived; the `<script>` one was refused and the visitor kept their text. All of today's re-test rows 1–14 and 17–28 confirm these fixes still hold on the live site |
| **F9** | `src/pages/index.astro`: the form request now uses an `AbortController` and is cancelled after 15 s; the existing error message is shown, the visitor's text is kept and the button works again. The timer is cleared in `finally`, so it cannot affect a later send | this commit | **Before** (live, 25 s wait): stuck on "Sending…" in Chromium, Firefox and WebKit. **After** (local build, 20 s wait): error shown, button reads "Send message", text kept, in all three engines (`local-after/hang_test.json`) |
| **F10** | `src/pages/projects/tech-docs.astro`: the MDN Cache-Control link now points to its current address | this commit | The new URL returns 200 with no redirect; page title "Cache-Control header - HTTP \| MDN" |
| **H1** | Error message reworded to "Sorry, your message could not be sent. Please try again (if it contains code or HTML, remove that first), or reach me through Book a Call or LinkedIn." It is now correct for timeouts, network errors and Formspree's code filter | this commit | Shown for 422, 403, network failure and timeout in all three engines (`local-after/results.json`, `local-after/hang_test.json`) |
| Docs | README lists the 15-second timeout | this commit | — |

**Regression check after the fixes:** the full suite was re-run against the fixed local build (`local-after/summary.md`). All 22 form cases, the honeypot checks, all 24 page × engine × viewport checks and the keyboard checks give the same results as the live baseline. The only differences are the new error wording and the fixed hang case. Live results after deploy are in section 9.

## 4. Known Limitations

| # | Limitation | Impact | Next action |
|---|---|---|---|
| K1 | `a@b` passes the email check | A visitor could leave an address I cannot reply to | None in the browser. HTML rules allow it, and no form can prove a mailbox exists |
| K2 | **Without JavaScript**, a spaces-only message is sent, and a fast double-click may send twice (seen in Firefox on 18 Oct) | Rare: needs JS off. At worst an empty or duplicate email | Accept; a static site has no server to validate. Formspree's own validation could be explored |
| K3 | LinkedIn blocks automated checks (HTTP 999) and shows a sign-in wall to logged-out visitors | Some visitors must sign in to see the profile | Outside my control; the GitHub and Cal.com links are alternatives |
| K4 | In WebKit/Safari, Tab only moves between form fields by default | Safari keyboard users need Option-Tab or the "Press Tab to highlight each item" setting | Browser default; the site's own focus order and outlines are correct in Chromium and Firefox |
| **K5** | **Search Console sitemap status.** On 20 October, Search Console showed **"Couldn't fetch"** for both `sitemap-index.xml` and `sitemap-0.xml`, with 0 discovered pages. On the same day, its URL Inspection live test of `sitemap-index.xml` reported the URL is available to Google, crawling allowed and page fetch successful. My re-check (row 28) found both files valid, 200, no redirects, correct content type, correct host, valid against the official XSD, and identical to a fresh build | The sitemap is not yet reported as processed. The homepage is indexed anyway | Treated as an **unresolved Search Console processing/reporting issue**. The code was not changed just to force a different status. Next: wait, then remove and resubmit `sitemap-index.xml`. **Google has not confirmed processing the sitemap** |
| K6 | Only the homepage is in Google's index (`site:` query) | `/dns/` and the case study cannot be found in Google yet | Request indexing for both in URL Inspection; re-check in a week. Indexing is never guaranteed |
| K7 | Formspree's Cloudflare filter can refuse messages containing code or HTML | That message cannot be sent through the form | The visitor sees the error, keeps their text and gets Book a Call and LinkedIn links. The filter itself is Formspree's |
| K8 | A request that is slow but succeeds after 15 s is reported as failed | The visitor may resend, so I could get the same message twice | Accepted: 15 s is well above a normal response time (I did not measure Formspree's), and a possible duplicate is better than a form that stays stuck |
| K9 | GitHub Pages sets a 10-minute cache (`max-age=600`) | Changes can take up to 10 minutes to appear | Platform limit on free GitHub Pages |
| K10 | No field data in PageSpeed Insights | Scores are lab tests only | Real-user data (CrUX) needs more traffic |
| K11 | Formspree's Spam folder shows 2 messages that I have not reviewed | A real message could have been marked as spam | I will check the Spam folder in the Formspree dashboard |

## 5. SEO, metadata and speed

**Metadata.** Checked on every page in all three engines (`results.json` → `pages`):

| Check | `/` | `/dns/` | `/projects/tech-docs/` | 404 |
|---|---|---|---|---|
| `<title>` | Anas Mansour \| AI Engineer | How DNS Helps My Portfolio Load \| Anas Mansour | Tech Docs Research Workflow \| Anas Mansour | Page not found \| Anas Mansour |
| Meta description | ✓ | ✓ | ✓ | ✓ |
| Canonical (absolute, same host) | ✓ | ✓ | ✓ | none (correct for `noindex`) |
| `og:title/description/url/image/type`, `twitter:card=summary_large_image` | ✓ | ✓ | ✓ | ✓ |
| `robots` meta | none (indexable) | none | none | `noindex` ✓ |
| One `<h1>`, no skipped heading levels | ✓ | ✓ | ✓ | ✓ |
| Landmarks `header/nav/main/footer`, `lang="en"` | ✓ | ✓ | ✓ | ✓ |
| Images without `alt` | 0 | 0 | 0 | 0 |
| `target=_blank` without `noopener` | 0 | 0 | 0 | 0 |
| Favicon `/favicon.svg` (200, `image/svg+xml`) | ✓ | ✓ | ✓ | ✓ |

**Other checks:**
- **Share image:** `og-image.png` returns 200 (`image/png`, 1200×630).
- **Structured data:** the homepage has one valid Person JSON-LD block, with only facts shown on the page.
- **Accidental `noindex`:** none. Only the 404 page has it, which is intended.
- **No change needed:** no metadata was missing or wrong today, so nothing was changed.

**Sitemap:** `sitemap-index.xml` lists `sitemap-0.xml`. That file lists the 3 real pages, on the canonical host and without the 404 page. `robots.txt` contains `Sitemap: https://anasabdelmotelb.github.io/sitemap-index.xml`. For the full check see `sitemap-check.txt`, and K5 for the Search Console status.

**PageSpeed Insights:** Google's official tool (https://pagespeed.web.dev/) was run on the live homepage on 20 Oct 2026 at 7:54 PM GMT+3, using Lighthouse 13.5.0. Report: https://pagespeed.web.dev/analysis/https-anasabdelmotelb-github-io/2xxpmhwtro

| | Performance | Accessibility | Best Practices | SEO | FCP | LCP | TBT | CLS | Speed Index |
|---|---|---|---|---|---|---|---|---|---|
| **Mobile** (emulated Moto G Power) | **100** | **100** | **100** | **100** | 0.8 s | 0.8 s | 0 ms | 0 | 0.8 s |
| **Desktop** | **100** | **100** | **100** | **100** | 0.2 s | 0.2 s | 0 ms | 0 | 0.3 s |

- **Field data:** PageSpeed shows "No Data" for real users.
- **Why the web UI:** the keyless PageSpeed API returned HTTP 429 (daily quota exceeded) the same day, so the web UI was used.
- **Code version:** this run measured the site *before* today's two small fixes. Neither fix touches page weight or rendering.
- **Evidence:** `pagespeed-2026-10-20.json`, `screenshots/pagespeed-mobile-2026-10-20.jpg` and `screenshots/pagespeed-desktop-2026-10-20.jpg`.

## 6. Search discoverability (20 October 2026)

| Query | Engine | Result |
|---|---|---|
| `site:anasabdelmotelb.github.io` | Google | **1 result: the homepage**, "Anas Mansour \| AI Engineer". `/dns/` and `/projects/tech-docs/` are not listed (K6) |
| `"Anas Mansour" AI Engineer FlyRank` | Google | Portfolio is **result #1** |
| `Anas Mansour AI Engineer` | Google | Portfolio is **result #1** of 9 organic results |
| `anasabdelmotelb.github.io`, `Anas Mansour AI Engineer portfolio` | Claude's web-search tool (not Google) | Portfolio not found; results were people with similar names |
| URL Inspection (Search Console, by me, 19 Oct) | Google | Homepage: "URL is on Google", served over HTTPS |

- **What the results mean:** Google results depend on location and history. These came from one browser session in GMT+3, signed out of Google. They show the homepage is indexed and findable by name. They do not guarantee ranking for other people or other queries.
- **Evidence:** `screenshots/google-site-query-2026-10-20.jpg` and `screenshots/google-name-flyrank-query-2026-10-20.jpg`.
- **Screenshot not kept:** the third query's page showed other people's LinkedIn photos, so I recorded it as text only.

## 7. Hardening review

**Who reviewed:** Claude Code (an AI assistant) did an adversarial review of today's diff (F9, F10, H1, README) on 20 October 2026. **No human mentor reviewed today's changes.**

Earlier, a peer reviewer reviewed the 18 October fixes on 19 October. Their verdict was a conditional pass: one must-fix (CV education wording), which was resolved and deployed in commit `da864b9`, and the limits K2, K7 and K6 accepted as known.

| # | Question asked | Finding | Disposition |
|---|---|---|---|
| H1 | Is any message misleading? | Yes: after a timeout or network error, the error told the visitor to remove code or HTML | **Fixed** (reworded; verified in 3 engines) |
| H2 | Can the timeout cause a wrong "failed" when the message actually arrived? | Yes, if Formspree accepts the message but answers after more than 15 s | **Accepted** as K8 |
| H3 | Can a timeout from one send cancel a later send? | No: each send creates its own `AbortController`, and `clearTimeout` runs in `finally` | No action |
| H4 | Does the success message ever appear without a 2xx response? | No: success is shown only after `response.ok`. Mocks returning 403, 422, a network error or no answer all show the error | No action |
| H5 | Unsafe HTML handling? | `status.innerHTML` only takes fixed strings written in the code; user input is never inserted. Adversarial inputs produced no dialogs and no page errors | No action |
| H6 | Browser support for `AbortController` | Supported by every browser that runs the form's module script. Older browsers ignore module scripts and fall back to the plain HTML form | No action |
| H7 | Duplicate sends after the change? | Still exactly 1 request for a double-click and for click + Enter + Enter, in all three engines | No action |
| H8 | Broken navigation or links from the change? | No: the MDN link resolves with 200, and all other links are unchanged (row 18–19 checks re-run after deploy) | No action |
| H9 | Metadata errors? | No changes to metadata. One harmless quirk: the 404 page's `og:url` is `/404/`, but the page is `noindex` and not in the sitemap | Accepted, no action |
| H10 | Could the evidence leak secrets or private data? | Scanned: no keys or tokens. The only email addresses are test ones (`w7-test@example.com`, `b@example.com`, `x@y.zz`). The Formspree form ID is already public in the page HTML. No Formspree dashboard or inbox screenshots are included | No action |
| H11 | Does the evidence or report change the deployed site? | No: `reports/` and `evidence/` are outside `public/` and `src/pages/`; the built `dist/` contains neither | No action |

## 8. Evidence index

All paths are relative to `evidence/week-7/` in this repository.

| File | What it shows |
|---|---|
| `scripts/break_tests.py` | The Playwright test suite (Formspree mocked) |
| `scripts/hang_test.py` | The stalled-request test (row 15 / F9) |
| `scripts/summarize.py` | Turns `results.json` into `summary.md` |
| `live-before/results.json`, `live-before/summary.md` | Full results on the live site before today's fixes (20 Oct, 16:59 UTC) |
| `live-before/hang_test.json` | F9 before: stuck on "Sending…" after 25 s, 3 engines |
| `live-before/screenshots/` | 24 page screenshots (3 engines × 2 viewports × 4 pages) plus the iPhone 13 profile |
| `local-after/results.json`, `local-after/summary.md`, `local-after/hang_test.json` | Same suite on the fixed local build (screenshots not kept; they duplicate the live ones) |
| `live-after/` | Same suite on the live site after deploy (section 9) |
| `link-check-live.tsv` | Status, content type and final URL of every link |
| `sitemap-check.txt` | Headers, bodies, XSD validation and URL checks for the sitemap and robots.txt |
| `pagespeed-2026-10-20.json`, `screenshots/pagespeed-*.jpg` | PageSpeed Insights results |
| `screenshots/google-*.jpg` | Google search results |
| `earlier-2026-10-18/` | First-pass evidence: Cloudflare block page (F7), the real sent and refused live tests, phone-width and dark-mode screenshots, and the earlier form tests |

**Not in the repo:**
- the Formspree dashboard screenshot (it shows submitters' email addresses);
- my own phone screenshots;
- Search Console screenshots.

They stay in my private assignment folder. The Search Console statuses are quoted above.

## 9. Deployment and live verification

_Filled in after deploy._

## 10. Checklist against the assignment

| Requirement | Status |
|---|---|
| Tried to break the site: form (empty, garbage, malformed, whitespace, long, adversarial, duplicates, states, honeypot), links and destinations, layout, keyboard, console, 3 engines + phone profile | ✓ sections 2 and 8 |
| SEO and meta basics checked and correct | ✓ section 5 (no metadata change needed today) |
| Searched for the site | ✓ section 6 |
| Speed check with Google PageSpeed Insights, mobile and desktop, with date | ✓ section 5 |
| Triage into Fix now and Known limitations | ✓ sections 3 and 4 |
| Fix-nows fixed and re-tested | ✓ F1–F10 and H1, with before/after evidence |
| Hardening review, labelled honestly | ✓ section 7 (AI review today; earlier peer review stated separately) |
| Honest "where it breaks" list with evidence | ✓ section 2, with the evidence index in section 8 |
| No invented scores, results or claims about Google | ✓ The sitemap is reported as *not* processed (K5); indexing is shown only where Google showed it |
| Not done honestly | Formspree's server-side honeypot filtering was not tested (it would need a real submission). X and WhatsApp share previews were not checked (LinkedIn's was, on 19 Oct) |
