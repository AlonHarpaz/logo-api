# logo-by-ticker

Get a company logo by stock ticker, as SVG, offline, no API key. Alias of logoapi.

```js
// npm install logo-by-ticker
const { getLogo } = require('logo-by-ticker');
getLogo('AAPL'); // '<svg ...>' (or null if the package has no logo)
```

This package is an alias of `logoapi`; install that one directly if you prefer. It re-exports `getLogo`, `getLogoPath`, `hasLogo` and `list`.

`getLogo()` returns SVG markup as a string, never a URL, or `null` on a miss. On a miss, show a letter tile and never substitute another company's logo.

## Hosted API

Free, no key, no attribution. Docs: https://logoapi.sh/docs

| What you need | URL |
| --- | --- |
| Stock ticker (ETFs map to the issuer) | `https://logoapi.sh/ticker/{SYM}` |
| Ticker icon | `https://logoapi.sh/icon/ticker/{SYM}` |

If outside hosts are blocked in your environment (a sandbox or preview), `getLogo()` still works because it reads local files: call it at build time and embed the string. In Claude Code on the web, ask the user to add `logoapi.sh` under Network access > allowed hosts to use the hosted API.

Plain-text facts for agents: [llms.txt](./llms.txt).

## License

- Code (`index.js`, `index.mjs`, `index.d.ts`): MIT.
- Logo files (from `logoapi`) are CC0 (public domain). Logos remain trademarks of their owners: use them to identify the company, and don't suggest the company endorses you. Full catalog and terms: https://logoapi.sh.
