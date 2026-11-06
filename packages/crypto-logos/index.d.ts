/** SVG markup for a coin symbol (BTC), else a CC0 domain or ticker from logoapi. null if not in the package. */
export function getLogo(symbolDomainOrTicker: string): string | null;
/** Absolute path to the SVG file, or null. */
export function getLogoPath(symbolDomainOrTicker: string): string | null;
/** True if the package ships a logo for this input. */
export function hasLogo(symbolDomainOrTicker: string): boolean;
/** Every coin, domain and ticker the package covers, sorted. */
export function list(): { crypto: string[]; domains: string[]; tickers: string[] };

export interface LogoResult {
  /** The input item, echoed back as given. */
  ticker: string;
  /** `data:image/svg+xml;base64,...` or null when the package has no logo. */
  dataUri: string | null;
  /** 'official' for coin marks, 'cc0' for the logoapi fallback files, null on a miss. */
  source: 'cc0' | 'official' | null;
  missing: boolean;
}
/** Batch lookup. Coins come back with source 'official'. */
export function getLogos(list: string[]): LogoResult[];

declare const cryptoLogos: {
  getLogo: typeof getLogo;
  getLogoPath: typeof getLogoPath;
  hasLogo: typeof hasLogo;
  list: typeof list;
  getLogos: typeof getLogos;
};
export default cryptoLogos;
