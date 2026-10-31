'use strict';
/**
 * L1 / signed op — signedOp(id, 'changeOwner', '0x'): off-chain-authorised execution. With an
 * empty signature the adapter signs with the current controller's key (ERC-1056
 * changeOwnerSigned, ERC-4337 handleOp) or runs the option's execute() surface (ERC-725 /
 * ERC-725xy, which are msg.sender-gated and ignore the signature — the adapter note says so).
 * ok with a receipt and gas > 0 is the generic assertion; the identity must still resolve.
 */
const L1 = require('./_l1');
const { expect } = L1;

describe('L1-08 signed op', function () {
  for (const { slug } of L1.options()) {
    it(`${slug}: signedOp('changeOwner') -> ok with a receipt (gas > 0)`, async function () {
      const f = await L1.freshIdentity(slug);
      await L1.run({ option: slug, mechanism: 'signed-op' }, async (ctx) => {
        const r = await f.adapter.signedOp(f.id, 'changeOwner', '0x');
        if (L1.isNA(r)) return r;
        expect(r.receipt, 'signedOp must carry a receipt').to.exist;
        expect(BigInt(r.gasUsed), 'signedOp gasUsed > 0').to.be.greaterThan(0n);
        const doc = await L1.resolveDoc(f.adapter, f.id);
        ctx.note(`resolved as ${doc.value.id}`);
        return r;
      });
    });
  }
});
