'use strict';
/**
 * Shared helper for the L1 cross-option mechanism suite (plan S3,
 * docs/PLAN_SANDBOX_AND_SUITES.md §2).
 *
 * - discovers every sandbox/options/<slug>/adapter.js at load time;
 * - gives each test a fresh deploy + create fixture (new adapter instance, new contracts,
 *   one identity bound to a 17-char VIN) so mechanisms never observe each other's state;
 * - records one row per (option, mechanism) — outcome ok | na | fail, exact gasUsed
 *   (BigInt kept as a decimal string in JSON), the NotApplicable reason or the error;
 * - in a mocha ROOT `after` hook writes sandbox/grand/report/L1-asymmetry.{json,md},
 *   including the comparison of the observed N/A outcomes with the manifests' stances.
 *
 * This file has no tests of its own; Hardhat loads it like any *.js under test/ and the
 * numbered files require it.
 *
 * Run only this layer (Hardhat's `test` task takes files, not a directory):
 *   cd 1_blockchain-identity && npx hardhat test test/L1-identity-mechanisms/*.test.js
 */
const fs = require('fs');
const path = require('path');
const { expect } = require('chai');
const { ethers } = require('hardhat');
const { NotApplicable, assertImplements, isNA } = require('../../../sandbox/lib/identity_option');

const REPO_ROOT = path.resolve(__dirname, '..', '..', '..');
const OPTIONS_DIR = path.join(REPO_ROOT, 'sandbox', 'options');
const REPORT_DIR = path.join(REPO_ROOT, 'sandbox', 'grand', 'report');

/** Mechanism keys in table order, with the manifest family each one is compared against. */
const MECHANISMS = Object.freeze([
  'create', 'controller-change', 'key-or-delegate', 'attribute', 'claim', 'revoke', 'transfer', 'signed-op', 'resolve',
]);
const FAMILY = Object.freeze({
  'create': ['Identity creation (explicit)', 'Off-chain creation (identity exists before any transaction)'],
  'controller-change': ['Ownership / controller change'],
  'key-or-delegate': ['Key / delegate management'],
  'attribute': ['Attributes / data store'],
  'claim': ['Claims / credentials'],
  'revoke': ['Revocation / status'],
  'transfer': ['Token economics (approvals, royalties, payments)', 'Ownership / controller change'],
  'signed-op': ['Delegated / signed (off-chain-authorised) execution'],
  // 'resolve' is adapter-synthesised from on-chain reads for every option; it is not compared
  // with "DID / resolution helpers" (that family is about on-chain helper functions).
});

// ---------------------------------------------------------------------------
// adapter discovery
// ---------------------------------------------------------------------------
let _options = null;
function options() {
  if (_options) return _options;
  _options = fs.readdirSync(OPTIONS_DIR)
    .filter((s) => fs.existsSync(path.join(OPTIONS_DIR, s, 'adapter.js')))
    .sort()
    .map((slug) => ({ slug, Adapter: require(path.join(OPTIONS_DIR, slug, 'adapter.js')) }));
  return _options;
}

/** 17-character VIN (ISO 3779) derived from the slug, like sandbox/grand/smoke.js. */
function vinFor(slug) {
  return (`VIN${slug.replace(/[^A-Z0-9]/gi, '').toUpperCase()}` + '0'.repeat(17)).slice(0, 17);
}

/**
 * Fresh deploy + create for one option. Returns { slug, adapter, signers, vin, id, deployed, created }.
 * Throws (so the test fails) if the adapter lacks a method, deploy fails, or create is not ok.
 */
async function freshIdentity(slug) {
  const entry = options().find((o) => o.slug === slug);
  if (!entry) throw new Error(`no adapter for option ${slug}`);
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const signers = { deployer, vehicleOwner, newOwner, delegate };
  const adapter = new entry.Adapter({ ethers, signers });
  assertImplements(adapter, slug);
  const deployed = await adapter.deploy();
  if (!deployed || !deployed.ok) throw new Error(`${slug}: deploy() returned ${JSON.stringify(deployed)}`);
  const vin = vinFor(slug);
  const created = await adapter.create({ vin, owner: vehicleOwner.address });
  if (!created || !created.ok || typeof created.id !== 'string') {
    throw new Error(`${slug}: create() returned ${safeJson(created)}`);
  }
  return { slug, adapter, signers, vin, id: created.id, deployed, created };
}

// ---------------------------------------------------------------------------
// document inspection (resolve() shapes differ per option; compare as lower-cased JSON)
// ---------------------------------------------------------------------------
function bigintReplacer(_k, v) { return typeof v === 'bigint' ? v.toString() : v; }
function safeJson(v) { try { return JSON.stringify(v, bigintReplacer); } catch (e) { return String(v); } }

async function resolveDoc(adapter, id) {
  const r = await adapter.resolve(id);
  expect(r && r.ok, `resolve() did not return ok: ${safeJson(r)}`).to.equal(true);
  expect(r.value, 'resolve().value must be an object').to.be.an('object');
  return { value: r.value, json: safeJson(r.value).toLowerCase(), result: r };
}

function contains(doc, needle) {
  if (needle == null || needle === '') return false;
  return doc.json.includes(String(needle).toLowerCase());
}

/** Candidate spellings under which a text/hex value can appear in a document. */
function spellings(value) {
  const out = new Set();
  const s = String(value);
  out.add(s);
  if (ethers.isHexString(s)) {
    out.add(s.slice(2));
  } else {
    out.add(ethers.hexlify(ethers.toUtf8Bytes(s)).slice(2));
    out.add(ethers.keccak256(ethers.toUtf8Bytes(s)));
    if (ethers.toUtf8Bytes(s).length <= 31) out.add(ethers.encodeBytes32String(s));
  }
  return [...out].filter((x) => x.length >= 4); // avoid trivially short needles
}

/** Returns the first needle (label) found in the document, or null. `needles` = [[label, value], ...]. */
function firstEvidence(doc, needles) {
  for (const [label, value] of needles) {
    for (const sp of spellings(value)) if (contains(doc, sp)) return `${label} (${sp.length > 48 ? sp.slice(0, 45) + '…' : sp})`;
  }
  return null;
}

function expectEvidence(doc, needles, what) {
  const ev = firstEvidence(doc, needles);
  expect(ev, `${what}: none of ${needles.map(([l]) => l).join(' | ')} appears in the resolved document`).to.be.a('string');
  return ev;
}

const REVOKED_MARKERS = ['"revoked":true', '"active":false', '"deactivated":true', '"exists":false', '"registered":false', '"inactive"'];
function revokedMarker(doc) { return REVOKED_MARKERS.find((m) => doc.json.includes(m)) || null; }

// ---------------------------------------------------------------------------
// recorder
// ---------------------------------------------------------------------------
const records = [];

function gasOf(r) {
  if (!r || r.gasUsed == null) return null;
  try { return BigInt(r.gasUsed); } catch (_) { return null; }
}

/**
 * Runs `body` for one (option, mechanism) and records the outcome.
 * `body(ctx)` returns the adapter Result (ok or NotApplicable); it may call ctx.note(text)
 * to attach evidence. NotApplicable -> recorded as `na` and the test passes. A throw (adapter
 * error or failed assertion) -> recorded as `fail` and rethrown so the test fails.
 */
async function run({ option, mechanism }, body) {
  const ctx = { notes: [], note(t) { if (t) this.notes.push(String(t)); } };
  let r;
  try {
    r = await body(ctx);
  } catch (e) {
    records.push({ option, mechanism, outcome: 'fail', gasUsed: null, reason: e && e.message ? e.message : String(e), note: ctx.notes.join('; ') || null });
    throw e;
  }
  if (isNA(r)) {
    records.push({ option, mechanism, outcome: 'na', gasUsed: null, reason: r.reason, note: ctx.notes.join('; ') || null });
    return r;
  }
  if (!r || r.ok !== true) {
    const msg = `${option}/${mechanism}: adapter returned neither ok nor NotApplicable: ${safeJson(r)}`;
    records.push({ option, mechanism, outcome: 'fail', gasUsed: null, reason: msg, note: ctx.notes.join('; ') || null });
    throw new Error(msg);
  }
  if (r.note) ctx.notes.unshift(r.note);
  records.push({ option, mechanism, outcome: 'ok', gasUsed: gasOf(r), reason: null, note: ctx.notes.join('; ') || null });
  return r;
}

// ---------------------------------------------------------------------------
// manifests
// ---------------------------------------------------------------------------
function loadManifestFamilies(slug) {
  const file = path.join(OPTIONS_DIR, slug, 'manifest.yaml');
  if (!fs.existsSync(file)) return null;
  const text = fs.readFileSync(file, 'utf8');
  try {
    const yaml = require('js-yaml');
    const m = yaml.load(text);
    const out = {};
    for (const f of m.families || []) out[f.name] = { stance: f.stance, reason: f.reason || '' };
    return out;
  } catch (_) {
    // minimal fallback: "- name: X" followed by "stance: Y" lines
    const out = {};
    let cur = null;
    for (const line of text.split('\n')) {
      const n = line.match(/^- name:\s*(.+)$/); if (n) { cur = n[1].trim().replace(/^'|'$/g, ''); out[cur] = { stance: '', reason: '' }; continue; }
      const s = line.match(/^\s+stance:\s*(.+)$/); if (s && cur) out[cur].stance = s[1].trim();
    }
    return out;
  }
}

const supported = (stance) => stance != null && stance !== '' && stance !== 'not-applicable';

/** manifest stance vs observed outcome for one record; returns { agree, expected, observed, detail }. */
function compareWithManifest(rec, fams) {
  const names = FAMILY[rec.mechanism];
  if (!names || !fams) return null;
  const st = names.map((n) => (fams[n] ? fams[n].stance : 'missing'));
  const says = names.map((n, i) => `"${n}" ${st[i]}`).join(', ');
  const observed = rec.outcome === 'ok'
    ? `ok (gas ${rec.gasUsed}${rec.note ? '; ' + rec.note : ''})`
    : rec.outcome === 'na' ? `n/a (${rec.reason})` : `fail (${rec.reason})`;
  let agree;
  if (rec.outcome === 'fail') agree = false;
  else if (rec.mechanism === 'create') {
    const implicit = rec.outcome === 'ok' && /implicit/.test(rec.note || '') && rec.gasUsed === 0n;
    if (rec.outcome === 'na') agree = !supported(st[0]);
    else if (implicit) agree = supported(st[1]) || supported(st[0]);
    else agree = supported(st[0]);
  } else if (rec.mechanism === 'transfer') {
    // ok via a token OR via the ownership/controller change; n/a disagrees only when a token family exists
    agree = rec.outcome === 'ok' ? (supported(st[0]) || supported(st[1])) : !supported(st[0]);
  } else {
    agree = rec.outcome === 'ok' ? supported(st[0]) : !supported(st[0]);
  }
  return { option: rec.option, mechanism: rec.mechanism, agree, manifest: says, observed };
}

// ---------------------------------------------------------------------------
// report
// ---------------------------------------------------------------------------
function buildReport() {
  const opts = [...new Set(records.map((r) => r.option))].sort();
  const mechs = MECHANISMS.filter((m) => records.some((r) => r.mechanism === m));
  const cell = {};
  for (const r of records) cell[`${r.mechanism}|${r.option}`] = r; // last write wins (one per pair expected)

  const manifests = {};
  for (const o of opts) manifests[o] = loadManifestFamilies(o);
  const comparison = records.map((r) => compareWithManifest(r, manifests[r.option])).filter(Boolean);
  const disagreements = comparison.filter((c) => !c.agree);

  const counts = {};
  for (const m of mechs) {
    counts[m] = { ok: 0, na: 0, fail: 0 };
    for (const o of opts) { const r = cell[`${m}|${o}`]; if (r) counts[m][r.outcome]++; }
  }

  const json = {
    generatedAt: new Date().toISOString(),
    suite: '1_blockchain-identity/test/L1-identity-mechanisms',
    options: opts,
    mechanisms: mechs,
    counts,
    records: records.map((r) => ({ ...r, gasUsed: r.gasUsed == null ? null : r.gasUsed.toString() })),
    naReasons: records.filter((r) => r.outcome === 'na').map((r) => ({ option: r.option, mechanism: r.mechanism, reason: r.reason, note: r.note })),
    failures: records.filter((r) => r.outcome === 'fail').map((r) => ({ option: r.option, mechanism: r.mechanism, error: r.reason })),
    manifestComparison: { families: FAMILY, agreements: comparison.length - disagreements.length, total: comparison.length, disagreements },
  };

  const sym = (r) => !r ? '·' : r.outcome === 'ok' ? `✓ ${r.gasUsed == null ? '?' : r.gasUsed.toString()}` : r.outcome === 'na' ? '—' : '✗';
  const lines = [];
  lines.push('# L1 identity mechanisms — cross-option asymmetry (from tests)');
  lines.push('');
  lines.push(`Generated ${json.generatedAt} by \`cd 1_blockchain-identity && npx hardhat test test/L1-identity-mechanisms/*.test.js\` (${opts.length} options × ${mechs.length} mechanisms, ${records.length} records; each record is a fresh deploy + create).`);
  lines.push('');
  lines.push('✓ gas = the adapter ran the mechanism (exact gasUsed of the measured transaction; 0 = no transaction, e.g. implicit creation or a view) · — = NotApplicable (reason below) · ✗ = adapter error or failed assertion · · = not run');
  lines.push('');
  lines.push(`| Mechanism | ${opts.join(' | ')} |`);
  lines.push(`|---|${opts.map(() => '---').join('|')}|`);
  for (const m of mechs) lines.push(`| ${m} | ${opts.map((o) => sym(cell[`${m}|${o}`])).join(' | ')} |`);
  lines.push('');
  lines.push('Per mechanism: ' + mechs.map((m) => `${m} ok ${counts[m].ok} / na ${counts[m].na} / fail ${counts[m].fail}`).join(' · '));
  lines.push('');
  lines.push('## N/A reasons');
  lines.push('');
  for (const m of mechs) {
    const nas = opts.map((o) => cell[`${m}|${o}`]).filter((r) => r && r.outcome === 'na');
    if (!nas.length) continue;
    lines.push(`### ${m}`);
    lines.push('');
    for (const r of nas) lines.push(`- **${r.option}**: ${r.reason}${r.note ? ` _(${r.note})_` : ''}`);
    lines.push('');
  }
  if (json.failures.length) {
    lines.push('## Adapter errors / failed assertions');
    lines.push('');
    for (const f of json.failures) lines.push(`- **${f.option}** / ${f.mechanism}: ${f.error}`);
    lines.push('');
  }
  lines.push('## Manifest stance vs observed outcome');
  lines.push('');
  lines.push('Family per mechanism: ' + Object.entries(FAMILY).map(([m, f]) => `${m} → ${f.map((x) => `"${x}"`).join(' / ')}`).join('; ') + '. `resolve` is adapter-synthesised for every option and is not compared.');
  lines.push('');
  lines.push(`Agreements: ${json.manifestComparison.agreements} of ${json.manifestComparison.total}. Disagreements (${disagreements.length}; manifests were not edited):`);
  lines.push('');
  if (!disagreements.length) lines.push('- none');
  for (const d of disagreements) lines.push(`- **${d.option}** / ${d.mechanism}: manifest says ${d.manifest}, test observed ${d.observed}`);
  lines.push('');
  return { json, md: lines.join('\n') };
}

function writeReport() {
  if (!records.length) return null;
  fs.mkdirSync(REPORT_DIR, { recursive: true });
  const { json, md } = buildReport();
  const jsonPath = path.join(REPORT_DIR, 'L1-asymmetry.json');
  const mdPath = path.join(REPORT_DIR, 'L1-asymmetry.md');
  fs.writeFileSync(jsonPath, JSON.stringify(json, null, 2) + '\n');
  fs.writeFileSync(mdPath, md);
  return { jsonPath, mdPath, json };
}

// Root-level mocha hook: registered once, when the helper is first loaded (before any describe opens).
if (!global.__L1_REPORT_HOOK__ && typeof after === 'function') {
  global.__L1_REPORT_HOOK__ = true;
  after(function writeL1AsymmetryReport() {
    const out = writeReport();
    if (out) {
      const c = out.json.counts;
      const tot = Object.values(c).reduce((a, x) => ({ ok: a.ok + x.ok, na: a.na + x.na, fail: a.fail + x.fail }), { ok: 0, na: 0, fail: 0 });
      // eslint-disable-next-line no-console
      console.log(`\n  L1 asymmetry report: ok ${tot.ok} / na ${tot.na} / fail ${tot.fail} -> ${path.relative(REPO_ROOT, out.jsonPath)}, ${path.relative(REPO_ROOT, out.mdPath)}`);
    }
  });
}

module.exports = {
  MECHANISMS, FAMILY, NotApplicable, isNA, expect, ethers,
  options, vinFor, freshIdentity,
  resolveDoc, contains, spellings, firstEvidence, expectEvidence, revokedMarker, safeJson,
  run, records, buildReport, writeReport, loadManifestFamilies,
};
