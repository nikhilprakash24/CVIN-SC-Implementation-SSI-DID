'use strict';
/**
 * S2 acceptance: for every option adapter present, deploy, create one identity,
 * change its controller, resolve it, and print one line per method with the
 * outcome (ran / NotApplicable + reason). Run with:
 *   cd 1_blockchain-identity && npx hardhat run ../sandbox/grand/smoke.js
 * Exits non-zero if an adapter throws or lacks a method. NotApplicable is not a failure.
 */
const path = require('path');
const fs = require('fs');
const { assertImplements, isNA, METHODS } = require('../lib/identity_option');

async function main() {
  const optionsDir = path.join(__dirname, '..', 'options');
  const slugs = fs.readdirSync(optionsDir).filter((s) => fs.existsSync(path.join(optionsDir, s, 'adapter.js'))).sort();
  if (!slugs.length) { console.log('no adapters yet'); return; }
  let failures = 0;
  for (const slug of slugs) {
    const Adapter = require(path.join(optionsDir, slug, 'adapter.js'));
    const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
    const a = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
    try {
      assertImplements(a, slug);
      const d = await a.deploy();
      // VINs are 17 characters (ISO 3779); some options validate the length.
      const vin = (`VIN${slug.replace(/[^A-Z0-9]/gi, '').toUpperCase()}` + '0000000000000000').slice(0, 17);
      const c = await a.create({ vin, owner: vehicleOwner.address });
      const id = c.id;
      const rows = [
        ['deploy', d], ['create', c],
        ['changeController', await a.changeController(id, newOwner.address)],
        ['addKeyOrDelegate', await a.addKeyOrDelegate(id, delegate.address, 'veriKey', 3600)],
        ['setAttribute', await a.setAttribute(id, 'did/svc/telematics', 'https://example.invalid/t')],
        ['addClaim', await a.addClaim(id, 1, '0x01', '0x')],
        ['transfer', await a.transfer(id, newOwner.address)],
        ['signedOp', await a.signedOp(id, 'changeOwner', '0x')],
        ['revoke', await a.revoke(id)],
        ['resolve', await a.resolve(id)],
      ];
      console.log(`\n== ${slug}`);
      for (const [m, r] of rows) {
        const tag = isNA(r) ? `NA  ${r.reason}` : r && r.ok ? `ok  ${r.gasUsed != null ? `gas=${r.gasUsed}` : ''}${r.implicit ? ' (implicit)' : ''}${r.note ? ' ' + r.note : ''}` : `??  ${JSON.stringify(r)}`;
        console.log(`  ${m.padEnd(18)} ${tag}`);
      }
      const caps = a.capabilities();
      const undeclared = Object.keys(METHODS).filter((m) => m !== 'capabilities' && !(m in caps));
      if (undeclared.length) { console.log(`  capabilities() missing: ${undeclared.join(', ')}`); failures++; }
    } catch (e) { console.log(`\n== ${slug}\n  FAILED: ${e.message}`); failures++; }
  }
  if (failures) { console.log(`\n${failures} adapter(s) failed`); process.exitCode = 1; }
  else console.log(`\nall ${slugs.length} adapter(s) conform`);
}

main().catch((e) => { console.error(e); process.exitCode = 1; });
