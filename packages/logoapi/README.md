`npm install logoapi` then `const { getLogo } = require('logoapi'); getLogo('AAPL')` returns the Apple logo as an SVG string.

Company and stock ticker logos as SVG files in your project. Free, no key, no network call, zero dependencies. CommonJS and ESM, with types.

```js
import { getLogo, getLogoPath, hasLogo, list } from 'logoapi';

getLogo('AAPL');            // '<svg ...>' (ticker, any case)
getLogo('apple.com');       // '<svg ...>' (domain; https://www.apple.com/ also works)
getLogo('nope');            // null
hasLogo('stripe.com');      // true
getLogoPath('stripe.com');  // absolute path to the .svg, or null
list();                     // { domains: [...], tickers: [...] }
```

## In a sandboxed artifact or preview

Some sandboxes block outside images, so a `https://logoapi.sh/...` `<img>` will not load. `getLogo()` returns the SVG as a string, so you can inline it with no network request:

```js
document.querySelector('#logo').innerHTML = getLogo('stripe.com') ?? '';
```

## What is in this package

- 2,016 SVG files from [gilbarbara/logos](https://github.com/gilbarbara/logos), dedicated to the public domain under CC0. Only CC0 files are included.
- 1,174 domains and 50 stock tickers map to those files (several domains can share one file). Names are slugs, so always look logos up through `getLogo()` or `list()`.
- It is a subset. The package does not cover every company, so check `hasLogo()` and fall back to the API below.

## The full catalog

The API at [logoapi.sh](https://logoapi.sh) serves 5,000+ logos, tickers and crypto, with wordmarks, icons, colour variants and PNG. Free, no key, no attribution required.

| What you need | URL |
| --- | --- |
| Wordmark logo | `https://logoapi.sh/{domain}.svg` |
| Square icon | `https://logoapi.sh/icon/{domain}.svg` |
| Stock ticker | `https://logoapi.sh/ticker/{SYM}` |
| Ticker icon (PNG) | `https://logoapi.sh/icon/ticker/{SYM}` |
| Favicon | `https://logoapi.sh/favicon/{domain}` |
| White, black, grey, dark mode | `https://logoapi.sh/{white\|black\|grey\|dark}/{domain}.svg` |
| Name to domain | `https://logoapi.sh/search?q=stripe` |

Docs: https://logoapi.sh/docs

## License

Logos are trademarks of their owners. You may show them, free and with no attribution, to identify a company in your site or app, including saving a few files into your project. Don't change them, don't suggest the company endorses you, and don't redistribute the catalog in bulk. Files in `logos/` in this repo are CC0. Full terms: https://logoapi.sh/terms.

Logo files: CC0 1.0 (`LICENSE`). Code (`index.js`, `index.mjs`, `index.d.ts`): MIT (`LICENSE-MIT`).
