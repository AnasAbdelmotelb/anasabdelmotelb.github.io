# Week 7 "Break Your Own Site": automated checks with Playwright (Chromium, Firefox, WebKit).
#
# Usage: python break_tests.py [BASE_URL] [OUT_DIR]
#   BASE_URL defaults to the live site. OUT_DIR receives results.json and screenshots/.
#
# Safety: every request to formspree.io is intercepted by page.route() and answered by a local mock,
# so these tests never send a real message. The mock records what the page *would* have sent.
import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://anasabdelmotelb.github.io").rstrip("/")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "evidence/week-7")
SHOTS = OUT / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=True)
PAGES = ["/", "/dns/", "/projects/tech-docs/", "/this-page-does-not-exist"]
ENGINES = ("chromium", "firefox", "webkit")
VIEWPORTS = {"mobile": {"width": 375, "height": 812}, "desktop": {"width": 1280, "height": 800}}


# ---------- contact form ----------
def formspree_mock(log, held):
    # Non-blocking: the route is held (request stays in flight) until answer() is called, so the test can
    # observe the loading state and fire extra clicks while the first request is still pending.
    def handler(route):
        req = route.request
        log.append({"method": req.method, "accept": req.headers.get("accept"), "body": req.post_data})
        held.append(route)
    return handler


def answer(route, kind):
    cors = {"Access-Control-Allow-Origin": "*"}
    if kind == "ok":
        route.fulfill(status=200, content_type="application/json", body='{"ok":true,"next":"/thanks"}', headers=cors)
    elif kind == "422":  # Formspree's JSON validation error
        route.fulfill(status=422, content_type="application/json", body='{"errors":[{"field":"email","message":"should be an email"}]}', headers=cors)
    elif kind == "blocked":  # Cloudflare-style block page: 403, HTML, no CORS header (what F7 looked like live)
        route.fulfill(status=403, content_type="text/html", body="<h1>Sorry, you have been blocked</h1>")
    else:  # network failure
        route.abort()


def loading_state(page):
    return page.evaluate("() => { const b = document.querySelector('.contact-form button[type=submit]'); return {disabled: b.disabled, text: b.textContent.trim()} }")


def settle(page, held, kind, in_flight_ms=800, total_ms=2500):
    """Keep requests in flight for in_flight_ms, then answer every request that arrived (including late duplicates)."""
    page.wait_for_timeout(in_flight_ms)
    waited = in_flight_ms
    while waited < total_ms:
        while held:
            answer(held.pop(0), kind)
        page.wait_for_timeout(100); waited += 100
    while held:
        answer(held.pop(0), kind)


def form_state(page):
    return page.evaluate("""() => {
      const f = document.querySelector('.contact-form'), s = f.querySelector('.form-status'), b = f.querySelector('button[type=submit]');
      return {
        status: s.hidden ? null : (s.dataset.state + ': ' + s.innerText.replace(/\\s+/g, ' ').trim()),
        button: (b.disabled ? 'disabled/' : '') + b.textContent.trim(),
        values: Object.fromEntries(['name', 'email', 'message'].map(n => [n, f.elements[n].value])),
        invalid: [...f.querySelectorAll('[required]')].filter(e => !e.validity.valid).map(e => e.name + ': ' + e.validationMessage),
        url: location.href,
      };
    }""")


# Exact texts the page must show (H1: one neutral error for every failure: timeout, network, 403, 422).
EXPECTED_ERROR = "Sorry, I couldn't send your message. Please try again, or contact me through Book a Call or LinkedIn."
EXPECTED_SUCCESS = "Thanks, your message was sent. I will reply by email."
EXPECTED_LINKS = ["https://cal.com/anas-mansour/intro-call", "https://www.linkedin.com/in/anas-mansour-b17302251/"]


def check_status(page, kind, typed):
    """Exact-wording assertion for the status line, plus the contact links and whether the typed text was kept."""
    got = page.evaluate("""() => { const s = document.querySelector('.form-status');
      return {hidden: s.hidden, state: s.dataset.state, text: s.innerText.replace(/\\s+/g, ' ').trim(),
              links: [...s.querySelectorAll('a')].map(a => a.href), message: document.querySelector('#contact-message').value} }""")
    if kind == "ok":
        ok = not got["hidden"] and got["state"] == "sent" and got["text"] == EXPECTED_SUCCESS and got["message"] == ""
    else:
        ok = (not got["hidden"] and got["state"] == "error" and got["text"] == EXPECTED_ERROR
              and got["links"] == EXPECTED_LINKS and got["message"] == typed)
    return {"exact_status_ok": ok, "status_text": got["text"], "status_links": got["links"], "message_after": got["message"][:40]}


def form_case(browser, label, fill, kind="ok", double=False, js=True):
    ctx = browser.new_context(java_script_enabled=js)
    page = ctx.new_page()
    log, held, dialogs, errors = [], [], [], []
    page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.route("**/formspree.io/**", formspree_mock(log, held))
    page.goto(BASE + "/#contact", wait_until="load")
    for k, v in fill.items():
        page.fill(f"#contact-{k}", v)
    btn = page.locator(".contact-form button[type=submit]")
    btn.dblclick(no_wait_after=True) if double else btn.click(no_wait_after=True)
    r = {"case": label, "kind": kind}
    if js:
        page.wait_for_timeout(300)
        r["state_while_in_flight"] = loading_state(page) if log else "no request (blocked before sending)"
    settle(page, held, kind)
    r["requests_sent"] = len(log)
    if not js and not page.url.startswith(BASE):
        r["result"] = "browser left the page with a plain POST (mock answered)"
    else:
        r.update(form_state(page))
        if js and len(log) == 1:
            r.update(check_status(page, kind, fill.get("message", "").strip()))
    if log:
        body = log[0]["body"] or ""
        r["sent_accept_header"] = log[0]["accept"]
        r["sent_gotcha_empty"] = bool(re.search(r'name="_gotcha"\r\n\r\n\r\n', body)) or "_gotcha=&" in body or body.endswith("_gotcha=")
        m = re.search(r'name="message"\r\n\r\n(.*?)\r\n------', body, re.S)
        r["sent_message_length"] = len(m.group(1)) if m else None
    r["dialogs"] = dialogs  # any alert() here would mean injected script ran
    r["page_errors"] = errors
    ctx.close()
    return r


VALID = {"name": "  W7 Test  ", "email": "w7-test@example.com", "message": "Automated test, not a real message."}
LONG = "Long message test. " * 160  # 3,040 characters, above the 2,000 maxlength
FORM_CASES = [
    ("empty submit", {}, "ok", False),
    ("malformed email: notanemail", {**VALID, "email": "notanemail"}, "ok", False),
    ("malformed email: a@", {**VALID, "email": "a@"}, "ok", False),
    ("malformed email: @example.com", {**VALID, "email": "@example.com"}, "ok", False),
    ("malformed email: a b@example.com", {**VALID, "email": "a b@example.com"}, "ok", False),
    ("edge email: a@b (valid under HTML rules)", {**VALID, "email": "a@b"}, "ok", False),
    ("whitespace-only name", {**VALID, "name": "     "}, "ok", False),
    ("whitespace-only message", {**VALID, "message": " \n\t  "}, "ok", False),
    ("garbage input", {"name": "%%%$$$###", "email": "x@y.zz", "message": "asdfghjkl;'[]\\=-0987 ~~~"}, "ok", False),
    ("unusually long message (3,040 chars)", {**VALID, "message": LONG}, "ok", False),
    ("adversarial: script tag", {**VALID, "message": "<script>alert('xss')</script>"}, "ok", False),
    ("adversarial: img onerror", {**VALID, "name": "\"><img src=x onerror=alert(1)>", "message": "<img src=x onerror=alert(2)>"}, "ok", False),
    ("adversarial: SQL-style", {**VALID, "message": "'; DROP TABLE messages; -- OR 1=1"}, "ok", False),
    ("unicode / RTL / emoji", {**VALID, "name": "أنس 🙂", "message": "مرحبا ‮test‬ 👋🏽 Ünïcødé"}, "ok", False),
    ("valid, double-click (duplicate check)", VALID, "ok", True),
    ("valid, server returns 422", VALID, "422", False),
    ("valid, Cloudflare-style 403 block", VALID, "blocked", False),
    ("valid, network failure", VALID, "network", False),
]


def form_tests(browser):
    res = [form_case(browser, *c) for c in FORM_CASES]
    # Rapid second and third submit via the Enter key while the first request is in flight
    ctx = browser.new_context(); page = ctx.new_page(); log, held = [], []
    page.route("**/formspree.io/**", formspree_mock(log, held))
    page.goto(BASE + "/#contact", wait_until="load")
    for k, v in VALID.items():
        page.fill(f"#contact-{k}", v)
    page.locator(".contact-form button[type=submit]").click(no_wait_after=True)
    page.wait_for_timeout(100)
    page.focus("#contact-email"); page.keyboard.press("Enter"); page.keyboard.press("Enter")
    settle(page, held, "ok")
    res.append({"case": "click then Enter twice while sending", "requests_sent": len(log), **form_state(page),
                **check_status(page, "ok", VALID["message"].strip())})
    ctx.close()
    # JavaScript disabled
    res.append(form_case(browser, "JS off: empty submit", {}, js=False))
    res.append(form_case(browser, "JS off: whitespace-only name", {**VALID, "name": "   "}, js=False))
    res.append(form_case(browser, "JS off: whitespace-only message (known gap)", {**VALID, "message": "   "}, js=False))
    return res


def honeypot_test(browser):
    ctx = browser.new_context(); page = ctx.new_page()
    page.goto(BASE + "/#contact", wait_until="load")
    hp = page.evaluate("""() => { const i = document.querySelector('#contact-gotcha'), w = i.closest('.honeypot'), r = i.getBoundingClientRect();
      return {name: i.name, tabindex: i.tabIndex, wrapper_display: getComputedStyle(w).display, aria_hidden: w.getAttribute('aria-hidden'),
              visible_box: r.width > 0 && r.height > 0, autocomplete: i.autocomplete} }""")
    # Tab through the whole form and check the honeypot never receives focus
    page.focus("#contact-name"); seen = []
    for _ in range(6):
        seen.append(page.evaluate("document.activeElement.id || document.activeElement.tagName"))
        page.keyboard.press("Tab")
    hp["tab_order_from_name"] = seen
    hp["honeypot_focused"] = "contact-gotcha" in seen
    ctx.close()
    return hp


# ---------- pages: console, layout, keyboard, SEO ----------
def page_checks(browser, engine):
    out = []
    for vp_name, vp in VIEWPORTS.items():
        ctx = browser.new_context(viewport=vp)
        for path in PAGES:
            page = ctx.new_page(); console, errors, failed = [], [], []
            page.on("console", lambda m: console.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("requestfailed", lambda r: failed.append(f"{r.url} {r.failure}"))
            resp = page.goto(BASE + path, wait_until="networkidle")
            info = page.evaluate("""() => {
              const m = n => document.querySelector(`meta[name="${n}"],meta[property="${n}"]`)?.content ?? null;
              const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => +h.tagName[1]);
              let skips = []; for (let i = 1; i < hs.length; i++) if (hs[i] > hs[i-1] + 1) skips.push(`h${hs[i-1]}->h${hs[i]}`);
              const ids = new Set([...document.querySelectorAll('[id]')].map(e => e.id));
              const badFrag = [...document.querySelectorAll('a[href*="#"]')].map(a => new URL(a.href)).filter(u => u.pathname === location.pathname && u.hash && !ids.has(decodeURIComponent(u.hash.slice(1)))).map(u => u.hash);
              const imgsNoAlt = [...document.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).length;
              const blank = [...document.querySelectorAll('a[target=_blank]')].filter(a => !/noopener/.test(a.rel)).map(a => a.href);
              return {
                title: document.title, lang: document.documentElement.lang, description: m('description'), robots: m('robots'),
                canonical: document.querySelector('link[rel=canonical]')?.href ?? null, favicon: document.querySelector('link[rel~=icon]')?.href ?? null,
                og: {title: m('og:title'), description: m('og:description'), url: m('og:url'), image: m('og:image'), type: m('og:type')},
                twitter_card: m('twitter:card'), h1_count: hs.filter(h => h === 1).length, heading_skips: skips,
                landmarks: {header: !!document.querySelector('header'), nav: !!document.querySelector('nav'), main: !!document.querySelector('main'), footer: !!document.querySelector('footer')},
                missing_fragment_targets: badFrag, imgs_without_alt: imgsNoAlt, target_blank_without_noopener: blank,
                horizontal_overflow_px: document.documentElement.scrollWidth - document.documentElement.clientWidth,
              };
            }""")
            shot = SHOTS / f"{engine}-{vp_name}-{(path.strip('/') or 'home').replace('/', '_')}.png"
            page.screenshot(path=str(shot), full_page=False)
            out.append({"engine": engine, "viewport": vp_name, "path": path, "status": resp.status if resp else None,
                        **info, "console": console, "page_errors": errors, "failed_requests": failed, "screenshot": str(shot.relative_to(OUT))})
            page.close()
        ctx.close()
    return out


def keyboard_test(browser):
    ctx = browser.new_context(viewport=VIEWPORTS["desktop"]); page = ctx.new_page()
    page.goto(BASE + "/", wait_until="load")
    order = []
    for _ in range(14):
        page.keyboard.press("Tab")
        order.append(page.evaluate("""() => { const e = document.activeElement, cs = getComputedStyle(e);
          return {text: (e.innerText || e.getAttribute('aria-label') || e.id || e.tagName).trim().slice(0, 40), href: e.getAttribute('href'),
                  focus_visible: e.matches(':focus-visible'), outline: cs.outlineStyle !== 'none' && cs.outlineWidth !== '0px'} }"""))
    # Skip link actually moves focus/scroll to main
    page.goto(BASE + "/", wait_until="load"); page.keyboard.press("Tab"); page.keyboard.press("Enter"); page.wait_for_timeout(300)
    skip = page.evaluate("() => ({hash: location.hash, active: document.activeElement.id || document.activeElement.tagName})")
    # Nav link via keyboard lands on the right section
    page.goto(BASE + "/", wait_until="load")
    page.locator("nav a", has_text="Contact").focus(); page.keyboard.press("Enter"); page.wait_for_timeout(600)
    nav = page.evaluate("() => ({hash: location.hash, contact_top: Math.round(document.querySelector('#contact').getBoundingClientRect().top)})")
    ctx.close()
    return {"tab_order_first_14": order, "skip_link_enter": skip, "nav_contact_enter": nav}


def mobile_device_test(p):
    # WebKit with an iPhone device profile: a different engine from the Chrome/Edge phone checks done before.
    dev = p.devices["iPhone 13"]
    b = p.webkit.launch(); ctx = b.new_context(**dev); page = ctx.new_page()
    page.goto(BASE + "/", wait_until="networkidle")
    info = page.evaluate("""() => ({overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      small_targets: [...document.querySelectorAll('a,button,input,textarea')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.height && (r.height < 24 || r.width < 24) && getComputedStyle(e).display !== 'none'; }).map(e => (e.innerText || e.id || e.tagName).trim().slice(0, 30))})""")
    page.screenshot(path=str(SHOTS / "webkit-iphone13-home-full.png"), full_page=True)
    page.goto(BASE + "/#contact", wait_until="networkidle"); page.wait_for_timeout(500)
    page.screenshot(path=str(SHOTS / "webkit-iphone13-contact.png"))
    ctx.close(); b.close()
    return {"device": "iPhone 13 profile (WebKit)", **info}


def main():
    results = {"base_url": BASE, "run_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "engines": {}}
    with sync_playwright() as p:
        for eng in ENGINES:
            b = getattr(p, eng).launch()
            results["engines"][eng] = {"version": b.version, "form": form_tests(b), "honeypot": honeypot_test(b),
                                       "pages": page_checks(b, eng), "keyboard": keyboard_test(b)}
            b.close()
            print("done", eng, flush=True)
        results["mobile_device"] = mobile_device_test(p)
    (OUT / "results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False))
    print("wrote", OUT / "results.json")
    # Save all observations before failing, so a failed run still has useful evidence.
    failures = []
    blocked = {c[0] for c in FORM_CASES[:5]} | {"whitespace-only name", "whitespace-only message",
               "JS off: empty submit", "JS off: whitespace-only name"}
    expected_cases = [c[0] for c in FORM_CASES] + ["click then Enter twice while sending",
        "JS off: empty submit", "JS off: whitespace-only name", "JS off: whitespace-only message (known gap)"]
    for eng in ENGINES:
        forms = results["engines"][eng]["form"]
        if [r["case"] for r in forms] != expected_cases:
            failures.append(f"{eng}: missing or unexpected form cases")
        for r in forms:
            label = f"{eng}: {r['case']}"
            expected_requests = 0 if r["case"] in blocked else 1
            if r["requests_sent"] != expected_requests:
                failures.append(f"{label}: expected {expected_requests} mocked request(s)")
            if expected_requests and not r["case"].startswith("JS off:"):
                if r.get("exact_status_ok") is not True:
                    failures.append(f"{label}: exact status, links or retained text failed/missing")
                if r.get("button") != "Send message":
                    failures.append(f"{label}: submit button not restored")
            if r.get("dialogs") or r.get("page_errors"):
                failures.append(f"{label}: unexpected dialog or JavaScript error")
    print("required form assertions:", "FAIL" if failures else "PASS", flush=True)
    if failures:
        raise AssertionError("\n".join(failures))


if __name__ == "__main__":
    main()
