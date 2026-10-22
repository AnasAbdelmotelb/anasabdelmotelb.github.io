import json, subprocess, sys
from pathlib import Path
repo = Path.cwd()
out = Path('/private/tmp/flyrank-negative-controls')
out.mkdir(exist_ok=True)
records = []
for name, args in [('break_tests.py', ['http://127.0.0.1:4321', str(out/'break-results')]), ('hang_test.py', ['http://127.0.0.1:4321', '20'])]:
    source = (repo/'evidence/week-7/scripts'/name).read_text()
    old = 'EXPECTED_ERROR = "Sorry, I couldn\'t send your message. Please try again, or contact me through Book a Call or LinkedIn."'
    assert old in source
    source = source.replace(old, 'EXPECTED_ERROR = "INTENTIONALLY WRONG NEGATIVE CONTROL"')
    if name == 'break_tests.py':
        source = source.replace('ENGINES = ("chromium", "firefox", "webkit")', 'ENGINES = ("chromium",)')
    path = out/name
    path.write_text(source)
    result = subprocess.run([sys.executable, str(path), *args], text=True, capture_output=True)
    (out/(name+'.stdout')).write_text(result.stdout)
    (out/(name+'.stderr')).write_text(result.stderr)
    record = {'script': name, 'mutation': 'EXPECTED_ERROR intentionally wrong; production files unchanged', 'exit_code': result.returncode, 'assertion_error': 'AssertionError' in result.stderr}
    records.append(record)
    print(json.dumps(record), flush=True)
    assert result.returncode != 0 and record['assertion_error'], record
(out/'results.json').write_text(json.dumps(records, indent=2)+'\n')
