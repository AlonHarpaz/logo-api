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
| `/index.json` | Every domain with its name, slug, files, source URL and `origin`. |

Simple Icons entries are single-color icons. They have the brand color set as `fill` on the root `<svg>`, and `/<domain>.svg` returns the same icon as `/icon/<domain>.svg`. Their index entries also carry `hex` and, when the icon has one, `license`.

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

3,296 domains: 1,283 from gilbarbara/logos and 2,013 from simple-icons. Cloud, SaaS and open source tools are well covered. Banks and retail are thin.

The logos come from two sources, each pinned to one commit in `build.py`:

- [gilbarbara/logos](https://github.com/gilbarbara/logos) (`UPSTREAM_SHA`). Wordmarks and icons. It wins when both sources have a domain.
- [simple-icons](https://github.com/simple-icons/simple-icons) (`SI_SHA`). Icons only. The domain is the host of each icon's `source` URL. An icon is dropped when that host is a code or wiki host (`CODE_WIKI_HOSTS`, for example github.com or wikipedia.org), when more than one icon maps to the same host, or when its license is `custom`.

Every `index.json` entry has `origin`: `gilbarbara` or `simple-icons`. To get a logo added, open a pull request upstream. It shows up here after the next bump.

## How it works

- `build.py` reads both upstream catalogs. It writes one SVG per domain into `dist/`, plus `dist/index.json`. It uses only the Python standard library.
- It strips `width` and `height` from each SVG root and keeps the `viewBox`.
- There is no database and no server state.

## Self-host

Run `python3 build.py`, then serve `dist/` from any static host. Unknown paths must return 404. Run the tests with `python3 -m unittest discover tests`.

## Bumping the upstream

For gilbarbara, run `gh api repos/gilbarbara/logos/commits/main --jq .sha` and paste the result into `UPSTREAM_SHA` in `build.py`. For simple-icons, run `gh api repos/simple-icons/simple-icons/commits/develop --jq .sha` and paste it into `SI_SHA`. Run the tests and `python3 build.py`, then commit. Downloads are cached per commit in `cache/<sha12>/` and `cache/si-<sha12>/`. A build with any download failure exits non-zero and leaves `dist/` unchanged.

## Takedown

If you own a mark and want it removed, [open a takedown issue](https://github.com/AlonHarpaz/logo-api/issues/new?template=takedown.yml) with the domain. To remove a domain, add it on its own line in `blocklist.txt` and rebuild. Lines starting with `#` are comments.

## License

The code is MIT. See `LICENSE`.

The gilbarbara/logos files are CC0. The simple-icons files are CC0 as a collection, but a few icons carry their own license, shown as `license` in `index.json` (icons with a `custom` license are not included). Logos are trademarks of their owners. They are served for identification only.
