'use strict';
/**
 * L1 / claim — addClaim(id, topic 1, data, '0x') (the adapter signs as issuer when the
 * signature is empty); afterwards the claim data, its claim id, the topic name or the
 * credential appears in the resolved document — or, for options that store only a hash /
 * a balance (MOBI VID lifecycle events, ERC-1155 credential units), the document differs
 * from the pre-claim document. The evidence found is recorded in the note.
 */
const L1 = require('./_l1');
const { expect, ethers } = L1;

describe('L1-05 claim', function () {
  for (const { slug } of L1.options()) {
    it(`${slug}: addClaim -> claim appears in the resolved document`, async function () {
      const f = await L1.freshIdentity(slug);
      const topic = 1;
      const data = `L1-claim:${slug}:${f.vin}`;
      await L1.run({ option: slug, mechanism: 'claim' }, async (ctx) => {
        const before = await L1.resolveDoc(f.adapter, f.id);
        const r = await f.adapter.addClaim(f.id, topic, data, '0x');
        if (L1.isNA(r)) return r;
        const after = await L1.resolveDoc(f.adapter, f.id);
        const needles = [['claim data', data], ['keccak(data)', ethers.keccak256(ethers.toUtf8Bytes(data))]];
        const claimId = r.claimId || r.value;
        if (claimId != null) needles.push(['claimId', String(claimId)]);
        let ev = L1.firstEvidence(after, needles);
        if (!ev && after.json !== before.json) ev = 'document changed after addClaim (claim stored as hash/balance only)';
        expect(ev, 'after addClaim: neither the claim data, its id nor a document change is observable').to.be.a('string');
        ctx.note(ev);
        return r;
      });
    });
  }
});
