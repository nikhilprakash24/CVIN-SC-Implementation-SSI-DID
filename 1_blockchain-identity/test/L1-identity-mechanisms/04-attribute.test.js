'use strict';
/**
 * L1 / attribute — setAttribute(id, 'did/svc/telematics', value); afterwards the key or the
 * value appears in the resolved document (as text, as hex bytes, as keccak(key) or as a
 * bytes32 string, depending on how the option stores attributes).
 */
const L1 = require('./_l1');

describe('L1-04 attribute', function () {
  for (const { slug } of L1.options()) {
    it(`${slug}: setAttribute -> key or value appears in the resolved document`, async function () {
      const f = await L1.freshIdentity(slug);
      const key = 'did/svc/telematics';
      const value = `https://l1.example.invalid/${slug}/telematics`;
      await L1.run({ option: slug, mechanism: 'attribute' }, async (ctx) => {
        const r = await f.adapter.setAttribute(f.id, key, value);
        if (L1.isNA(r)) return r;
        const doc = await L1.resolveDoc(f.adapter, f.id);
        ctx.note(L1.expectEvidence(doc, [['attribute value', value], ['attribute key', key]], 'after setAttribute'));
        return r;
      });
    });
  }
});
