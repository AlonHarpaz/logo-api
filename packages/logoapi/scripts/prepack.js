// Copies the CC0 catalog from the repo root into this package before npm pack.
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..', '..', '..');
const pkg = path.join(__dirname, '..');
fs.rmSync(path.join(pkg, 'logos'), { recursive: true, force: true });
fs.cpSync(path.join(root, 'logos'), path.join(pkg, 'logos'), { recursive: true });
// Filtered copy: only domains and tickers whose values are repo paths (strings).
// The root index.json also carries API-only tickers, coins and URL patterns; keep them out of the tarball.
const full = JSON.parse(fs.readFileSync(path.join(root, 'index.json'), 'utf8'));
const onlyStrings = (m) => Object.fromEntries(Object.entries(m || {}).filter(([, v]) => typeof v === 'string'));
const filtered = { domains: onlyStrings(full.domains), tickers: onlyStrings(full.tickers) };
fs.writeFileSync(path.join(pkg, 'index.json'), JSON.stringify(filtered, null, 1) + '\n');
fs.copyFileSync(path.join(root, 'LICENSE'), path.join(pkg, 'LICENSE'));
const idx = JSON.parse(fs.readFileSync(path.join(pkg, 'index.json'), 'utf8'));
for (const m of [idx.domains, idx.tickers]) {
  for (const p of Object.values(m)) {
    if (typeof p !== 'string') continue; // API-only entries are objects, not repo paths
    if (!fs.existsSync(path.join(pkg, p))) throw new Error('index.json points to a missing file: ' + p);
  }
}

// Regenerate the "Bundled tickers" section of llms.txt from index.json so it cannot drift.
const llmsPath = path.join(pkg, 'llms.txt');
const llms = fs.readFileSync(llmsPath, 'utf8');
const start = '<!-- tickers:start -->';
const end = '<!-- tickers:end -->';
const a = llms.indexOf(start);
const b = llms.indexOf(end);
if (a === -1 || b === -1 || b < a) throw new Error('llms.txt is missing the tickers markers');
const syms = Object.keys(idx.tickers).filter((k) => typeof idx.tickers[k] === 'string').sort();
const block = start + '\n' + syms.length + ' tickers: ' + syms.join(', ') + '\n' + end;
fs.writeFileSync(llmsPath, llms.slice(0, a) + block + llms.slice(b + end.length));
