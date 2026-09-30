import { spawn } from 'child_process';

const PORT = 9241;
const PDIR = '/tmp/brave_test_capture_' + Date.now();
const EXTENSION_DIR = '/home/oh2fxd/toolbox/python/noai';

console.log('Testing with CDP console capture...');
const brave = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${PDIR}`,
  `--load-extension=${EXTENSION_DIR}`,
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-gpu',
  'https://www.youtube.com/results?search_query=dark+techno+ai'
], { stdio: 'ignore' });

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

setTimeout(async () => {
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    const page = list.find(t => t.type === 'page');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.method === 'Runtime.consoleAPICalled') {
        const text = d.params.args.map(a => a.value || a.description).join(' ');
        console.log('CONSOLE:', text);
      }
      if (d.method === 'Runtime.exceptionThrown') {
        console.log('EXCEPTION:', JSON.stringify(d.params.exceptionDetails));
      }
    });

    ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));
    await sleep(6000);

    ws.send(JSON.stringify({
      id: 2,
      method: 'Runtime.evaluate',
      params: {
        expression: `({
          total: document.querySelectorAll('ytd-video-renderer').length,
          hidden: document.querySelectorAll('.noai-hidden').length
        })`,
        returnByValue: true
      }
    }));

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 2) {
        console.log('Cards count:', d.result?.result?.value);
        brave.kill('SIGKILL');
        process.exit(0);
      }
    });
  } catch (err) {
    console.error(err);
    brave.kill('SIGKILL');
    process.exit(1);
  }
}, 2000);
