'use strict';
/**
 * L1 / revoke — revoke(id) with a bare identity id. Options with identity-level revocation
 * (revokeIdentity, deactivateVehicle, burn) revoke the identity; the event-based / claim-holder
 * options revoke the most recent revocable (claim, delegate or attribute) the adapter added, so
 * the fixture first adds one (addClaim, else addKeyOrDelegate, else setAttribute — the prep is
 * not counted in the recorded gas). Afterwards the resolved document must differ from the
 * pre-revoke document or carry a revoked / inactive / deregistered marker.
 * When the bare id is NotApplicable and the prep produced a claimId / keyId, the sub-identity
 * form is probed and reported in the note (the recorded outcome stays `na`).
 */
const L1 = require('./_l1');
const { expect } = L1;

describe('L1-06 revoke', function () {
  for (const { slug } of L1.options()) {
    it(`${slug}: revoke(id) -> document differs or carries a revoked marker`, async function () {
      const f = await L1.freshIdentity(slug);
      await L1.run({ option: slug, mechanism: 'revoke' }, async (ctx) => {
        // prep: give the identity something revocable
        let prep = null;
        let handle = null;
        for (const [name, call] of [
          ['addClaim', () => f.adapter.addClaim(f.id, 1, `L1-revoke:${slug}`, '0x')],
          ['addKeyOrDelegate', () => f.adapter.addKeyOrDelegate(f.id, f.signers.delegate.address, 'veriKey', 3600)],
          ['setAttribute', () => f.adapter.setAttribute(f.id, 'did/svc/telematics', `https://l1.example.invalid/${slug}`)],
        ]) {
          const p = await call();
          if (p && p.ok) { prep = name; handle = p.claimId || p.keyId || p.value || null; break; }
        }
        ctx.note(prep ? `prep: ${prep}` : 'prep: nothing revocable could be added');

        const before = await L1.resolveDoc(f.adapter, f.id);
        const r = await f.adapter.revoke(f.id);
        if (L1.isNA(r)) {
          if (handle != null) {
            const sub = await f.adapter.revoke(handle);
            ctx.note(L1.isNA(sub)
              ? `sub-identity revoke(${prep} handle) also n/a: ${sub.reason}`
              : `sub-identity revoke(${prep} handle) ok gas=${sub.gasUsed}${sub.note ? ' ' + sub.note : ''}`);
          }
          return r;
        }
        const after = await L1.resolveDoc(f.adapter, f.id);
        const marker = L1.revokedMarker(after);
        const differs = after.json !== before.json;
        expect(differs || marker != null, 'after revoke: document unchanged and no revoked/inactive marker').to.equal(true);
        ctx.note(marker ? `marker ${marker}` : 'document differs from pre-revoke document');
        return r;
      });
    });
  }
});
