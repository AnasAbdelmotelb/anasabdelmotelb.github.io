# Turns a results.json written by break_tests.py into a short Markdown summary (summary.md next to it).
# Usage: python summarize.py RESULTS_JSON
import json, sys
from pathlib import Path

src = Path(sys.argv[1])
d = json.loads(src.read_text())
engines = list(d["engines"])
lines = [f"# Results for {d['base_url']} ({d['run_at_utc']})", "",
         "Engines: " + ", ".join(f"{e} {d['engines'][e]['version']}" for e in engines), "",
         "## Contact form (Formspree mocked, nothing sent)", "",
         "| Case | " + " | ".join(engines) + " |", "|---|" + "---|" * len(engines)]


def cell(f):
    parts = [f"{f['requests_sent']} req"]
    w = f.get("state_while_in_flight")
    if isinstance(w, dict):
        parts.append(f"in flight: {'disabled' if w['disabled'] else 'ENABLED'} '{w['text']}'")
    if f.get("result"):
        parts.append(f["result"])
    elif f.get("status"):
        parts.append(f["status"].split(":")[0])
    elif f.get("invalid"):
        parts.append("blocked: " + f["invalid"][0][:60].replace("|", "/"))
    if "exact_status_ok" in f:
        parts.append("exact text " + ("OK" if f["exact_status_ok"] else "MISMATCH"))
    if f.get("dialogs"):
        parts.append("DIALOG " + str(f["dialogs"]))
    if f.get("page_errors"):
        parts.append("JS ERROR")
    return "; ".join(parts)


for i, f in enumerate(d["engines"][engines[0]]["form"]):
    lines.append(f"| {f['case']} | " + " | ".join(cell(d["engines"][e]["form"][i]) for e in engines) + " |")

lines += ["", "## Honeypot (`_gotcha`)", ""]
for e in engines:
    h = d["engines"][e]["honeypot"]
    lines.append(f"- {e}: display={h['wrapper_display']}, aria-hidden={h['aria_hidden']}, tabindex={h['tabindex']}, "
                 f"reached by Tab: {h['honeypot_focused']}")

lines += ["", "## Pages", "", "| Engine | Viewport | Path | Status | h1 | Heading skips | Overflow px | Console errors/warnings | Page errors | robots | canonical |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
for e in engines:
    for p in d["engines"][e]["pages"]:
        lines.append(f"| {e} | {p['viewport']} | {p['path']} | {p['status']} | {p['h1_count']} | {', '.join(p['heading_skips']) or '-'} | "
                     f"{p['horizontal_overflow_px']} | {'; '.join(p['console']) or '-'} | {'; '.join(p['page_errors']) or '-'} | {p['robots'] or '-'} | {p['canonical'] or '-'} |")

lines += ["", "## Keyboard", ""]
for e in engines:
    k = d["engines"][e]["keyboard"]
    order = " → ".join(t["text"] for t in k["tab_order_first_14"])
    no_outline = [t["text"] for t in k["tab_order_first_14"] if not t["outline"]]
    lines.append(f"- {e}: Tab order: {order}. Without a visible outline: {no_outline or 'none'}. "
                 f"Skip link + Enter: {k['skip_link_enter']}. Nav 'Contact' + Enter: {k['nav_contact_enter']}.")

m = d["mobile_device"]
lines += ["", "## Mobile device profile", "", f"- {m['device']}: horizontal overflow {m['overflow']} px; targets under 24 px on one side: {m['small_targets']}"]
(src.parent / "summary.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
