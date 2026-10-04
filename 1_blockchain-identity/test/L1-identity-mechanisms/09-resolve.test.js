'use strict';
/**
 * L1 / resolve — resolve(id) on a fresh identity returns a DID-document-like object built
 * from on-chain reads: an `id`, a `controller` field, a `verificationMethod` array, and the
 * creating owner's address somewhere in the document. resolve is a view: gas is recorded as 0.
 */
const L1 = require('./_l1');
const { expect } = L1;

describe('L1-09 resolve', function () {
  for (const { slug } of L1.options()) {
    it(`${slug}: resolve -> DID-document-like object naming the owner`, async function () {
      const f = await L1.freshIdentity(slug);
      await L1.run({ option: slug, mechanism: 'resolve' }, async (ctx) => {
        const doc = await L1.resolveDoc(f.adapter, f.id);
        const v = doc.value;
        expect(v.id, 'document.id').to.be.a('string').and.not.empty;
        expect(v, 'document.controller').to.have.property('controller');
        expect(v.verificationMethod, 'document.verificationMethod').to.be.an('array');
        ctx.note(L1.expectEvidence(doc, [['owner address', f.signers.vehicleOwner.address]], 'resolve'));
        ctx.note(`id=${v.id}; verificationMethods=${v.verificationMethod.length}`);
        return { ok: true, gasUsed: 0n, note: doc.result.note };
      });
    });
  }
});
