// Copies the official coin marks from the repo root into this package before npm pack.
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..', '..', '..');
const pkg = path.join(__dirname, '..');
const out = path.join(pkg, 'official');
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(path.join(out, 'crypto'), { recursive: true });
const src = path.join(root, 'official', 'crypto');
const crypto = {};
for (const f of fs.readdirSync(src).filter((n) => n.endsWith('.svg')).sort()) {
  fs.copyFileSync(path.join(src, f), path.join(out, 'crypto', f));
  crypto[f.slice(0, -4)] = 'official/crypto/' + f;
}
if (!Object.keys(crypto).length) throw new Error('no coin marks found in official/crypto');
fs.copyFileSync(path.join(root, 'official', 'LICENSE.md'), path.join(out, 'LICENSE.md'));
fs.writeFileSync(path.join(out, 'index.json'), JSON.stringify({ crypto }, null, 1) + '\n');
