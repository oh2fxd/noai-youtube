# Privacy Policy for NoAI for YouTube

**Last updated:** September 30, 2026

## 1. Overview
NoAI for YouTube ("the Extension") is committed to protecting your privacy. This extension operates entirely locally within your browser.

## 2. Data Collection
**NoAI for YouTube does not collect, transmit, sell, or monetize any personal data, browsing history, or user information.**

- **No Personal Information**: We do not collect names, email addresses, IP addresses, or device identifiers.
- **No Browsing Activity**: We do not track websites you visit, search queries you make, or videos you watch.
- **No External Servers**: The extension communicates with zero external servers, third-party analytics, or tracking services.

## 3. Data Storage
All data managed by the Extension is stored locally on your device via standard browser storage APIs (`chrome.storage.sync` / `chrome.storage.local`):
- **User Preferences**: Your chosen display mode (Tag, Hide, Blur), keyword filters, and toggle settings.
- **Custom Blocklist**: The names and handles of YouTube channels you choose to block.

If you have browser synchronization enabled (e.g. Brave Sync or Google Account Sync), your preferences sync exclusively through your browser's encrypted sync service.

## 4. Permissions
The extension requests only the minimum permissions required for core functionality:
- `storage`: Required to save your settings and custom channel blocklist locally.
- Host Permission (`*://*.youtube.com/*`): Required to inspect video titles, channel names, and disclosure tags on YouTube to display AI badges and block buttons.

## 5. Third-Party Services
The Extension does not integrate any third-party advertising, analytics, or remote scripts.

## 6. Contact & Open Source
For inquiries, bug reports, or questions regarding this Privacy Policy, please open an issue in the project repository.
