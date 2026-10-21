# Results for https://anasabdelmotelb.github.io (2026-10-21T15:11:36Z)

Engines: chromium 156.0.8078.4, firefox 157.0, webkit 27.2

## Contact form (Formspree mocked, nothing sent)

| Case | chromium | firefox | webkit |
|---|---|---|---|
| empty submit | 0 req; blocked: name: Please fill out this field. | 0 req; blocked: name: Please fill out this field. | 0 req; blocked: name: Fill out this field |
| malformed email: notanemail | 0 req; blocked: email: Please include an '@' in the email address. 'notanema | 0 req; blocked: email: Please enter an email address. | 0 req; blocked: email: Enter an email address |
| malformed email: a@ | 0 req; blocked: email: Please enter a part following '@'. 'a@' is incomplete | 0 req; blocked: email: Please enter an email address. | 0 req; blocked: email: Enter an email address |
| malformed email: @example.com | 0 req; blocked: email: Please enter a part followed by '@'. '@example.com' i | 0 req; blocked: email: Please enter an email address. | 0 req; blocked: email: Enter an email address |
| malformed email: a b@example.com | 0 req; blocked: email: A part followed by '@' should not contain the symbol  | 0 req; blocked: email: Please enter an email address. | 0 req; blocked: email: Enter an email address |
| edge email: a@b (valid under HTML rules) | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK |
| whitespace-only name | 0 req; blocked: name: Please match the requested format. | 0 req; blocked: name: Please match the requested format: Please enter your n | 0 req; blocked: name: Match the requested format: Please enter your name |
| whitespace-only message | 0 req; blocked: message: Please write your message. | 0 req; blocked: message: Please write your message. | 0 req; blocked: message: Please write your message. |
| garbage input | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK |
| unusually long message (3,040 chars) | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK |
| adversarial: script tag | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK |
| adversarial: img onerror | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK |
| adversarial: SQL-style | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK |
| unicode / RTL / emoji | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK |
| valid, double-click (duplicate check) | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK | 1 req; in flight: disabled 'Sending…'; sent; exact text OK |
| valid, server returns 422 | 1 req; in flight: disabled 'Sending…'; error; exact text OK | 1 req; in flight: disabled 'Sending…'; error; exact text OK | 1 req; in flight: disabled 'Sending…'; error; exact text OK |
| valid, Cloudflare-style 403 block | 1 req; in flight: disabled 'Sending…'; error; exact text OK | 1 req; in flight: disabled 'Sending…'; error; exact text OK | 1 req; in flight: disabled 'Sending…'; error; exact text OK |
| valid, network failure | 1 req; in flight: disabled 'Sending…'; error; exact text OK | 1 req; in flight: disabled 'Sending…'; error; exact text OK | 1 req; in flight: disabled 'Sending…'; error; exact text OK |
| click then Enter twice while sending | 1 req; sent | 1 req; sent | 1 req; sent |
| JS off: empty submit | 0 req; blocked: name: Please fill out this field. | 0 req; blocked: name: Please fill out this field. | 0 req; blocked: name: Fill out this field |
| JS off: whitespace-only name | 0 req; blocked: name: Please match the requested format. | 0 req; blocked: name: Please match the requested format: Please enter your n | 0 req; blocked: name: Match the requested format: Please enter your name |
| JS off: whitespace-only message (known gap) | 1 req; browser left the page with a plain POST (mock answered) | 1 req; browser left the page with a plain POST (mock answered) | 1 req; browser left the page with a plain POST (mock answered) |

## Honeypot (`_gotcha`)

- chromium: display=none, aria-hidden=true, tabindex=-1, reached by Tab: False
- firefox: display=none, aria-hidden=true, tabindex=-1, reached by Tab: False
- webkit: display=none, aria-hidden=true, tabindex=-1, reached by Tab: False

## Pages

| Engine | Viewport | Path | Status | h1 | Heading skips | Overflow px | Console errors/warnings | Page errors | robots | canonical |
|---|---|---|---|---|---|---|---|---|---|---|
| chromium | mobile | / | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/ |
| chromium | mobile | /dns/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/dns/ |
| chromium | mobile | /projects/tech-docs/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/projects/tech-docs/ |
| chromium | mobile | /this-page-does-not-exist | 404 | 1 | - | 0 | error: Failed to load resource: the server responded with a status of 404 () | - | noindex | - |
| chromium | desktop | / | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/ |
| chromium | desktop | /dns/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/dns/ |
| chromium | desktop | /projects/tech-docs/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/projects/tech-docs/ |
| chromium | desktop | /this-page-does-not-exist | 404 | 1 | - | 0 | error: Failed to load resource: the server responded with a status of 404 () | - | noindex | - |
| firefox | mobile | / | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/ |
| firefox | mobile | /dns/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/dns/ |
| firefox | mobile | /projects/tech-docs/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/projects/tech-docs/ |
| firefox | mobile | /this-page-does-not-exist | 404 | 1 | - | 0 | - | - | noindex | - |
| firefox | desktop | / | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/ |
| firefox | desktop | /dns/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/dns/ |
| firefox | desktop | /projects/tech-docs/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/projects/tech-docs/ |
| firefox | desktop | /this-page-does-not-exist | 404 | 1 | - | 0 | - | - | noindex | - |
| webkit | mobile | / | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/ |
| webkit | mobile | /dns/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/dns/ |
| webkit | mobile | /projects/tech-docs/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/projects/tech-docs/ |
| webkit | mobile | /this-page-does-not-exist | 404 | 1 | - | 0 | error: Failed to load resource: the server responded with a status of 404 () | - | noindex | - |
| webkit | desktop | / | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/ |
| webkit | desktop | /dns/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/dns/ |
| webkit | desktop | /projects/tech-docs/ | 200 | 1 | - | 0 | - | - | - | https://anasabdelmotelb.github.io/projects/tech-docs/ |
| webkit | desktop | /this-page-does-not-exist | 404 | 1 | - | 0 | error: Failed to load resource: the server responded with a status of 404 () | - | noindex | - |

## Keyboard

- chromium: Tab order: Skip to content → Anas Mansour → About → Skills → Experience → Projects → Writing → DNS → Contact → CV → Download CV (PDF, 135 KB) → Book a Call
(opens in a new tab) → LinkedIn
(opens in a new tab) → GitHub
(opens in a new tab). Without a visible outline: none. Skip link + Enter: {'hash': '#main', 'active': 'BODY'}. Nav 'Contact' + Enter: {'hash': '#contact', 'contact_top': 391}.
- firefox: Tab order: Skip to content → Anas Mansour → About → Skills → Experience → Projects → Writing → DNS → Contact → CV → Download CV (PDF, 135 KB) → Book a Call
(opens in a new tab) → LinkedIn
(opens in a new tab) → GitHub
(opens in a new tab). Without a visible outline: none. Skip link + Enter: {'hash': '#main', 'active': 'BODY'}. Nav 'Contact' + Enter: {'hash': '#contact', 'contact_top': 83}.
- webkit: Tab order: contact-name → contact-email → contact-message → Skip to content
Anas Mansour
About
Skill → contact-name → contact-email → contact-message → Skip to content
Anas Mansour
About
Skill → contact-name → contact-email → contact-message → Skip to content
Anas Mansour
About
Skill → contact-name → contact-email. Without a visible outline: ['Skip to content\nAnas Mansour\nAbout\nSkill', 'Skip to content\nAnas Mansour\nAbout\nSkill', 'Skip to content\nAnas Mansour\nAbout\nSkill']. Skip link + Enter: {'hash': '', 'active': 'contact-name'}. Nav 'Contact' + Enter: {'hash': '#contact', 'contact_top': 80}.

## Mobile device profile

- iPhone 13 profile (WebKit): horizontal overflow 0 px; targets under 24 px on one side: ['CV', 'How DNS Helps My Portfolio Loa']
