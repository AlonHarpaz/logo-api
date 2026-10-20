<picture><source media="(prefers-color-scheme: dark)" srcset="assets/logoapi-lo-inverse.svg"><img src="assets/logoapi-lo.svg" height="40" alt="LogoAPI"></picture>

Free, keyless logo API. One URL per domain.

Hosted at **[logoapi.sh](https://logoapi.sh)**. Try it: [logoapi.sh/stripe.com.svg](https://logoapi.sh/stripe.com.svg)

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
[![Tests](https://github.com/AlonHarpaz/logo-api/actions/workflows/tests.yml/badge.svg)](https://github.com/AlonHarpaz/logo-api/actions/workflows/tests.yml)

## Quick start

```html
<img src="https://logoapi.sh/stripe.com.svg" alt="Stripe" height="24">
```

```
curl https://logoapi.sh/github.com.svg
```

No API key. No signup.

## API

Base URL: `https://logoapi.sh`

| Path | Returns |
| --- | --- |
| `/<domain>.svg` | The wordmark. Falls back to the icon when a brand has no wordmark. |
| `/icon/<domain>.svg` | The square icon. Falls back to the wordmark when there is no icon. |
| `/index.json` | Every domain with its name, slug, files and source URL. |

- Unknown domains return `404` with the body `not found`. There is no placeholder image, so your own fallback can run.
- Domains are lowercase. A path with capitals gets a `301` to the lowercase path.
- Only `GET` and `HEAD` are allowed. Other methods return `405`.
- Every response sends `Access-Control-Allow-Origin: *`.
- SVGs are cached for a day: `Cache-Control: public, max-age=86400, stale-while-revalidate=604800`. `index.json` is cached for an hour.
- SVGs have no fixed width or height. They keep their `viewBox`, so size them with CSS or attributes.

## Examples

HTML, with your own fallback on 404:

```html
<img src="https://logoapi.sh/icon/acme.example.svg"
     alt="Acme" width="32" height="32"
     onerror="this.src='/img/generic-company.svg'">
```

React:

```jsx
function Logo({ domain, name }) {
  return (
    <img
      src={`https://logoapi.sh/${domain}.svg`}
      alt={name}
      height={24}
      onError={(e) => { e.currentTarget.src = "/img/generic-company.svg"; }}
    />
  );
}
```

curl and jq:

```
curl -s https://logoapi.sh/index.json | jq -r '.[] | select(.domain == "github.com") | .name'
curl -s https://logoapi.sh/index.json | jq 'length'
```

## Coverage

1,283 domains. Cloud, SaaS and open source tools are well covered. Banks and retail are thin.

The logos come from [gilbarbara/logos](https://github.com/gilbarbara/logos), pinned to one commit (`UPSTREAM_SHA` in `build.py`). To get a logo added, open a pull request upstream. It shows up here after the next bump.

## How it works

- `build.py` reads the upstream catalog. It writes one SVG per domain into `dist/`, plus `dist/index.json`. It uses only the Python standard library.
- It strips `width` and `height` from each SVG root and keeps the `viewBox`.
- There is no database and no server state.

## Self-host

Run `python3 build.py`, then serve `dist/` from any static host. Unknown paths must return 404. Run the tests with `python3 -m unittest discover tests`.

## Bumping the upstream

Run `gh api repos/gilbarbara/logos/commits/main --jq .sha`. Paste the result into `UPSTREAM_SHA` in `build.py`. Run the tests and `python3 build.py`, then commit. Downloads are cached per commit in `cache/<sha12>/`. A build with any download failure exits non-zero and leaves `dist/` unchanged.

## Takedown

If you own a mark and want it removed, [open a takedown issue](https://github.com/AlonHarpaz/logo-api/issues/new?template=takedown.yml) with the domain. To remove a domain, add it on its own line in `blocklist.txt` and rebuild. Lines starting with `#` are comments.

## License

The code is MIT. See `LICENSE`.

The logo files come from gilbarbara/logos and are CC0. Logos are trademarks of their owners. They are served for identification only.
