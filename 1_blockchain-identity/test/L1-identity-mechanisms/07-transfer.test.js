'use strict';
/**
 * L1 / transfer — transfer(id, recipient) from the fresh owner (vehicleOwner) to newOwner;
 * afterwards the recipient's address appears in the resolved document. Token options move the
 * token; account options rotate the owner key; registry options without a token return
 * NotApplicable (control moves with changeController).
 */
const L1 = require('./_l1');

describe('L1-07 transfer', function () {
  for (const { slug } of L1.options()) {
    it(`${slug}: transfer -> recipient appears in the resolved document`, async function () {
      const f = await L1.freshIdentity(slug);
      const to = f.signers.newOwner.address;
      await L1.run({ option: slug, mechanism: 'transfer' }, async (ctx) => {
        const r = await f.adapter.transfer(f.id, to);
        if (L1.isNA(r)) return r;
        const doc = await L1.resolveDoc(f.adapter, f.id);
        ctx.note(L1.expectEvidence(doc, [['recipient address', to]], 'after transfer'));
        return r;
      });
    });
  }
});
