import { spawn } from 'child_process';

const brave = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  '--remote-debugging-port=9250',
  '--user-data-dir=/tmp/brave_inspect_thumb_' + Date.now(),
  'https://www.youtube.com/results?search_query=midjourney+sora+ai+music'
], { stdio: 'ignore' });

setTimeout(async () => {
  try {
    const list = await (await fetch('http://127.0.0.1:9250/json/list')).json();
    const page = list.find(t => t.type === 'page');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));
    ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));

    setTimeout(() => {
      ws.addEventListener('message', e => {
        const d = JSON.parse(e.data);
        if (d.id === 10) {
          console.log('Structure:', JSON.stringify(d.result?.result?.value, null, 2));
          brave.kill('SIGKILL');
          process.exit(0);
        }
      });
      ws.send(JSON.stringify({
        id: 10,
        method: 'Runtime.evaluate',
        params: {
          expression: `(() => {
            const card = document.querySelector('ytd-video-renderer');
            if (!card) return 'no card';
            const ytdThumb = card.querySelector('ytd-thumbnail');
            const aThumb = card.querySelector('a#thumbnail');
            const overlays = card.querySelector('#overlays');
            return {
              ytdThumbChildren: ytdThumb ? Array.from(ytdThumb.children).map(c => c.tagName + '#' + c.id) : [],
              aThumbChildren: aThumb ? Array.from(aThumb.children).map(c => c.tagName + '#' + c.id) : [],
              overlaysTag: overlays ? overlays.tagName : null,
              overlaysParent: overlays ? overlays.parentElement.tagName + '#' + overlays.parentElement.id : null
            };
          })()`,
          returnByValue: true
        }
      }));
    }, 4500);
  } catch (err) {
    console.error(err);
    brave.kill('SIGKILL');
  }
}, 2000);
