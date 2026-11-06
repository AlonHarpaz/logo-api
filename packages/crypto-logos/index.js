'use strict';
const fs = require('fs');
const path = require('path');
const base = require('logoapi');

const dir = path.join(__dirname, 'official', 'crypto');

function coinPath(input) {
  if (typeof input !== 'string') return null;
  const sym = input.trim().toUpperCase();
  if (!/^[A-Z0-9]{1,15}$/.test(sym)) return null;
  const p = path.join(dir, sym + '.svg');
  return fs.existsSync(p) ? p : null;
}

function getLogoPath(input) {
  return coinPath(input) || base.getLogoPath(input);
}

function getLogo(input) {
  const p = coinPath(input);
  return p ? fs.readFileSync(p, 'utf8') : base.getLogo(input);
}

function hasLogo(input) {
  return coinPath(input) !== null || base.hasLogo(input);
}

function list() {
  const crypto = fs.existsSync(dir)
    ? fs.readdirSync(dir).filter((n) => n.endsWith('.svg')).map((n) => n.slice(0, -4)).sort()
    : [];
  return Object.assign({}, base.list(), { crypto });
}

function getLogos(items) {
  if (!Array.isArray(items)) throw new TypeError('getLogos expects an array');
  return items.map((item) => {
    const p = coinPath(item);
    if (!p) return base.getLogos([item])[0];
    return {
      ticker: item,
      dataUri: 'data:image/svg+xml;base64,' + fs.readFileSync(p).toString('base64'),
      source: 'official',
      missing: false
    };
  });
}

module.exports = { getLogo, getLogoPath, hasLogo, list, getLogos };
