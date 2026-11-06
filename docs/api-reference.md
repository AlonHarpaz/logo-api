Canonical: https://logoapi.sh/docs
Synced from the site build on 2026-11-07; do not edit here.

# LogoAPI.sh API reference: logo, icon, favicon and search endpoints

Canonical page: https://logoapi.sh/docs
Updated: 2026-11-03

LogoAPI.sh returns any company's logo from its domain: `https://logoapi.sh/stripe.com`. Free, no key.

Everything LogoAPI.sh does today, with real examples. Every route is a plain GET.

## Quick start

**No key, no signup, no attribution. Commercial use included.** Copy this tag, swap the domain, done.

Every fallback says so in the `X-Logo-Fallback` response header, or add `?fallback=404` to get a 404 instead.

```
<img src="https://logoapi.sh/stripe.com.svg" alt="Stripe" height="24">
```

Coming from Clearbit? Read the [Clearbit Logo API migration guide](https://logoapi.sh/blog/clearbit-logo-api-migration).

## Tell your AI builder

Using Lovable, Bolt, Base44, v0 or Cursor? Paste this into your prompt. The tool writes the code.

```
For company logos, use an img tag with src https://logoapi.sh/{domain}, where {domain} is the company's website, for example https://logoapi.sh/stripe.com. It returns an SVG. No API key and no signup. Do not add a key or a token.
```

## Logo

**GET** `/{domain}.svg`

The wordmark. Falls back to the square icon when a brand has no wordmark. Every valid domain returns an image. If the catalog misses, you get the site's live favicon, then a wordmark tile with the brand name (.svg URLs always return an SVG: a PNG favicon is wrapped in one).

```
curl -I https://logoapi.sh/stripe.com.svg
```

**Response**

```
HTTP/2 200
content-type: image/svg+xml
access-control-allow-origin: *
cache-control: public, max-age=86400, stale-while-revalidate=86400
```

The `X-Logo-Kind` header says what the file is: `wordmark` when this route served a wordmark (a separate wordmark file, or a logo wider than 3:2), `icon` when it served an icon. Catalog logos only. It is sent on the bare `/icon/{domain}` route and on a bare PNG logo. The bare `/{domain}` route does not send it for an SVG logo, and the `/{domain}.svg` and `/icon/{domain}.svg` forms are plain static files that never did; use `wordmark` from search for those. A favicon or tile fallback has no such header.

**No logo? Get the favicon, or a wordmark tile with the brand name.**

This is on by default, and never a 404. `.svg` URLs always return an SVG: the logo, else the site's favicon wrapped in an SVG (a PNG of at least 32 px on its long side; an SVG favicon passes through), else a wordmark tile with the brand name. Versions get the tile in their colors: light text on a dark box for `/dark/`, plain text for `/white/`, `/black/` and `/grey/`. **Changed in November 2026:** these version URLs used to return a 404 for an unknown domain. Add `?fallback=404` to keep that. Bare URLs (no `.svg`) and `/icon/{domain}` serve the site's favicon as it is (any type or size, fetched and cached), then a wordmark tile with the brand name. `/{domain}.png` serves the favicon as a real PNG, or a 404. Version URLs (`/dark/`, `/white/`, `/black/`, `/grey/`) get the tile only. The tile color is the same for the same domain every time. The `X-Logo-Fallback: favicon` or `X-Logo-Fallback: tile` header tells you which one you got. Add `?fallback=404` to get a 404 on a miss, so your own `onerror` fallback runs. `?fallback=none` does the same. **Changed in November 2026:** `.svg` URLs now use the favicon too; before, they went straight to the tile.

```
<img src="https://logoapi.sh/example.com.svg?fallback=404" alt="Example" onerror="this.src='/img/generic-company.svg'">
```

**Errors**

Never a 404 by default: a miss on a `.svg` URL returns the favicon wrapped in an SVG, else a wordmark tile with the brand name. Add `?fallback=404` to get a plain-text `not found` 404 instead. Too many requests return `429`; wait for `Retry-After`.

[Full guide: get a company logo by domain](https://logoapi.sh/docs/logo-by-domain)

## Bare domain

**GET** `/{domain}`

Same answer as `/{domain}.svg`, without the extension. A Clearbit-style URL works after a host swap.

SVG when the brand publishes one. Some brands have only a PNG; the bare URL serves it as image/png with X-Logo-Kind: raster.

```
<img src="https://logoapi.sh/stripe.com" alt="Stripe" height="24">
```

**Response**

The logo as SVG, or PNG when the brand has only a PNG. A PNG answer carries `X-Logo-Kind` (`raster`, or `wordmark` for a PNG wordmark next to an SVG icon). An SVG answer carries no such header; `wordmark` in search says whether this route serves a wordmark or an icon.

**Errors**

A miss returns the site's favicon as it is (fetched and cached), then a wordmark tile. The `X-Logo-Fallback` header says `favicon` or `tile`. Add `?fallback=404` to get a 404.

[Full guide: get a company logo by domain](https://logoapi.sh/docs/logo-by-domain)

## PNG for email

**GET** `/{domain}.png`

Gmail and Outlook block SVG, so every logo also has a PNG. Colour versions (`/dark/`, `/white/`, `/black/`) are SVG only; `/dark/{domain}.png` returns 404. The default is 512 px on the longest side, with a transparent background. `?size=` snaps to 128, 256, 512 or 1024 (for example 300 gives 256). `?bg=white` returns it on a white background. The icon is `/icon/{domain}.png`. PNG files are rendered from the SVG and carry `X-Logo-Format: png-render`. Brands with only a PNG logo serve that original file unchanged: no resize, no `bg`, no header.

```
<img src="https://logoapi.sh/stripe.com.png?size=256&bg=white" alt="Stripe" width="128">
```

**Response**

A PNG, 512 px on the longest side by default, with `X-Logo-Format: png-render`.

**Errors**

`/dark/{domain}.png` and the other colour versions return 404: they are SVG only. Too many requests return `429`.

[Full guide: PNG company logos for email](https://logoapi.sh/docs/png-logos-for-email)

## Icon

**GET** `/icon/{domain}.svg`

The square mark, for avatars and lists. The bare `/icon/{domain}` route sends `X-Logo-Kind: icon` (the `.svg` form is a static file without it), except for brands whose only logo is a wide wordmark (no square icon exists): there the icon route serves that wordmark and says `X-Logo-Kind: wordmark`.

```
<img src="https://logoapi.sh/icon/github.com.svg" width="32" height="32" alt="GitHub">
```

## Favicon

**GET** `/favicon/{domain}`

A favicon for a site, taken from the catalog icon. `/favicon/{domain}.svg` works too. The answer is SVG. An unknown domain returns a 404 with a JSON body. PNG is coming. See the [Favicon API page](https://logoapi.sh/favicon) for a live demo and a comparison with Google.

```
<link rel="icon" type="image/svg+xml" href="https://logoapi.sh/favicon/github.com">
```

## Colour versions

**GET** `/{version}/{domain}.svg`

These versions are generated by URL, not official brand files, except where the brand publishes its own (Notion today), which is served as is. Put `white`, `black`, `grey` or `dark` in front of any logo path. `white` and `black` repaint every colour to one flat colour, `grey` removes the colour. `dark`: a version for dark backgrounds. Black marks turn white; colourful logos stay as they are. The icon form is `/{version}/icon/{domain}.svg`. The `.svg` ending is optional.

| Version | URL |
| --- | --- |
| white | `/white/stripe.com.svg` |
| black | `/black/stripe.com.svg` |
| grey | `/grey/stripe.com.svg` |
| dark | `/dark/stripe.com.svg` |
| icon | `/white/icon/github.com.svg` |

```
<img src="https://logoapi.sh/white/stripe.com.svg" alt="Stripe" height="24">
```

## Search

**GET** `/search?q={text}`

Match an exact brand name, an exact domain or a close typo. Returns up to 8 results as JSON. `q` is 2 to 80 characters. A typo is tolerated (1 edit for 4 to 6 characters, 2 for 7 or more); those hits rank below exact matches and carry `"fuzzy": true`. An alias domain finds its main brand. Every result has `wordmark`: `true` when the bare `logo` route serves a wordmark (a separate wordmark file, or a logo wider than 3:2), `false` when it serves an icon. The `/icon/{domain}` route and bare PNG logos say what they served in `X-Logo-Kind`; the bare SVG route does not. Listed companies also carry `ticker` and `exchange` for their main listing (for example `MNDY` on `NASDAQ`). A company listed in the US and on another exchange shows its US listing. Both fields are absent when we do not know them.

```
curl "https://logoapi.sh/search?q=stripe"
```

**Response**

```
{
  "query": "stripe",
  "results": [
    {
      "domain": "stripe.com",
      "name": "Stripe",
      "logo": "https://logoapi.sh/stripe.com.svg",
      "icon": "https://logoapi.sh/icon/stripe.com.svg",
      "tags": ["finance"],
      "source": "https://stripe.com/",
      "wordmark": true,
      "score": 90
    }
  ]
}
```

**Errors**

`400` when `q` is too short or too long (and no tag is given). Too many requests return `429`; wait for `Retry-After`. See Errors for every status.

[Full guide: find a company logo by name](https://logoapi.sh/docs/logo-by-name)

## Tags and filters

**GET** `/search?tag={tag}`

Filter by exactly one tag; a comma list returns 400. With `tag`, `q` is optional. A tag alone returns the first 48 results, with no total. A tag plus `q` returns up to 8. Asking for `page=2` of a tag returns 403. Case does not matter.

```
curl "https://logoapi.sh/search?tag=finance"
curl "https://logoapi.sh/search?tag=finance&q=stripe"
```

**Response**

```
{
  "query": "stripe",
  "tag": ["finance"],
  "page": 1,
  "results": [ { "domain": "stripe.com", "name": "Stripe", "tags": ["finance"], ... } ]
}
```

| Tag | What it covers |
| --- | --- |
| `tech` | Software, SaaS, hardware, AI, security, telecom |
| `devtools` | Developer tools, languages, frameworks, databases, open source |
| `finance` | Banks, payments, fintech, investors, insurance |
| `retail` | Consumer brands, shops, food, travel, cars |
| `media` | News, TV, games, music, social, streaming |
| `organizations` | Nonprofits, government, universities, standards bodies |
| `health` | Pharma, hospitals, health tech |
| `industry` | Energy, manufacturing, logistics, real estate |

An unknown tag returns 400 with the allowed list. For a browsable list, see [`/tag/finance`](https://logoapi.sh/tag/finance) or the [Logo Finder](https://logoapi.sh/finder).

## Brand pages

**GET** `/brand/{domain}`

An HTML page for one brand: its logo, icon and official versions (only the ones the brand publishes), colours, URLs and embed code. White, black, grey and dark versions generated by URL are not shown on the page; see colour versions. Link to it from your docs or share it with a teammate. An unknown domain returns 404.

```
https://logoapi.sh/brand/stripe.com
```

[Open the Stripe page](https://logoapi.sh/brand/stripe.com)

## Aliases

Some brands answer on several domains, for example `aboutamazon.com` and `amazon.com` both serve the Amazon logo. Search returns the main domain once, even when you search for an alias.

## Errors

| Status | When |
| --- | --- |
| `404` | Brand page for an unknown domain, or a logo, icon or version (`/dark/`, `/white/`, `/black/`, `/grey/`) with `?fallback=404`. Plain text `not found`, no placeholder image, so your own fallback runs. Cached for an hour. `/favicon/{domain}` returns a JSON body instead: `{"error":"not_found", "message":..., "claim":...}`. |
| `400` | Bad search input: `q` too short or too long, an unknown tag, or a comma list of tags. JSON with an `error` message. |
| `403` | `page=2` or higher on a tag search. JSON with `error: "page_limit"`. |
| `429` | Too many requests. Wait for `Retry-After`. |
| `503` | Search is briefly unavailable. JSON with `error: "search_unavailable"`. Try again later. |

**404 body for `/favicon/{domain}` and 400 body for a bad search**

```
{
  "error": "not_found",
  "message": "No favicon for acme.example yet. Owners can add one at https://logoapi.sh/startups.",
  "claim": "https://logoapi.sh/startups"
}

{ "error": "q must be 2 to 80 characters (or give tag)" }
```

```
<img src="https://logoapi.sh/icon/acme.example.svg?fallback=404"
     onerror="this.src='/img/generic-company.svg'" alt="Acme">
```

## Caching and CORS

Logo updates go live everywhere within a day. Logos, icons, favicons and colour versions send `cache-control: public, max-age=86400, stale-while-revalidate=86400`. Search results cache for 5 minutes. Brand pages and 404 answers cache for an hour. Error JSON is never cached. Every response sends `Access-Control-Allow-Origin: *`, so you can fetch from any site.

## Stock ticker lookup

**GET** `/ticker/{TICKER}.svg`

Get the logo of a listed company by its stock ticker. The URL redirects (302) to the normal logo URL. Use `.svg` or `.png`; the query string is kept. Tickers are not case sensitive. To pick an exchange, use `/ticker/{EXCHANGE}:{TICKER}.svg`, for example `NASDAQ:MNDY` (`%3A` also works). If a ticker is listed on several exchanges, the US listing is preferred. An unknown ticker returns a plain 404.

```
<img src="https://logoapi.sh/ticker/MNDY.svg" alt="monday.com" height="24">
https://logoapi.sh/ticker/NASDAQ:MNDY.svg
```

**Response**

A `302` redirect to the normal logo URL.

**Errors**

An unknown ticker returns a plain `404`. A known ticker with no logo in the catalog yet serves the company's own favicon on the `.svg` URL, or a name tile when there is none; `X-Logo-Fallback` says which. Add `?fallback=none` to get a 404 instead.

[Full guide: company logo by stock ticker](https://logoapi.sh/docs/logo-by-stock-ticker)

## Limits

2M requests a month per site. Free. No key. No attribution required. Embed our logos and use the search API in your site or app. Don't copy the whole catalog. No surprise bills: we never charge unless you choose a paid plan. Need more volume? Pro is $29 a month for up to 10M requests a month; contact us. Comparing free tiers? See the [best free logo API](https://logoapi.sh/best-free-logo-api).

Tag search returns the first 48 results. A tag plus `q` gives up to 8.

Need more (aggregators, bulk, heavy apps)? Email hello@logoapi.sh.

## AI agents

No setup needed. An agent that writes HTML can use the URL pattern directly: `https://logoapi.sh/{domain}.svg`. To find a domain from a name, call `/search?q=`. For a set, use `/search?tag=`.

To check that a logo exists without reading the SVG, call `https://logoapi.sh/search?q=stripe.com` (JSON with the logo URL). Chat previews block external images. To show logos inside Claude artifacts or ChatGPT canvas, fetch `/{domain}.svg.txt` (or `/icon/{domain}.svg.txt`) and inline the SVG or use a data URI. It is the same file as the .svg, served as plain text. There is no `index.json` or catalog download; use `/search` to look up a domain. No attribution required.

Machine-readable summary: [/llms.txt](https://logoapi.sh/llms.txt). [Full text for AI agents](https://logoapi.sh/llms-full.txt): this whole page, the terms and the Clearbit migration guide as one plain Markdown file.

```
Prompt: "Add a row of customer logos for stripe.com, notion.so and linear.app.\nUse https://logoapi.sh/{domain}.svg for each."
```

## Finder links

The [Logo Finder](https://logoapi.sh/finder) lets you search any brand or browse the top 48 logos of each category.

## FAQ

**Do I need an API key or an account?**

No. There is no key and no signup. Logo requests set no cookies. Put the URL in an img tag.

**Do I have to credit LogoAPI.sh?**

No. No attribution is required.

**Can I use the logos in a commercial product without a link back?**

Yes. No attribution is required, for personal or commercial projects, on the free plan and on paid plans.

**What happens when you don't have a logo?**

.svg URLs always return an SVG: the logo, else the site's favicon wrapped in an SVG (a PNG of at least 32 px; an SVG favicon passes through), else a wordmark tile with the brand name. Bare URLs may return the site's favicon as it is (fetched and cached) before the tile. Add `?fallback=404` to get a 404, for example to run an `onerror` handler on the img.

**How do I check that a logo exists?**

Call `/search?q=stripe.com`. It returns JSON with the logo URL, so you do not need to read the SVG.

**Can I cache the files?**

Yes. Logos are sent with `max-age=86400`, so browsers and CDNs keep them for a day. Do not copy the whole catalog.

**Can I rely on LogoAPI.sh long term?**

Yes. The free tier stays free. We give 12 months' notice before the free tier is reduced or removed. We'll post it here, in the docs and in llms.txt, and email everyone on our updates list.

**How do I claim, correct or remove a logo?**

Trademark owners can claim or correct a logo at [/claim](https://logoapi.sh/claim) and remove it at [/remove](https://logoapi.sh/remove), with one email from their domain.

**Who runs LogoAPI.sh?**

H. Tech Innovation LLC. Questions: hello@logoapi.sh.

## Coming soon

Not live yet. We list them here so you know what is next.

- WebP, and PNG favicons
- Optional monogram fallback
- Free API keys
- OpenAPI spec at `/openapi.json`
