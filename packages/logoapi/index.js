'use strict';
const fs = require('fs');
const path = require('path');

const index = require('./index.json');
const domains = index.domains;
const tickers = index.tickers;

function resolve(input) {
  if (typeof input !== 'string') return null;
  let s = input.trim();
  if (!s) return null;
  const t = s.toUpperCase();
  const pick = (map, key) =>
    Object.prototype.hasOwnProperty.call(map, key) && typeof map[key] === 'string' ? map[key] : null;
  const tk = pick(tickers, t);
  if (tk) return tk;
  s = s.toLowerCase().replace(/^[a-z][a-z0-9+.-]*:\/\//, '').split(/[/?#]/)[0].replace(/:\d+$/, '');
  const dm = pick(domains, s);
  if (dm) return dm;
  if (s.startsWith('www.')) {
    s = s.slice(4);
    return pick(domains, s);
  }
  return null;
}

function getLogoPath(domainOrTicker) {
  const rel = resolve(domainOrTicker);
  return rel ? path.join(__dirname, rel) : null;
}

function getLogo(domainOrTicker) {
  const p = getLogoPath(domainOrTicker);
  return p ? fs.readFileSync(p, 'utf8') : null;
}

function hasLogo(domainOrTicker) {
  return resolve(domainOrTicker) !== null;
}

function list() {
  return {
    domains: Object.keys(domains).filter((k) => typeof domains[k] === 'string').sort(),
    tickers: Object.keys(tickers).filter((k) => typeof tickers[k] === 'string').sort()
  };
}

function getLogos(items) {
  if (!Array.isArray(items)) throw new TypeError('getLogos expects an array');
  return items.map((item) => {
    const rel = resolve(item);
    if (!rel) return { ticker: item, dataUri: null, source: null, missing: true };
    const svg = fs.readFileSync(path.join(__dirname, rel));
    return {
      ticker: item,
      dataUri: 'data:image/svg+xml;base64,' + svg.toString('base64'),
      source: 'cc0',
      missing: false
    };
  });
}

module.exports = { getLogo, getLogoPath, hasLogo, list, getLogos };
