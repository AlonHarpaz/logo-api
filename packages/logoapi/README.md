# logoapi

Offline company and stock ticker logos as SVG. No key, no network, CC0 files, zero dependencies.

```js
// npm install logoapi
const { getLogo } = require('logoapi');
getLogo('AAPL'); // '<svg ...>' (or null if the package has no logo)
```

Bundles 1,174 domains and 50 stock tickers (2,016 CC0 SVG files). It is a subset: the hosted API at [logoapi.sh](https://logoapi.sh) covers 5,000+ more (see "Beyond this package").

## API

`getLogo()` returns SVG markup as a string, never a URL, or `null` on a miss. CommonJS and ESM, with types.

```js
import { getLogo, getLogoPath, hasLogo, list } from 'logoapi';

getLogo('AAPL');            // ticker, any case
getLogo('apple.com');       // domain; https://www.apple.com/ also works
getLogo('nope');            // null
hasLogo('stripe.com');      // true
getLogoPath('stripe.com');  // absolute path to the .svg, or null
list();                     // { domains: [...], tickers: [...] }
```

## Misses

When `getLogo()` returns `null`, show a letter tile (recipes below). Never guess or substitute another company's logo.

## Recipes

Portfolio tracker by ticker, with a letter tile when there is no logo:

```js
import { getLogo } from 'logoapi';

const tile = (sym) =>
  `<span class="tile">${sym.slice(0, 1).toUpperCase()}</span>`;
const row = (sym) =>
  `<li><span class="logo">${getLogo(sym) ?? tile(sym)}</span> ${sym}</li>`;

console.log(['AAPL', 'NVDA', 'ZZZZ'].map(row).join('\n'));
```

Company directory by domain (the package ships its list):

```js
import { getLogo, list } from 'logoapi';

const cards = list().domains.slice(0, 12)
  .map((d) => `<a href="https://${d}">${getLogo(d)}<span>${d}</span></a>`);
```

Sandboxed artifact or preview that blocks outside images: call `getLogo()` at build time (it reads files with Node `fs`, so not in browser code) and embed the string.

```js
import { writeFileSync } from 'node:fs';
import { getLogo } from 'logoapi';

writeFileSync('index.html',
  `<div class="logo">${getLogo('stripe.com') ?? ''}</div>`);
```

React component (server component or build step, keep `logoapi` external if you bundle for Node; the SVG comes from your own package, not user input):

```jsx
import { getLogo } from 'logoapi';

export function Logo({ id, size = 32 }) {
  const svg = getLogo(id);
  if (!svg) return <span className="tile" style={{ width: size, height: size }}>{id[0]?.toUpperCase()}</span>;
  return <span style={{ display: 'inline-block', width: size, height: size }} dangerouslySetInnerHTML={{ __html: svg }} />;
}
```

Dark mode: these files keep their original colours (none use `currentColor`), so CSS cannot recolour them. For white, black, grey or dark-background versions use the API variants below.

## Beyond this package

The API serves 5,000+ logos. Free, no key, no attribution. Docs: https://logoapi.sh/docs

| What you need | URL |
| --- | --- |
| Logo by domain | `https://logoapi.sh/{domain}.svg` |
| Square icon | `https://logoapi.sh/icon/{domain}.svg` |
| Stock ticker (ETFs map to the issuer) | `https://logoapi.sh/ticker/{SYM}` |
| Ticker icon | `https://logoapi.sh/icon/ticker/{SYM}` |
| PNG for email | `https://logoapi.sh/{domain}.png` |
| Favicon | `https://logoapi.sh/favicon/{domain}` |
| White, black, grey, dark | `https://logoapi.sh/{white\|black\|grey\|dark}/{domain}.svg` |
| Name to domain | `https://logoapi.sh/search?q=stripe` |
| MCP server | `https://logoapi.sh/mcp` |

If outside hosts are blocked in your environment, ask the user to allow `logoapi.sh`.

Plain-text facts for agents: [llms.txt](./llms.txt).

## License

- Code (`index.js`, `index.mjs`, `index.d.ts`): MIT, see `LICENSE-MIT`.
- Files in this package are CC0 (public domain). Logos remain trademarks of their owners: use them to identify the company, and don't suggest the company endorses you. Full catalog and terms: https://logoapi.sh.
