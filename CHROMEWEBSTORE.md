# Chrome Web Store & Brave Publishing Guide

This document is the single source of truth for publishing **NoAI for YouTube** to the Chrome Web Store (which also serves Brave users directly with 1-click installation).

---

## 1. Store Listing Details

### Extension Name (Max 45 chars)
```
NoAI for YouTube — Block & Tag AI Content
```

### Short Description / Summary (Max 132 chars)
```
Detects, tags, and hides AI-generated music, videos, and Shorts on YouTube. 1-click block AI content farms with zero tracking.
```

### Category
```
Productivity / Workflow & Planning  (or Accessibility)
```

### Detailed Description (Plain text formatted for Chrome Web Store)
```
Tired of AI-generated music, deepfakes, synthetic voiceovers, and automated content farms flooding your YouTube recommendations?

NoAI for YouTube cleans up your feed by automatically identifying, tagging, and optionally hiding synthetic media — returning YouTube to real, human creators.

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ KEY FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━

🏷️ PROMINENT AI BADGES
Instantly spots AI content and stamps a clear, high-contrast AI badge in the corner of video thumbnails across Home, Search, and Shorts.

🚫 1-CLICK CHANNEL BLOCKING
Permanently blacklist AI content farms with a single click. Blocked channels and their videos instantly disappear from your feed.

👁️ THREE FLEXIBLE DISPLAY MODES
• Tag Mode (Default): Shows prominent visual AI badges and 1-click block buttons while keeping content accessible.
• Hide Mode: Completely removes AI-flagged videos from your feed and preserves clean grid spacing.
• Blur Mode: Gently blurs thumbnails and dims AI video cards until you hover over them.

🛡️ MULTI-LAYER AI DETECTION ENGINE
• Official YouTube Disclosures: Catches YouTube's native "Altered or synthetic content" labels.
• Modern Model Signatures: Detects music and video generators including Suno (v3-v6), Udio, Sora, Runway Gen-3, Kling, Pika, Flux.1, Midjourney, ElevenLabs, RVC voice clones, and ChatGPT.
• Covert Content-Farm Heuristics: Identifies automated clickbait patterns and synthetic description formulas used by mass-produced music channels.
• Community Database: Built-in database of verified automated content farms.

🔒 ZERO TRACKING & COMPLETE PRIVACY
• 100% on-device processing.
• Zero analytics, zero telemetry, zero data collection.
• Operates exclusively on youtube.com with minimal permissions.

━━━━━━━━━━━━━━━━━━━━━━━━━━
☕ SUPPORT & SPONSORSHIP
━━━━━━━━━━━━━━━━━━━━━━━━━━
NoAI for YouTube is 100% free, privacy-focused, and open source with zero telemetry.
If this extension helps keep your feed clean, consider supporting ongoing maintenance:
• PayPal: https://www.paypal.com/paypalme/dxdroid
• GitHub Sponsors: https://github.com/sponsors/oh2fxd

Take back your recommendations and support authentic human creators with NoAI for YouTube.
```

---

## 2. Permissions Justification (For CWS Review Team)

The Chrome Web Store review team requires specific, plain-English justifications for all permissions:

### `storage`
> **Justification:** "Used exclusively to persist the user's chosen display preferences (Tag, Hide, or Blur), custom keyword filters, and the list of user-blocked YouTube channels locally on their device and across their synced browser sessions."

### `host_permissions: *://*.youtube.com/*`
> **Justification:** "Required solely to inspect video titles, channel names, and disclosure tags on YouTube pages in order to display the visual AI badges and 1-click channel block button."

---

## 3. Privacy & Data Use Disclosure (For Developer Dashboard)

In the **Privacy practices** tab of the Chrome Developer Dashboard, fill in:

1. **Single Purpose Description:**
   > "Detects, tags, and hides AI-generated videos, music, and Shorts on YouTube to help users find authentic human content."
2. **Data Collection Questions:**
   - Personally Identifiable Information: **NO**
   - Health Information: **NO**
   - Financial Information: **NO**
   - Authentication Information: **NO**
   - Personal Communications: **NO**
   - Location: **NO**
   - Web History: **NO**
   - User Activity: **NO**
   - Website Content: **NO** (The extension inspects public DOM elements locally and never transmits them).
3. **Data Usage Certifications:**
   - [x] Does not sell data to third parties.
   - [x] Does not use or transfer data for purposes unrelated to the single purpose.
   - [x] Does not use or transfer data to determine creditworthiness or for lending purposes.
4. **Privacy Policy Link:**
   Provide the URL to your hosted `PRIVACY.md` (e.g. on your GitHub repository).

---

## 4. Graphic Assets Specifications

| Asset | Dimensions | Requirement |
|-------|------------|-------------|
| Extension Icon | 128×128 px | Included in `/icons/icon-128.png` |
| Small Promo Tile (Optional) | 440×280 px | PNG format |
| Marquee Promo Tile (Optional) | 1400×560 px | PNG format |
| Screenshots | 1280×800 px or 640×400 px | At least 1 required (up to 5) |

---

## 5. Step-by-Step Store Submission Process

### Step 1: Register as a Chrome Web Store Developer
1. Go to the [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole).
2. Sign in with your Google account.
3. Pay the one-time $5 developer registration fee (mandated by Google for spam prevention).

### Step 2: Build the Upload ZIP
Run the automated packaging script in this directory:
```bash
python3 package_extension.py
```
This produces `youtube-noai-brave.zip` containing only the required production files (excluding git, tests, and documentation).

### Step 3: Upload and Submit
1. In the Chrome Developer Dashboard, click **New Item**.
2. Drag and drop `youtube-noai-brave.zip`.
3. Fill in the **Store Listing** fields using Section 1 of this document.
4. Upload at least 1 screenshot (1280×800) showing the extension in action on YouTube.
5. In the **Privacy** tab, enter the justifications from Section 2 & 3.
6. Click **Submit for Review**.
7. Google typically approves utility extensions within 24 to 72 hours.

### Step 4: Availability on Brave & Chrome
* Once published on the Chrome Web Store, **Brave users can install it directly with 1 click** from your Chrome Web Store listing — **no developer mode, no unzipping, and no manual loading required**.
* Updates are delivered automatically to all users in the background.
