# Official marks

Square brand marks for about 100 large US-listed companies and the main coins, reproduced unchanged from each company's own brand or press material, under predictable file names. These files are NOT CC0; see [LICENSE.md](LICENSE.md). The CC0 set lives in `../logos/` and `../tickers/`.

Raw URL pattern:

`https://raw.githubusercontent.com/AlonHarpaz/logo-api/main/official/tickers/<SYMBOL>.svg`
`https://raw.githubusercontent.com/AlonHarpaz/logo-api/main/official/crypto/<SYMBOL>.svg`

Examples: `.../main/official/tickers/WMT.svg`, `.../main/official/crypto/BTC.svg`. The map is in [index.json](index.json): `{"tickers": {"WMT": "official/tickers/WMT.svg"}, "crypto": {"BTC": "official/crypto/BTC.svg"}}`.

## What is here

- `tickers/`: 24 square marks from a list of about 100 large US-listed companies, as of 2026-11-06, whose square icon is a real vector: ABBV, ACN, AXP, BAC, BKNG, CSCO, CVX, GE, HON, MCD, PANW, PG, SCHW, T, TSLA, WFC, WMT, plus seven Vanguard ETFs: BND, VIG, VOO, VTI, VTV, VUG, VXUS. ETFs map to the issuer's mark (VTI -> Vanguard).
- `crypto/`: 14 coin marks: ADA, BCH, BNB, BTC, ETH, LINK, NEAR, SOL, TRX, USDC, USDT, XLM, XRP, ZEC.

Every file is byte-for-byte what the API serves at `https://logoapi.sh/icon/<domain>.svg`. USDC and XRP are the marks the `https://logoapi.sh/crypto/<SYMBOL>.svg` route serves from its bundle. Nothing is redrawn or edited.

## What is not here

- Already in `../tickers/` (CC0, same raw pattern with `tickers/` instead of `official/tickers/`): NVDA, MSFT, AAPL, GOOGL, META, AVGO, V, ORCL, MA, NFLX, AMD, IBM, QCOM, ADBE, MU, CRM.
- Use the API for these. Their square icon today is a wordmark, a name tile or a wrapped PNG, so there is no vector square mark to copy. `https://logoapi.sh/icon/ticker/<SYMBOL>` always answers, and `https://logoapi.sh/ticker/<SYMBOL>` gives the full logo.

| Ticker | Domain | Use |
| --- | --- | --- |
| ABT | abbott.com | https://logoapi.sh/icon/ticker/ABT |
| ADI | analog.com | https://logoapi.sh/icon/ticker/ADI |
| ADP | adp.com | https://logoapi.sh/icon/ticker/ADP |
| AMAT | appliedmaterials.com | https://logoapi.sh/icon/ticker/AMAT |
| AMGN | amgen.com | https://logoapi.sh/icon/ticker/AMGN |
| AMZN | amazon.com | https://logoapi.sh/icon/ticker/AMZN |
| ANET | arista.com | https://logoapi.sh/icon/ticker/ANET |
| APH | amphenol.com | https://logoapi.sh/icon/ticker/APH |
| BA | boeing.com | https://logoapi.sh/icon/ticker/BA |
| BLK | blackrock.com | https://logoapi.sh/icon/ticker/BLK |
| BMY | bms.com | https://logoapi.sh/icon/ticker/BMY |
| BRK.B | berkshirehathaway.com | https://logoapi.sh/icon/ticker/BRK.B |
| BSX | bostonscientific.com | https://logoapi.sh/icon/ticker/BSX |
| C | citigroup.com | https://logoapi.sh/icon/ticker/C |
| CAT | caterpillar.com | https://logoapi.sh/icon/ticker/CAT |
| CB | chubb.com | https://logoapi.sh/icon/ticker/CB |
| CMCSA | comcast.com | https://logoapi.sh/icon/ticker/CMCSA |
| COF | capitalone.com | https://logoapi.sh/icon/ticker/COF |
| COP | conocophillips.com | https://logoapi.sh/icon/ticker/COP |
| COST | costco.com | https://logoapi.sh/icon/ticker/COST |
| CRWD | crowdstrike.com | https://logoapi.sh/icon/ticker/CRWD |
| DE | deere.com | https://logoapi.sh/icon/ticker/DE |
| DHR | danaher.com | https://logoapi.sh/icon/ticker/DHR |
| DIS | thewaltdisneycompany.com | https://logoapi.sh/icon/ticker/DIS |
| ETN | eaton.com | https://logoapi.sh/icon/ticker/ETN |
| GEV | gevernova.com | https://logoapi.sh/icon/ticker/GEV |
| GILD | gilead.com | https://logoapi.sh/icon/ticker/GILD |
| GS | goldmansachs.com | https://logoapi.sh/icon/ticker/GS |
| HD | homedepot.com | https://logoapi.sh/icon/ticker/HD |
| INTU | intuit.com | https://logoapi.sh/icon/ticker/INTU |
| ISRG | intuitive.com | https://logoapi.sh/icon/ticker/ISRG |
| JNJ | jnj.com | https://logoapi.sh/icon/ticker/JNJ |
| JPM | jpmorgan.com | https://logoapi.sh/icon/ticker/JPM |
| KKR | kkr.com | https://logoapi.sh/icon/ticker/KKR |
| KLAC | kla.com | https://logoapi.sh/icon/ticker/KLAC |
| KO | coca-cola.com | https://logoapi.sh/icon/ticker/KO |
| LIN | linde.com | https://logoapi.sh/icon/ticker/LIN |
| LLY | lilly.com | https://logoapi.sh/icon/ticker/LLY |
| LMT | lockheedmartin.com | https://logoapi.sh/icon/ticker/LMT |
| LOW | lowes.com | https://logoapi.sh/icon/ticker/LOW |
| LRCX | lamresearch.com | https://logoapi.sh/icon/ticker/LRCX |
| MDT | medtronic.com | https://logoapi.sh/icon/ticker/MDT |
| MMC |  | https://logoapi.sh/icon/ticker/MMC |
| MO | altria.com | https://logoapi.sh/icon/ticker/MO |
| MRK | msd.no | https://logoapi.sh/icon/ticker/MRK |
| MS | ms.com | https://logoapi.sh/icon/ticker/MS |
| NEE | nexteraenergy.com | https://logoapi.sh/icon/ticker/NEE |
| NOW | servicenow.com | https://logoapi.sh/icon/ticker/NOW |
| PEP | pepsico.com | https://logoapi.sh/icon/ticker/PEP |
| PFE | pfizer.com | https://logoapi.sh/icon/ticker/PFE |
| PGR | progressiveagent.com | https://logoapi.sh/icon/ticker/PGR |
| PLD | prologis.com | https://logoapi.sh/icon/ticker/PLD |
| PLTR | palantir.com | https://logoapi.sh/icon/ticker/PLTR |
| PM | pmi.com | https://logoapi.sh/icon/ticker/PM |
| RTX | rtx.com | https://logoapi.sh/icon/ticker/RTX |
| SO | southerncompany.com | https://logoapi.sh/icon/ticker/SO |
| SPGI | spglobal.com | https://logoapi.sh/icon/ticker/SPGI |
| SYK | stryker.com | https://logoapi.sh/icon/ticker/SYK |
| TJX | tjx.com | https://logoapi.sh/icon/ticker/TJX |
| TMUS | t-mobile.com | https://logoapi.sh/icon/ticker/TMUS |
| TXN | ti.com | https://logoapi.sh/icon/ticker/TXN |
| UBER | uber.com | https://logoapi.sh/icon/ticker/UBER |
| UNH | unitedhealthgroup.com | https://logoapi.sh/icon/ticker/UNH |
| UNP | up.com | https://logoapi.sh/icon/ticker/UNP |
| VRTX | vrtx.com | https://logoapi.sh/icon/ticker/VRTX |
| VZ | verizon.com | https://logoapi.sh/icon/ticker/VZ |
| XOM | exxonmobil.com | https://logoapi.sh/icon/ticker/XOM |

- Coins without a vector mark here: DOGE, HYPE, XMR. Use `https://logoapi.sh/crypto/<SYMBOL>`.
- Everything else (5,000+ companies, PNG, dark variants): `https://logoapi.sh/<domain>`, `https://logoapi.sh/ticker/<SYMBOL>`, `https://logoapi.sh/icon/ticker/<SYMBOL>`. Docs: https://logoapi.sh/docs. MCP: https://logoapi.sh/mcp.

Owners: to change or remove a mark, use https://logoapi.sh/claim.
