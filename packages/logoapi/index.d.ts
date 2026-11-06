/** SVG markup for a domain (apple.com, www.apple.com, https://apple.com) or a ticker (AAPL). null if not in the package. */
export function getLogo(domainOrTicker: string): string | null;
/** Absolute path to the SVG file, or null. */
export function getLogoPath(domainOrTicker: string): string | null;
/** True if the package ships a logo for this domain or ticker. */
export function hasLogo(domainOrTicker: string): boolean;
/** Every domain and ticker the package covers, sorted. */
export function list(): { domains: string[]; tickers: string[] };

export interface LogoResult {
  /** The input item, echoed back as given. */
  ticker: string;
  /** `data:image/svg+xml;base64,...` or null when the package has no logo. */
  dataUri: string | null;
  /** 'cc0' for the bundled CC0 files; null on a miss. */
  source: 'cc0' | 'official' | null;
  missing: boolean;
}
/** Batch lookup. Each item may be a ticker or a domain, any case. Misses return missing: true. */
export function getLogos(list: string[]): LogoResult[];

declare const logoapi: {
  getLogo: typeof getLogo;
  getLogoPath: typeof getLogoPath;
  hasLogo: typeof hasLogo;
  list: typeof list;
  getLogos: typeof getLogos;
};
export default logoapi;
