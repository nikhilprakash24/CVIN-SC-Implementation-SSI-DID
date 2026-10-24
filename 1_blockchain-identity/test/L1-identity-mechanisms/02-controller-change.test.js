'use strict';
/**
 * L1 / controller change — changeController(id, newOwner); afterwards the resolved document
 * contains the new controller's address (case-insensitive search of the JSON, since document
 * shapes differ per option).
 */
const L1 = require('./_l1');

describe('L1-02 controller change', function () {
  for (const { slug } of L1.options()) {
    it(`${slug}: changeController -> new controller appears in the resolved document`, async function () {
      const f = await L1.freshIdentity(slug);
      const to = f.signers.newOwner.address;
      await L1.run({ option: slug, mechanism: 'controller-change' }, async (ctx) => {
        const r = await f.adapter.changeController(f.id, to);
        if (L1.isNA(r)) return r;
        const doc = await L1.resolveDoc(f.adapter, f.id);
        ctx.note(L1.expectEvidence(doc, [['new controller address', to]], 'after changeController'));
        return r;
      });
    });
  }
});
