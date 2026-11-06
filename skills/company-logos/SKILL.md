---
name: company-logos
description: Add company logos, brand logos and stock ticker logos to a website, app, email or no-code builder using LogoAPI.sh. Use when the user needs a company logo, brand logo, logo by domain, logo by stock ticker, a logo for a customer or partner list, an avatar or icon for a company, or a Clearbit Logo API replacement (logo.clearbit.com shut down in December 2025). Free, no API key, no signup, no attribution. Covers SVG and PNG URLs, ticker lookups, square icons, dark-background versions, missing-logo fallbacks, and Softr, Glide and Airtable-style builders.
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
| By stock ticker | `https://logoapi.sh/ticker/AAPL` (also `.svg`, `.png`, `/ticker/NASDAQ:AAPL.svg`) |
| Dark background | `https://logoapi.sh/dark/apple.com.svg` |
| White / black / grey | `https://logoapi.sh/white/apple.com.svg`, `/black/`, `/grey/` |
| Search by name | `https://logoapi.sh/search?q=stripe` (JSON) |

The ticker route answers with a 302 to the logo, so `<img>` follows it. It is case-insensitive.

## Rules

1. **Domain in hand: use `logoapi.sh/<domain>`.** Nothing else is needed.
2. **Only a ticker: use `/ticker/<SYMBOL>`.** Never build a domain from a ticker (`AAPL` + `.com` is wrong; the company is `apple.com`). Add an exchange when the symbol is ambiguous: `/ticker/NASDAQ:AAPL.svg`. An unknown ticker returns a plain 404.
3. **Never use `logo.clearbit.com`.** The Clearbit Logo API shut down in December 2025. To migrate, swap the host and keep the domain: `logo.clearbit.com/stripe.com` becomes `logoapi.sh/stripe.com`. Drop Clearbit-only query params; on LogoAPI.sh `?size` and `?bg` apply to `.png` only.
4. **Square slots (avatars, list rows, table cells, favicons): use `/icon/<domain>`** and set `object-fit: contain` so wide wordmarks are never cropped.
   ```html
   <img src="https://logoapi.sh/icon/coca-cola.com" alt="Coca-Cola logo"
        width="40" height="40" style="object-fit: contain">
   ```
   Some brands only have a wide wordmark; `/icon/` then returns it, and `contain` keeps it whole. Never use `object-fit: cover` for logos.
5. **Always write alt text**: `alt="<Company> logo"`. For a decorative logo next to the company name in text, use `alt=""`.
6. **Dark backgrounds**: use `/dark/<domain>.svg`. It returns the brand's official dark file when one exists, else a contrast-checked version. Colour versions are SVG only (no `.png`).
7. **Email**: use the `.png` URL with explicit `width` and `height`. SVG is blocked in Gmail and Outlook.

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

- Downloading the whole catalog or scraping it. Hot-link instead; caching a day is fine.
- Guessing a domain from a name or ticker without checking `/search`.
- `logo.clearbit.com`, or any Clearbit param.
- Cropping logos into circles with `object-fit: cover`.
- Calling `/suggest` (it is only for the site's own search box).

## More

- Full agent docs: https://logoapi.sh/llms.txt
- API reference: https://logoapi.sh/docs.md
- MCP server (get_logo, search_logos, get_favicon): https://logoapi.sh/mcp
