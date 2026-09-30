# NoAI for YouTube (Brave & Chrome Extension)

An ultra-lightweight, privacy-first Manifest V3 browser extension for Brave and Google Chrome that detects, tags, and hides AI-generated videos, synthetic music, deepfakes, and automated content farms on YouTube.

---

## ⚡ Key Highlights

- **Prominent Visual AI Badges**: High-contrast vector badge stamped on video thumbnails in feeds, search results, and Shorts.
- **1-Click Channel Blocking**: Click `[🚫 Block Channel]` right beside the video title to permanently blacklist the channel and instantly remove all its videos.
- **Advanced Multi-Signal Heuristic Engine**: Spots covert AI music farms that try to hide by detecting automated title templates, clickbait setting cliches, and ChatGPT promotional bio formulas.
- **Official YouTube Synthetic Media Detection**: Seamlessly flags YouTube's native *"Altered or synthetic content"* disclosures.
- **Modern 2024–2026 AI Coverage**: Pre-loaded signatures for Suno (v3–v6), Udio, Sora, Runway Gen-3, Kling, Pika, Flux.1, Midjourney, ElevenLabs, celebrity RVC voice clones, and ChatGPT.
- **Zero Tracking & 100% On-Device**: Zero external network requests, zero telemetry, zero analytics. Works entirely locally on your machine.

---

## 🚀 Installation

### Option 1: Chrome Web Store (Recommended for General Users)
> *Brave is built on Chromium and natively uses the Chrome Web Store. No developer mode is required once installed from the store.*
1. Visit the extension page on the Chrome Web Store (see [CHROMEWEBSTORE.md](file:///home/oh2fxd/toolbox/python/noai/CHROMEWEBSTORE.md) for publishing status).
2. Click **Add to Brave** (or **Add to Chrome**).
3. Confirm the prompt — the extension will install and update automatically.

---

### Option 2: Unpacked / Developer Mode (For Testing & Sharing `.zip`)
1. Download or unzip `youtube-noai-brave.zip` into a local folder (e.g. `youtube-noai`).
2. Open Brave or Chrome and navigate to:
   ```
   brave://extensions/   (or chrome://extensions/)
   ```
3. Enable **Developer mode** toggle in the top-right corner.
4. Click **Load unpacked** (top-left) and select the extracted `youtube-noai` folder containing `manifest.json`.
5. Pin the **NoAI** puzzle piece icon in your browser toolbar for quick settings access.

---

## 🛠️ Display Modes

From the popup settings menu, you can select your preferred action:
* **🏷️ Tag Mode (Default)**: Displays prominent AI vector badges on thumbnails and adds a `[🚫 Block Channel]` button next to the title.
* **🚫 Hide Mode**: Automatically collapses and removes AI content from your feed while preserving grid spacing.
* **👁️ Blur Mode**: Blurs thumbnails and dims AI video cards until you hover over them.

---

## 🔒 Security & Privacy

* **Strict Minimum Privileges**: Only requests `storage` and host permission for `*://*.youtube.com/*`.
* **Zero Remote Scripts / No Eval**: Compliant with strict Manifest V3 Content Security Policy (CSP).
* **Safe DOM Manipulation**: All injected elements use safe native DOM APIs and inline vector SVGs without `innerHTML` interpolation of external data.
* **Full Privacy Policy**: Detailed in [PRIVACY.md](file:///home/oh2fxd/toolbox/python/noai/PRIVACY.md).

---

## 📦 Building & Packaging

To create a clean distribution ZIP excluding development files:
```bash
python3 package_extension.py
```
This generates `youtube-noai-brave.zip` ready for store submission or sharing.

---

## ☕ Support & Donations

NoAI for YouTube is 100% free and open-source. If you find this extension helpful in keeping your feed free of automated AI content:

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-00457C?style=flat&logo=paypal)](https://www.paypal.com/paypalme/dxdroid)

[Donate via PayPal (paypal.me/dxdroid)](https://www.paypal.com/paypalme/dxdroid) — 73 de OH2FXD
