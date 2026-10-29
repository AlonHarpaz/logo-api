<p align="center">
  <a href="https://logoapi.sh?utm_source=github&utm_medium=readme&utm_campaign=logo-api">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset=".github/assets/logoapi-wordmark-dark.svg">
      <img src=".github/assets/logoapi-wordmark.svg" alt="LogoAPI.sh" height="64">
    </picture>
  </a>
</p>

<p align="center">
  <b>Company logos by domain. One URL returns the SVG.</b><br>
  A free alternative to the Clearbit Logo API. No API key, no signup, no attribution. Commercial use included.
</p>

<p align="center">
  <a href="https://logoapi.sh?utm_source=github&utm_medium=readme&utm_campaign=logo-api"><img src="https://img.shields.io/badge/logos%20via%20API-4%2C138-15161a?style=flat-square" alt="4,138 logos via API"></a>
  <a href="logos/"><img src="https://img.shields.io/badge/CC0%20files%20in%20this%20repo-2%2C016-15161a?style=flat-square" alt="2,016 CC0 files in this repo"></a>
  <a href="https://logoapi.sh/docs?utm_source=github&utm_medium=readme&utm_campaign=logo-api"><img src="https://img.shields.io/badge/API%20key-not%20needed-15161a?style=flat-square" alt="No API key"></a>
  <a href="https://logoapi.sh/docs?utm_source=github&utm_medium=readme&utm_campaign=logo-api"><img src="https://img.shields.io/badge/attribution-not%20required-15161a?style=flat-square" alt="Attribution not required"></a>
  <a href="https://logoapi.sh/pricing?utm_source=github&utm_medium=readme&utm_campaign=logo-api"><img src="https://img.shields.io/badge/free-1M%20requests%20a%20month-15161a?style=flat-square" alt="1M requests a month per site, free"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/logo%20files-CC0-15161a?style=flat-square" alt="CC0"></a>
</p>

<p align="center">
  <a href="https://logoapi.sh/docs?utm_source=github&utm_medium=readme&utm_campaign=logo-api">Docs</a> ·
  <a href="https://logoapi.sh/finder?utm_source=github&utm_medium=readme&utm_campaign=logo-api">Logo Finder</a> ·
  <a href="https://logoapi.sh/pricing?utm_source=github&utm_medium=readme&utm_campaign=logo-api">Pricing</a> ·
  <a href="https://logoapi.sh/guides/clearbit-migration?utm_source=github&utm_medium=readme&utm_campaign=logo-api">Migrating from Clearbit</a>
</p>

<br>

<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://logoapi.sh/dark/stripe.com.svg"><img src="https://logoapi.sh/stripe.com.svg" alt="Stripe" height="32"></picture>&nbsp;&nbsp;&nbsp;&nbsp;
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://logoapi.sh/dark/github.com.svg"><img src="https://logoapi.sh/github.com.svg" alt="GitHub" height="32"></picture>&nbsp;&nbsp;&nbsp;&nbsp;
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://logoapi.sh/dark/slack.com.svg"><img src="https://logoapi.sh/slack.com.svg" alt="Slack" height="32"></picture>&nbsp;&nbsp;&nbsp;&nbsp;
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://logoapi.sh/dark/spotify.com.svg"><img src="https://logoapi.sh/spotify.com.svg" alt="Spotify" height="32"></picture>&nbsp;&nbsp;&nbsp;&nbsp;
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://logoapi.sh/dark/figma.com.svg"><img src="https://logoapi.sh/figma.com.svg" alt="Figma" height="32"></picture>&nbsp;&nbsp;&nbsp;&nbsp;
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://logoapi.sh/dark/vercel.com.svg"><img src="https://logoapi.sh/vercel.com.svg" alt="Vercel" height="32"></picture>
</p>

<p align="center"><sub>Every logo above is a live response from logoapi.sh, with the dark mode version on dark themes.</sub></p>

---

## Quick start

Swap the domain. That's it.

```html
<img src="https://logoapi.sh/stripe.com.svg" alt="Stripe" height="24">
```

```bash
curl -I https://logoapi.sh/stripe.com.svg
# HTTP/2 200
# content-type: image/svg+xml
# access-control-allow-origin: *
```

An unknown domain gets the site's live favicon, then a letter tile. Add `?fallback=404` to get a plain `404` and run your own fallback.

## Routes

| What you need | URL |
| --- | --- |
| Wordmark logo | `https://logoapi.sh/{domain}.svg` |
| Square icon | `https://logoapi.sh/icon/{domain}.svg` |
| Favicon | `https://logoapi.sh/favicon/{domain}` |
| White, black, grey, dark mode | `https://logoapi.sh/{white\|black\|grey\|dark}/{domain}.svg` |
| Name to domain | `https://logoapi.sh/search?q=stripe` |
| Clearbit-style bare domain | `https://logoapi.sh/{domain}` |

Full reference with real responses: [logoapi.sh/docs](https://logoapi.sh/docs?utm_source=github&utm_medium=readme&utm_campaign=logo-api)

## Examples

**React**

```jsx
function CompanyLogo({ domain, name }) {
  return (
    <img
      src={`https://logoapi.sh/${domain}.svg?fallback=404`}
      alt={name}
      height={24}
      onError={(e) => { e.currentTarget.style.display = "none"; }}
    />
  );
}
```

**Dark mode**

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://logoapi.sh/dark/stripe.com.svg">
  <img src="https://logoapi.sh/stripe.com.svg" alt="Stripe" height="24">
</picture>
```

**Only have a company name?**

```bash
curl "https://logoapi.sh/search?q=stripe"
```

```json
{
  "query": "stripe",
  "results": [
    {
      "domain": "stripe.com",
      "name": "Stripe",
      "logo": "https://logoapi.sh/stripe.com.svg",
      "icon": "https://logoapi.sh/icon/stripe.com.svg",
      "tags": ["finance"]
    }
  ]
}
```

## Coming from Clearbit?

The Clearbit Logo API (`logo.clearbit.com`) has shut down. Change the host and keep the domain:

```diff
- https://logo.clearbit.com/stripe.com
+ https://logoapi.sh/stripe.com
```

Step-by-step guide: [Clearbit Logo API migration](https://logoapi.sh/guides/clearbit-migration?utm_source=github&utm_medium=readme&utm_campaign=logo-api)

## Pricing

**Free:** 1M requests a month per site. No key, no attribution required.
**Pro (waitlist):** $29 a month for 10M requests a month and email support. Join at [logoapi.sh/pricing](https://logoapi.sh/pricing?utm_source=github&utm_medium=readme&utm_campaign=logo-api).
Details: [logoapi.sh/pricing](https://logoapi.sh/pricing?utm_source=github&utm_medium=readme&utm_campaign=logo-api)

**Do I have to credit LogoAPI.sh?** No. No attribution is required, for personal or commercial projects.

## What's in this repo

This repo holds the open logo files behind LogoAPI.sh: 2,016 SVGs from
[gilbarbara/logos](https://github.com/gilbarbara/logos), dedicated to the public domain under
[CC0](LICENSE). They are pinned to commit `dafdf2df1334` and keep gilbarbara's file names.

The hosted API serves the full catalog of 4,138 brands, with wordmarks, icons, colour versions and
search. The API service itself is not in this repo.

## Contributing

- **Missing, wrong or outdated logo?** [Open an issue](../../issues/new/choose). The forms ask for the domain and a link to the official file.
- **You own a brand and want its logo changed or removed?** Use [logoapi.sh/claim](https://logoapi.sh/claim?utm_source=github&utm_medium=readme&utm_campaign=logo-api). We reply within 2 business days.

## License

Logo files in this repo: [CC0 1.0](LICENSE), from gilbarbara/logos.
Logos remain trademarks of their owners. Use them to refer to the company, not to imply endorsement.

<p align="center"><sub>LogoAPI.sh is operated by H. Tech Innovation LLC, Dallas, TX.</sub></p>
