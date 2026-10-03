"use strict";

function sorted(xs) {
  return xs.slice().sort((a, b) => a - b);
}

function percentile(xs, p) {
  if (xs.length === 0) return NaN;
  const s = sorted(xs);
  const idx = (s.length - 1) * p;
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  return s[lo] + (s[hi] - s[lo]) * (idx - lo);
}

function summarize(xs) {
  const n = xs.length;
  if (n === 0) return { n: 0 };
  const mean = xs.reduce((a, b) => a + b, 0) / n;
  const sd = n > 1 ? Math.sqrt(xs.reduce((a, b) => a + (b - mean) ** 2, 0) / (n - 1)) : 0;
  return {
    n,
    mean: round(mean),
    sd: round(sd),
    median: round(percentile(xs, 0.5)),
    p95: round(percentile(xs, 0.95)),
    min: round(Math.min(...xs)),
    max: round(Math.max(...xs)),
  };
}

function round(x, d = 3) {
  const f = 10 ** d;
  return Math.round(x * f) / f;
}

// Bootstrap CI of the median (percentile method).
function bootstrapMedianCI(xs, resamples = 10000, alpha = 0.05, seed = 7) {
  if (xs.length < 2) return null;
  let a = seed >>> 0;
  const rnd = () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const meds = new Array(resamples);
  const n = xs.length;
  for (let r = 0; r < resamples; r++) {
    const sample = new Array(n);
    for (let i = 0; i < n; i++) sample[i] = xs[Math.floor(rnd() * n)];
    meds[r] = percentile(sample, 0.5);
  }
  return { lo: round(percentile(meds, alpha / 2)), hi: round(percentile(meds, 1 - alpha / 2)), resamples };
}

// Mann–Whitney U with normal approximation and tie correction (two-sided).
function mannWhitneyU(xs, ys) {
  const all = xs.map((v) => ({ v, g: 0 })).concat(ys.map((v) => ({ v, g: 1 })));
  all.sort((a, b) => a.v - b.v);
  const ranks = new Array(all.length);
  const tieGroups = [];
  let i = 0;
  while (i < all.length) {
    let j = i;
    while (j + 1 < all.length && all[j + 1].v === all[i].v) j++;
    const r = (i + j) / 2 + 1;
    for (let k = i; k <= j; k++) ranks[k] = r;
    if (j > i) tieGroups.push(j - i + 1);
    i = j + 1;
  }
  const n1 = xs.length, n2 = ys.length, N = n1 + n2;
  let r1 = 0;
  for (let k = 0; k < all.length; k++) if (all[k].g === 0) r1 += ranks[k];
  const u1 = r1 - (n1 * (n1 + 1)) / 2;
  const u2 = n1 * n2 - u1;
  const U = Math.min(u1, u2);
  const mu = (n1 * n2) / 2;
  const tieTerm = tieGroups.reduce((s, t) => s + (t ** 3 - t), 0);
  const sigma = Math.sqrt(((n1 * n2) / 12) * (N + 1 - tieTerm / (N * (N - 1))));
  const z = sigma === 0 ? 0 : (U - mu) / sigma;
  const p = 2 * (1 - normalCdf(Math.abs(z)));
  return { U, z: round(z), p: round(p, 6), n1, n2 };
}

// erf(z) by Abramowitz–Stegun 7.1.26 (|error| ≤ 1.5e-7).
function erf(z) {
  const a = Math.abs(z);
  const t = 1 / (1 + 0.3275911 * a);
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-a * a);
  return z >= 0 ? y : -y;
}

// Standard normal CDF: Φ(x) = ½ (1 + erf(x / √2)). Review 02, H-5: the previous
// version fed x (not x/√2) into the polynomial while using exp(−x²/2), mixing two
// approximations (Φ(1.96) came out 0.981 instead of 0.975).
function normalCdf(x) {
  return 0.5 * (1 + erf(x / Math.SQRT2));
}

function mode(xs) {
  const counts = new Map();
  for (const x of xs) counts.set(x, (counts.get(x) || 0) + 1);
  let best = null, bestN = -1;
  for (const [v, n] of counts) if (n > bestN) { best = v; bestN = n; }
  return { value: best, count: bestN, distinct: [...counts.keys()] };
}

module.exports = { summarize, percentile, bootstrapMedianCI, mannWhitneyU, mode, round, normalCdf, erf };
