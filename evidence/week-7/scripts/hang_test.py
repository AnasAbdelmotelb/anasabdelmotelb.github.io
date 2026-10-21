# Edge case: Formspree never answers (stalled network). The request is intercepted and never fulfilled,
# so nothing is sent. Records the form state after WAIT seconds. Usage: python hang_test.py BASE_URL WAIT_SECONDS
import json, sys
EXPECTED_ERROR = "Sorry, I couldn't send your message. Please try again, or contact me through Book a Call or LinkedIn."
from playwright.sync_api import sync_playwright
BASE, WAIT = sys.argv[1].rstrip("/"), int(sys.argv[2])
out = {}
with sync_playwright() as p:
    for eng in ("chromium", "firefox", "webkit"):
        b = getattr(p, eng).launch(); page = b.new_page(); held = []
        page.route("**/formspree.io/**", lambda route: held.append(route))  # never fulfilled
        page.goto(BASE + "/#contact", wait_until="load")
        page.fill("#contact-name", "W7 Test"); page.fill("#contact-email", "w7-test@example.com"); page.fill("#contact-message", "Hang test.")
        page.click(".contact-form button[type=submit]", no_wait_after=True)
        page.wait_for_timeout(WAIT * 1000)
        out[eng] = page.evaluate("""() => { const b = document.querySelector('.contact-form button[type=submit]'), s = document.querySelector('.form-status');
            return {after_seconds: %d, button: (b.disabled ? 'disabled/' : '') + b.textContent.trim(), status: s.hidden ? null : s.dataset.state + ': ' + s.innerText.replace(/\\s+/g, ' ').trim(),
                    message_kept: document.querySelector('#contact-message').value} }""" % WAIT)
        out[eng]["requests_held"] = len(held)
        out[eng]["exact_status_ok"] = out[eng]["status"] == "error: " + EXPECTED_ERROR and out[eng]["button"] == "Send message" and out[eng]["message_kept"] == "Hang test."
        b.close()
print(json.dumps(out, indent=1))
