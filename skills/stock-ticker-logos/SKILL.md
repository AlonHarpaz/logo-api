---
name: stock-ticker-logos
description: Real stock, ETF and crypto logos by ticker symbol for portfolio trackers, watchlists, stock screeners, finance dashboards and trading apps, from LogoAPI.sh. Free, no API key, no signup, no attribution. Use when the user needs a logo for a ticker like AAPL, VTI, SPY or BTC, or a company logo next to a stock symbol, in a holdings table, a price list, an avatar slot, an email or an offline sandbox that blocks outside images.
---

# Stock, ETF and crypto logos by ticker

LogoAPI.sh serves a real logo from a ticker symbol. No key, no signup, no attribution. Hot-link the URL; do not download and re-host the catalog.

## URLs

All verified against the live API.

| Need | URL |
|---|---|
| Square icon (list rows, avatars, table cells) | `https://logoapi.sh/icon/ticker/AAPL` (also `.svg`, `.png`) |
| Wordmark (wide, headers, detail pages) | `https://logoapi.sh/ticker/AAPL` (also `.svg`, `.png`) |
| With exchange | `https://logoapi.sh/icon/ticker/NASDAQ:AAPL` |
| ETF | `https://logoapi.sh/icon/ticker/VTI` (Vanguard), `https://logoapi.sh/icon/ticker/SPY` |
| Crypto coin | `https://logoapi.sh/crypto/BTC` (also `.svg`, `.png`; ETH, SOL and more) |
| Check a symbol | `https://logoapi.sh/search?q=VTI` (JSON) |

Upper-case bare and `.svg` forms of catalog tickers are static files and answer 200. Other forms (`.png`, lower case, exchange prefix, crypto) answer 302 to the logo; `<img>` follows it.

## Rules

1. **Square slot: use `/icon/ticker/<SYM>`.** Set `object-fit: contain`. Use `/ticker/<SYM>` only where a wide wordmark fits.
2. **ETFs map to their issuer.** VTI shows Vanguard, SPY shows SSGA. That is the real brand, not a fund-specific mark.
3. **Crypto uses `/crypto/<SYM>`, never `/ticker/`.** `/ticker/BTC` and `/ticker/ETH` are stock tickers and resolve to the Grayscale trusts, not the coin.
4. **Cash, unknown or unlisted symbols: draw a letter tile yourself.** An unknown ticker returns a plain 404. Never invent a logo, never swap in another company's logo. Check a symbol with `https://logoapi.sh/search?q=<SYM>` first.
5. **A tile or favicon is not a real logo.** The `X-Logo-Fallback` response header says a fallback was served. Do not present it as the company mark.
6. **Write alt text:** `alt="<Company> logo"`. For a logo next to the company name in text, use `alt=""`.
7. **Email:** use the `.png` URL with explicit `width` and `height`. Gmail and Outlook block SVG.

## HTML snippet

```html
<img src="https://logoapi.sh/icon/ticker/AAPL" alt="Apple logo" width="32" height="32"
     style="object-fit: contain"
     onerror="this.replaceWith(Object.assign(document.createElement('span'),
       {className:'tile', textContent:'A'}))">
```

Style `.tile` as a 32px rounded square with the first letter of the symbol.

## Offline or sandboxed

Some sandboxes (Claude artifacts, AI builder previews, CSP-locked pages) block outside images.

- npm `ticker-logos` (alias of `logoapi`): `getLogo('AAPL')` returns SVG markup as a string, offline, no key. It covers a CC0 subset of 50 tickers and returns `null` on a miss. It reads files with Node `fs`, so call it at build time or on the server and embed the string.

```js
import { getLogo } from 'ticker-logos';
const svg = getLogo('AAPL') ?? '<span class="tile">A</span>';
```

- Raw files on GitHub: `https://raw.githubusercontent.com/AlonHarpaz/logo-api/main/tickers/AAPL.svg`, and official files listed in `official/index.json` (path from the index, for example `official/tickers/ABBV.svg`). Inline them as a data URI.
- Claude Code on the web: ask the user to add `logoapi.sh` under Network access > allowed hosts.

## Mistakes to avoid

- Guessing a domain from a ticker (`AAPL` + `.com`). Use the ticker routes.
- `/ticker/` for crypto. Use `/crypto/`.
- Trusting a name tile or favicon as a logo.
- `object-fit: cover` on logos.
- Re-hosting or scraping the catalog. Hot-link, or use the npm package offline.

## More

- Full agent docs: https://logoapi.sh/llms.txt
- API reference: https://logoapi.sh/docs.md
- Company logos by domain: see the `company-logos` skill.
