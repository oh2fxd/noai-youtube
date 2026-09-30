import { spawn } from 'child_process';

const brave = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  '--remote-debugging-port=9230',
  '--load-extension=/home/oh2fxd/toolbox/python/noai',
  '--user-data-dir=/tmp/brave_test_match_' + Date.now(),
  'https://www.youtube.com/results?search_query=dark+techno+ai'
], { stdio: 'ignore' });

setTimeout(async () => {
  try {
    const list = await (await fetch('http://127.0.0.1:9230/json/list')).json();
    const page = list.find(t => t.type === 'page' && t.url.includes('youtube'));
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 2) {
        console.log('DOM check:', JSON.stringify(d.result?.result?.value, null, 2));
      }
    });

    ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));

    setTimeout(() => {
      ws.send(JSON.stringify({
        id: 2,
        method: 'Runtime.evaluate',
        params: {
          expression: `(() => {
            const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
            return {
              total: cards.length,
              hiddenCount: document.querySelectorAll('.noai-hidden').length,
              badgeCount: document.querySelectorAll('.noai-badge').length,
              sampleCardClasses: cards[0] ? cards[0].className : 'none',
              firstTitle: cards[0] ? (cards[0].querySelector('#video-title') || {}).textContent : 'none'
            };
          })()`,
          returnByValue: true
        }
      }));
    }, 6000);

    setTimeout(() => {
      brave.kill('SIGKILL');
      process.exit(0);
    }, 8500);
  } catch (err) {
    console.error(err);
    brave.kill('SIGKILL');
  }
}, 2000);
