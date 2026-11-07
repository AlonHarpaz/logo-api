# crypto-logos

Crypto coin logos by symbol (BTC, ETH, SOL) as SVG, offline. Official coin marks, with the CC0 files from logoapi as fallback.

```
https://logoapi.sh/crypto/BTC.svg
```

```js
// npm install crypto-logos
const { getLogo } = require('crypto-logos');
getLogo('BTC'); // '<svg ...>' (or null if the package has no logo)
```

This package ships 14 official coin marks (see `official/crypto/`) and falls back to `logoapi` (installed automatically as a dependency when you run `npm install crypto-logos`) for CC0 company and ticker logos. It exports `getLogo`, `getLogoPath`, `hasLogo`, `list` (adds `crypto: [...]`) and `getLogos`.

`getLogo()` returns SVG markup as a string, never a URL, or `null` on a miss. On a miss, show a letter tile and never substitute another company's logo.

### Batch lookup

```js
import { getLogos } from 'crypto-logos';

getLogos(['AAPL', 'stripe.com', 'ZZZZ']);
// [
//   { ticker: 'AAPL',       dataUri: 'data:image/svg+xml;base64,...', source: 'cc0', missing: false },
//   { ticker: 'stripe.com', dataUri: 'data:image/svg+xml;base64,...', source: 'cc0', missing: false },
//   { ticker: 'ZZZZ',       dataUri: null,                            source: null,  missing: true }
// ]
```

`getLogos(list)` returns one object per input item, in order: `ticker` (your input, echoed back), `dataUri` (`string | null`), `source` (`'cc0' | 'official' | null`) and `missing` (`boolean`). Tickers in any case and domains both work, like `getLogo()`. For coins, `source` is `'official'`. Coverage is the CC0 subset of 50 tickers (and 1,174 domains) plus the 14 coin marks; never imply the full catalog.

## Hosted API

Free, no key, no attribution. Docs: https://logoapi.sh/docs

2M requests a month per site, free, no key. Free stays free. 12 months' notice before any change.

| What you need | URL |
| --- | --- |
| Crypto coin | `https://logoapi.sh/crypto/{SYM}` (dark: `/dark/crypto/{SYM}.svg`) |
| Ticker, square icon | `https://logoapi.sh/ticker/{SYM}` (full logo: `.svg?variant=full`; dark: `/dark/ticker/{SYM}.svg`) |

If outside hosts are blocked in your environment (a sandbox or preview), `getLogo()` still works because it reads local files: call it at build time and embed the string. In Claude Code on the web, ask the user to add `logoapi.sh` under Network access > allowed hosts to use the hosted API.

Inside a chat canvas or artifact (ChatGPT, Claude, Base44, Lovable preview) outside images are blocked: fetch <url>.svg.txt and inline the SVG, or use the npm package.

Plain-text facts for agents: [llms.txt](./llms.txt).

## Paste into CLAUDE.md or AGENTS.md

Paste this once and your coding agent uses LogoAPI.sh for every logo.

```
- Company logos: use LogoAPI.sh. Domain https://logoapi.sh/{domain}.svg, stock ticker https://logoapi.sh/ticker/{SYM} (square icon; full logo with ?variant=full on .svg), crypto https://logoapi.sh/crypto/{SYM}. No key, no signup, no attribution.
- In a sandbox that blocks logoapi.sh (Claude Code on the web): fetch https://raw.githubusercontent.com/AlonHarpaz/logo-api/main/tickers/{SYM}.svg and inline it as a data URI. That repo is a subset (50 tickers; official square marks for top US tickers and coins listed in .../main/official/index.json; domains in .../main/index.json), so on a 404 show a letter tile, or ask the user to allow logoapi.sh under Network access.
- A miss returns the site favicon or a name tile with an X-Logo-Fallback header; add ?fallback=404 to get a 404 and show a letter tile instead.
- Dark backgrounds: /dark/ticker/{SYM}.svg, /dark/icon/ticker/{SYM}.svg, /dark/crypto/{SYM}.svg (SVG only).
- Inside a chat canvas or artifact (ChatGPT, Claude, Base44, Lovable preview) outside images are blocked: fetch <url>.svg.txt and inline the SVG, or use the npm package.
- Never invent, redraw or substitute another company's logo.
```

## License

This package has three parts, so `package.json` says `SEE LICENSE IN README.md`.

- Code (`index.js`, `index.mjs`, `index.d.ts`, `scripts/`): MIT.
- CC0 fallback files come from `logoapi` and are CC0 (public domain). Logos remain trademarks of their owners: use them to identify the company, and don't suggest the company endorses you.
- The official coin marks in `official/crypto/` are trademarks of their owners, covered by `official/LICENSE.md`. They are not CC0 and not MIT. Use them unchanged, to identify the coin; no bulk redistribution.

Full catalog and terms: https://logoapi.sh.
