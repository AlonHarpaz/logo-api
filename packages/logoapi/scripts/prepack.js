// Copies the CC0 catalog from the repo root into this package before npm pack.
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..', '..', '..');
const pkg = path.join(__dirname, '..');
fs.rmSync(path.join(pkg, 'logos'), { recursive: true, force: true });
fs.cpSync(path.join(root, 'logos'), path.join(pkg, 'logos'), { recursive: true });
fs.copyFileSync(path.join(root, 'index.json'), path.join(pkg, 'index.json'));
fs.copyFileSync(path.join(root, 'LICENSE'), path.join(pkg, 'LICENSE'));
const idx = JSON.parse(fs.readFileSync(path.join(pkg, 'index.json'), 'utf8'));
for (const m of [idx.domains, idx.tickers]) {
  for (const p of Object.values(m)) {
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
const syms = Object.keys(idx.tickers).sort();
const block = start + '\n' + syms.length + ' tickers: ' + syms.join(', ') + '\n' + end;
fs.writeFileSync(llmsPath, llms.slice(0, a) + block + llms.slice(b + end.length));
