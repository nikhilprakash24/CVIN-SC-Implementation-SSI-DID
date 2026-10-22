'use strict';
/**
 * L1 / key or delegate — addKeyOrDelegate(id, delegate, 'veriKey', 3600); afterwards the key
 * address (or the key id the adapter derived from it, e.g. ERC-734 keccak(abi.encode(address)))
 * appears in the resolved document.
 */
const L1 = require('./_l1');
const { ethers } = L1;

describe('L1-03 key or delegate', function () {
  for (const { slug } of L1.options()) {
    it(`${slug}: addKeyOrDelegate -> key appears in the resolved document`, async function () {
      const f = await L1.freshIdentity(slug);
      const key = f.signers.delegate.address;
      await L1.run({ option: slug, mechanism: 'key-or-delegate' }, async (ctx) => {
        const r = await f.adapter.addKeyOrDelegate(f.id, key, 'veriKey', 3600);
        if (L1.isNA(r)) return r;
        const doc = await L1.resolveDoc(f.adapter, f.id);
        const needles = [
          ['key address', key],
          ['ERC-734 key id keccak(abi.encode(address))', ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(['address'], [key]))],
        ];
        if (r.keyId) needles.push(['adapter keyId', r.keyId]);
        ctx.note(L1.expectEvidence(doc, needles, 'after addKeyOrDelegate'));
        return r;
      });
    });
  }
});
