/** SVG markup for a domain (apple.com, www.apple.com, https://apple.com) or a ticker (AAPL). null if not in the package. */
export function getLogo(domainOrTicker: string): string | null;
/** Absolute path to the SVG file, or null. */
export function getLogoPath(domainOrTicker: string): string | null;
/** True if the package ships a logo for this domain or ticker. */
export function hasLogo(domainOrTicker: string): boolean;
/** Every domain and ticker the package covers, sorted. */
export function list(): { domains: string[]; tickers: string[] };

declare const logoapi: {
  getLogo: typeof getLogo;
  getLogoPath: typeof getLogoPath;
  hasLogo: typeof hasLogo;
  list: typeof list;
};
export default logoapi;
