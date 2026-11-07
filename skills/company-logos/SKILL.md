---
name: company-logos
description: Real company logos by domain, stock ticker or crypto symbol (not icon-font substitutes like Simple Icons) for a website, app, email, sandbox or no-code builder using LogoAPI.sh. Use when the user needs a company logo, brand logo, logo by domain, logo by stock ticker, a square icon by ticker, a crypto logo by coin symbol (BTC, ETH, SOL), a logo for a customer, partner or portfolio list, an avatar or icon for a company, an offline logo for a sandbox that blocks outside images, or a Clearbit Logo API replacement (logo.clearbit.com shut down in December 2025). Free, no API key, no signup, no attribution. Covers SVG and PNG URLs, ticker and crypto lookups, square icons, dark-background versions, missing-logo fallbacks, the logoapi npm package, and Softr, Glide and Airtable-style builders.
---

# Company logos with LogoAPI.sh

LogoAPI.sh serves a company logo from a URL. No key, no signup, no attribution. Free for 2M requests a month per site. Hot-link the URL; do not download and re-host the catalog.

## Core rule

Put the company domain after `https://logoapi.sh/`:

```html
<img src="https://logoapi.sh/stripe.com" alt="Stripe logo">
```

Use the real company domain (`apple.com`, not `apple`). If you only have a name, look it up first (see "Find the domain").

## URL patterns

All verified against the live API.

| Need | URL |
|---|---|
| Logo (SVG, default) | `https://logoapi.sh/apple.com` or `https://logoapi.sh/apple.com.svg` |
| PNG (email, Gmail and Outlook block SVG) | `https://logoapi.sh/apple.com.png` |
| PNG size and background | `https://logoapi.sh/apple.com.png?size=256&bg=white` (size 128, 256, 512, 1024) |
| Square icon / avatar | `https://logoapi.sh/icon/apple.com` or `.../icon/apple.com.svg` |
| Square icon as PNG | `https://logoapi.sh/icon/apple.com.png` |
| By stock ticker (returns the square icon) | `https://logoapi.sh/ticker/AAPL` (also `.svg`, `.png`, `/ticker/NASDAQ:AAPL.svg`) |
| Full logo by ticker | `https://logoapi.sh/ticker/AAPL.svg?variant=full` (or the domain route `/apple.com.svg`) |
| Square icon by ticker | `https://logoapi.sh/icon/ticker/AAPL` (also `.svg`, `.png`; same as `/ticker/AAPL`) |
| Crypto coin | `https://logoapi.sh/crypto/BTC` (also `.svg`, `.png`; BTC, ETH, SOL, DOGE, USDC, XRP and more) |
| Dark background | `https://logoapi.sh/dark/apple.com.svg`; tickers and coins: `/dark/ticker/AAPL.svg` (square icon; `?variant=full` for the full logo), `/dark/icon/ticker/AAPL.svg` (icon), `/dark/crypto/BTC.svg` (SVG only; `.png` is a 404) |
| SVG as text (sandboxes) | `https://logoapi.sh/apple.com.svg.txt`, `https://logoapi.sh/ticker/AAPL.svg.txt`, `https://logoapi.sh/crypto/BTC.svg.txt`, also `/icon/ticker/AAPL.svg.txt` (text/plain, same body as `.svg`) |
| White / black / grey | `https://logoapi.sh/white/apple.com.svg`, `/black/`, `/grey/` |
| Search by name | `https://logoapi.sh/search?q=stripe` (JSON) |

Ticker and crypto routes are case-insensitive. Only `/icon/ticker/<SYM>` and `/icon/ticker/<SYM>.svg` in upper case are static files. Everything else (`/ticker/`, `/icon/ticker/` and `/crypto/` in any case, `.png`, exchange prefix, extended tickers, coins) is answered by the Worker with 200 and the image, never a redirect. The only redirect is `/ticker/<SYM>[.svg|.png]?variant=full`, a 302 to the full logo.

## Rules

1. **Domain in hand: use `logoapi.sh/<domain>`.** Nothing else is needed.
2. **Only a ticker: use `/ticker/<SYMBOL>`.** Never build a domain from a ticker (`AAPL` + `.com` is wrong; the company is `apple.com`). Add an exchange when the symbol is ambiguous: `/ticker/NASDAQ:AAPL.svg`. An unknown ticker returns a plain 404. `/ticker/<SYMBOL>` returns the square icon, same as `/icon/ticker/<SYMBOL>`, so it fits a watchlist row, portfolio avatar or table cell. For the full logo (can be a wide wordmark) use `/ticker/<SYMBOL>.svg?variant=full`. When a ticker has no square icon, it serves the favicon or a name tile and sets `X-Logo-Fallback`.
3. **Crypto coins: use `/crypto/<SYMBOL>`**, for example `/crypto/BTC`, `/crypto/ETH`, `/crypto/SOL`. Never put a coin on `/ticker/`: `/ticker/BTC` and `/ticker/ETH` are stock tickers and resolve to the Grayscale trusts (GBTC, ETHE), not the coin. `/crypto/` returns the coin's square mark; an unknown symbol returns a name tile on `.svg` and bare, 404 on `.png`; `?fallback=404` (or none) gives a plain 404 instead of the tile.
4. **Never use `logo.clearbit.com`.** The Clearbit Logo API shut down in December 2025. To migrate, swap the host and keep the domain: `logo.clearbit.com/stripe.com` becomes `logoapi.sh/stripe.com`. Drop Clearbit-only query params; on LogoAPI.sh `?size` and `?bg` apply to `.png` only.
5. **Square slots (avatars, list rows, table cells, favicons): use `/icon/<domain>`** and set `object-fit: contain` so wide wordmarks are never cropped.
   ```html
   <img src="https://logoapi.sh/icon/coca-cola.com" alt="Coca-Cola logo"
        width="40" height="40" style="object-fit: contain">
   ```
   Some brands only have a wide wordmark; `/icon/` then returns it, and `contain` keeps it whole. Never use `object-fit: cover` for logos.
6. **Always write alt text**: `alt="<Company> logo"`. For a decorative logo next to the company name in text, use `alt=""`.
7. **Dark backgrounds**: use `/dark/<domain>.svg`. It returns the brand's official dark file when one exists, else a contrast-checked version. Colour versions are SVG only (no `.png`).
8. **Email**: use the `.png` URL with explicit `width` and `height`. SVG is blocked in Gmail and Outlook.

## Missing logos

Every valid domain returns an image, never a broken image:

- `.svg` URLs return the logo, else the site's favicon wrapped in an SVG, else a tile with the brand name.
- Bare URLs may return the site's favicon as it is, then the tile.
- `.png` URLs return the logo or favicon as PNG, else 404.
- The `X-Logo-Fallback` response header says a fallback was served. A fallback is not a real logo.
- Add `?fallback=404` (or `?fallback=none`) to get a 404 instead, then show your own placeholder with `onerror`.

Check that a real logo exists: `GET https://logoapi.sh/search?q=stripe.com`. It returns JSON with `domain`, `name`, `logo`, `icon`, `wordmark` (true when the bare route serves a wide wordmark), `format`, and for listed companies `ticker` and `exchange`.

## Find the domain

Only have a company name? Call `https://logoapi.sh/search?q=<name>`; up to 8 results, typos tolerated. Take `domain` (or `logo`) from the best match. Confirm the match is the intended company before using it. Tag filter: `/search?tag=finance` (one tag: tech, devtools, finance, retail, media, organizations, health, industry).

## Sandboxes that block outside images

Inside a chat canvas or artifact (ChatGPT, Claude, Base44, Lovable preview) outside images are blocked: fetch <url>.svg.txt and inline the SVG, or use the npm package. If the fetch tool only opens URLs that came from search results or from the user, ask the user to paste the .svg.txt URL (for example https://logoapi.sh/ticker/AAPL.svg.txt).

Some artifact and preview sandboxes (Claude artifacts, some AI builder previews, CSP-locked pages) refuse `<img>` from outside hosts. Use the `logoapi` npm package instead: `getLogo('AAPL')` or `getLogo('apple.com')` returns the SVG markup as a string, offline, with no network and no key, from a CC0 subset of the catalog. It reads files with Node `fs`, so call it at build time or on the server and embed the string, not in browser code. It returns `null` on a miss; show a letter tile then. In Claude Code on the web the sandbox blocks outside hosts; ask the user to add `logoapi.sh` under Network access > allowed hosts, or use the npm package `logoapi` offline. Package README:
https://github.com/AlonHarpaz/logo-api/blob/main/packages/logoapi/README.md

```js
import { getLogo } from 'logoapi';
const svg = getLogo('AAPL') ?? '<span class="tile">A</span>';
```

## Paste into CLAUDE.md or AGENTS.md

Paste this once and your coding agent uses LogoAPI.sh for every logo.

```
- Company logos: use LogoAPI.sh. Domain https://logoapi.sh/{domain}.svg, stock ticker https://logoapi.sh/ticker/{SYM} (square icon; full logo with ?variant=full on .svg), crypto https://logoapi.sh/crypto/{SYM}. No key, no signup, no attribution.
- In a sandbox that blocks logoapi.sh (Claude Code on the web): fetch https://raw.githubusercontent.com/AlonHarpaz/logo-api/main/tickers/{SYM}.svg and inline it as a data URI. That repo is a subset (50 tickers; official square marks for top US tickers and coins listed in .../main/official/index.json; domains in .../main/index.json), so on a 404 show a letter tile, or ask the user to allow logoapi.sh under Network access.
- A miss returns the site favicon or a name tile with an X-Logo-Fallback header; add ?fallback=404 to get a 404 and show a letter tile instead.
- Dark backgrounds: /dark/ticker/{SYM}.svg, /dark/icon/ticker/{SYM}.svg, /dark/crypto/{SYM}.svg (SVG only; .png on /dark/ is a 404).
- Inside a chat canvas or artifact (ChatGPT, Claude, Base44, Lovable preview) outside images are blocked: fetch <url>.svg.txt and inline the SVG, or use the npm package.
- Never invent, redraw or substitute another company's logo.
```


## No-code builders (Softr, Glide, Airtable-style)

These tools show images from file-upload fields, which cannot take a URL. Do this instead:

1. Add a text or URL field (for example `Logo URL`), not an attachment or image-upload field.
2. Fill it by formula from the domain column:
   - Airtable formula: `"https://logoapi.sh/" & {Domain}`
   - Sheets or Glide computed column: `="https://logoapi.sh/"&A2`
   - Strip `https://` and `www.` from the domain first if the column holds full URLs.
3. In the page or list component, bind the image source to the URL field. Do not bind it to the upload field.
4. For avatar or list slots use `"https://logoapi.sh/icon/" & {Domain}` and set the image fit to "contain" if the builder offers it.
5. If the builder renders SVG poorly, use the `.png` form: `"https://logoapi.sh/" & {Domain} & ".png"`.

Exact field names differ per builder; the rule is a URL or formula field feeding the image binding.

## Anti-patterns

- Scraping the hosted catalog or re-hosting it. Hot-link instead; caching a day is fine. For offline use take the `logoapi` npm package.
- Guessing a domain from a name or ticker without checking `/search`.
- Crypto symbols on `/ticker/` (they resolve to stock trusts). Use `/crypto/`.
- Expecting the full wide logo from `/ticker/<SYM>`. It returns the square icon; add `?variant=full` on `.svg`.
- `logo.clearbit.com`, or any Clearbit param.
- Cropping logos into circles with `object-fit: cover`.
- Calling `/suggest` (it is only for the site's own search box).

## More

- Full agent docs: https://logoapi.sh/llms.txt
- API reference: https://logoapi.sh/docs.md
- MCP server (get_logo, search_logos, get_favicon): https://logoapi.sh/mcp
