# -*- coding: utf-8 -*-
"""
Dev helper: screenshot the demo after real wall-clock time has passed, using
the DevTools protocol over a live websocket connection to a persistent
headless Chrome.

Why this exists: --virtual-time-budget (the normal way to script a headless
screenshot) freezes CSS transition and animation timelines relative to
virtual time, so it cannot show whether a fade or transition actually
completes -- only whether the DOM is structurally correct at some instant.
This launches a real, running Chrome instead and waits in genuine wall-clock
time before capturing, so animations play out exactly as a viewer would see
them.

Usage:
    python dev_screenshot.py <url> <output.png> [wait_seconds] [WxH]

Requires the `websocket-client` package and a local Chrome install.
"""
import sys, json, time, base64, subprocess, urllib.request

url = sys.argv[1]
out = sys.argv[2]
wait_s = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
size = sys.argv[4] if len(sys.argv) > 4 else '1280,800'
port = 9333

proc = subprocess.Popen([
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "--headless=new", "--disable-gpu", "--hide-scrollbars",
    f"--remote-debugging-port={port}", f"--window-size={size}",
    "--remote-allow-origins=*",
    url,
])
try:
    # wait for devtools to come up and find our target
    target = None
    for _ in range(50):
        time.sleep(0.2)
        try:
            with urllib.request.urlopen(f"http://localhost:{port}/json") as r:
                targets = json.loads(r.read())
            target = next((t for t in targets if t.get('type') == 'page'), None)
            if target:
                break
        except Exception:
            continue
    if not target:
        raise SystemExit('no target found')

    import websocket
    ws = websocket.create_connection(target['webSocketDebuggerUrl'], timeout=10)

    def send(method, params=None, _id=[1]):
        _id[0] += 1
        ws.send(json.dumps({'id': _id[0], 'method': method, 'params': params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get('id') == _id[0]:
                return msg

    send('Page.enable')
    # real wall-clock wait: lets setTimeout/rAF/CSS transitions actually run
    time.sleep(wait_s)
    shot = send('Page.captureScreenshot', {'format': 'png'})
    data = base64.b64decode(shot['result']['data'])
    with open(out, 'wb') as f:
        f.write(data)
    print('wrote', out, len(data), 'bytes')
finally:
    proc.terminate()
