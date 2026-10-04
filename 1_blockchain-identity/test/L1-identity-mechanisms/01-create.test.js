'use strict';
/**
 * L1 / create — every option: create({ vin, owner }) yields a resolvable identity.
 * Implicit creations (identity = the address, no transaction) must report gasUsed 0;
 * explicit ones (a mint / registration / account deployment) gas > 0.
 */
const L1 = require('./_l1');
const { expect } = L1;

describe('L1-01 create', function () {
  for (const { slug } of L1.options()) {
    it(`${slug}: create -> resolvable identity (implicit: gas 0, explicit: gas > 0)`, async function () {
      const f = await L1.freshIdentity(slug);
      await L1.run({ option: slug, mechanism: 'create' }, async (ctx) => {
        const c = f.created;
        expect(c.id, 'create() must return a string id').to.be.a('string').and.not.empty;
        const gas = BigInt(c.gasUsed);
        if (c.implicit === true) {
          expect(gas, 'implicit creation must report gasUsed 0').to.equal(0n);
          ctx.note('implicit');
        } else {
          expect(gas, 'explicit creation must report gasUsed > 0').to.be.greaterThan(0n);
          expect(c.receipt, 'explicit creation must carry a receipt').to.exist;
          ctx.note('explicit');
        }
        const doc = await L1.resolveDoc(f.adapter, f.id);
        expect(doc.value.id, 'resolved document has an id').to.be.a('string');
        ctx.note(`resolved as ${doc.value.id}`);
        return c;
      });
    });
  }
});
