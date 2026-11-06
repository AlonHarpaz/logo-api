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
