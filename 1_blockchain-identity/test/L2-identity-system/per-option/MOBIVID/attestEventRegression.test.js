/**
 * PLAN_MOBI_SUMO M3: regression test for the attestEvent found-and-fixed
 * (register #28: 121,110 -> 192,718 gas).
 *
 * Before the fix, MOBIVIDRegistryV2.attestEvent stored the `signature` blob
 * with no on-chain check, so any role-holder could record a forged
 * attestation in another party's name. The fixed path recovers the signer of
 * keccak256(address(this), chainid, vehicle, eventId) (EIP-191) and requires
 * it to equal msg.sender.
 *
 * The test (1) asserts the vulnerable path is closed and (2) pins the gas of
 * the fixed path.
 *
 * Why the pin is on EXECUTION gas, not on receipt.gasUsed:
 * eventId = keccak256(vehicle, type, issuer, block.timestamp, count), so it
 * changes with the block timestamp, and the attester's signature changes with
 * eventId and the registry address. Both travel in calldata, where a zero
 * byte costs 4 gas and a non-zero byte 16. receipt.gasUsed therefore moves in
 * 12-gas steps from run to run (e.g. 192,659 / 192,671 / 192,683), while
 * gasUsed - 21,000 - calldataGas(tx.data) does not depend on the bytes.
 *
 * The register's 192,718 (commit c376c2f) is above the largest value the
 * current build can produce (169,295 + 21,000 + at most 2,388 calldata gas =
 * 192,683), so that figure came from an earlier build. Swapping the MOBI
 * sources back to c376c2f gives the same 169,295, so the difference is not
 * the K-3/K-4 source changes.
 * The test records several events at different timestamps and checks that
 * this execution gas is identical for all of them and equal to the pinned
 * constant (± 0). receipt.gasUsed is then checked against the exact formula.
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture, time } = require("@nomicfoundation/hardhat-toolbox/network-helpers");

const V2_FQN = "contracts/MOBI/MOBIVIDRegistryV2.sol:MOBIVIDRegistryV2";
const MAINTENANCE = 0;
const ROLE = { MANUFACTURER: 1, SERVICE_CENTER: 3, GOVERNMENT_DMV: 5, INSPECTION_STATION: 7 };

const VIN_HASH = ethers.keccak256(ethers.toUtf8Bytes("5YJ3E1EA0PF123456:salt"));
const BIRTH_CERT_HASH = ethers.keccak256(ethers.toUtf8Bytes("signed-birth-vc"));
const BIRTH_ATTRS = ethers.toUtf8Bytes(JSON.stringify({ make: "Tesla", model: "Model 3", year: 2024 }));
const DATA_HASH = ethers.keccak256(ethers.toUtf8Bytes("event-data"));
const CRED_HASH = ethers.keccak256(ethers.toUtf8Bytes("signed-event-vc"));

// Pinned execution gas of the fixed path: the FIRST attestation on an event,
// 65-byte signature, attester already authorized (gasUsed minus the 21,000
// base and the calldata bytes). Measured 2026-10-04 on solc 0.8.24, viaIR,
// optimizer 200, evm cancun, Hardhat 2.28.6.
const PINNED_EXECUTION_GAS = 169_361n; // re-pinned 2026-10-06 on the merged bytecode (anchorVehicleKey + K-3/K-4 moved the dispatch by +66); was 169_295 on the review-2 tree

const TX_BASE_GAS = 21_000n;

function calldataGas(data) {
  let gas = 0n;
  for (const b of ethers.getBytes(data)) gas += b === 0 ? 4n : 16n;
  return gas;
}

async function attestationSignature(registry, vehicle, eventId, signer) {
  const chainId = (await ethers.provider.getNetwork()).chainId;
  const inner = ethers.solidityPackedKeccak256(
    ["address", "uint256", "address", "bytes32"],
    [await registry.getAddress(), chainId, vehicle, eventId]
  );
  return signer.signMessage(ethers.getBytes(inner));
}

function eventIdOf(registry, receipt) {
  for (const log of receipt.logs) {
    try {
      const parsed = registry.interface.parseLog(log);
      if (parsed && parsed.name === "LifecycleEventRecorded") return parsed.args.eventId;
    } catch (_) { /* not ours */ }
  }
  throw new Error("LifecycleEventRecorded not emitted");
}

describe("MOBI VID V2 attestEvent: M3 regression (forged-signature path closed, fixed-path gas pinned)", function () {
  async function fixture() {
    const [authority, manufacturer, firstOwner, serviceCenter, dmv, inspection, vehicle] =
      await ethers.getSigners();
    const registry = await (await ethers.getContractFactory(V2_FQN)).deploy();
    await registry.waitForDeployment();
    await registry.authorizeManufacturer(manufacturer.address);
    await registry.authorizeIssuer(manufacturer.address, ROLE.MANUFACTURER);
    await registry.authorizeIssuer(serviceCenter.address, ROLE.SERVICE_CENTER);
    await registry.authorizeIssuer(dmv.address, ROLE.GOVERNMENT_DMV);
    await registry.authorizeIssuer(inspection.address, ROLE.INSPECTION_STATION);
    await registry.connect(manufacturer).registerVehicleBirth(
      vehicle.address, VIN_HASH, "encrypted:VIN", BIRTH_CERT_HASH, firstOwner.address, BIRTH_ATTRS
    );
    return { registry, serviceCenter, dmv, inspection, vehicle };
  }

  async function recordEvent(registry, serviceCenter, vehicle, odometer) {
    const tx = await registry.connect(serviceCenter).recordLifecycleEvent(
      vehicle.address, MAINTENANCE, odometer, DATA_HASH, CRED_HASH, "BC-CAN"
    );
    return eventIdOf(registry, await tx.wait());
  }

  it("vulnerable path closed: a role-holder cannot record another party's (forged) or a garbage attestation", async function () {
    const { registry, serviceCenter, dmv, inspection, vehicle } = await loadFixture(fixture);
    const eventId = await recordEvent(registry, serviceCenter, vehicle, 12_000);

    // The pre-fix exploit: dmv (a role-holder) submits inspection's signature
    // as its own attestation, and a placeholder blob.
    const forged = await attestationSignature(registry, vehicle.address, eventId, inspection);
    await expect(registry.connect(dmv).attestEvent(eventId, vehicle.address, forged))
      .to.be.revertedWith("Invalid attestation signature");

    const blob = ethers.toUtf8Bytes("0xsignature-placeholder");
    await expect(registry.connect(dmv).attestEvent(eventId, vehicle.address, blob))
      .to.be.revertedWithCustomError(registry, "ECDSAInvalidSignatureLength")
      .withArgs(blob.length);

    // A well-formed 65-byte signature by nobody in particular.
    const randomSig = await ethers.Wallet.createRandom().signMessage(ethers.getBytes(eventId));
    await expect(registry.connect(dmv).attestEvent(eventId, vehicle.address, randomSig))
      .to.be.revertedWith("Invalid attestation signature");

    expect((await registry.getEventAttestations(eventId)).length).to.equal(0);

    // Control: the genuine attester's own signature is accepted.
    const valid = await attestationSignature(registry, vehicle.address, eventId, dmv);
    await expect(registry.connect(dmv).attestEvent(eventId, vehicle.address, valid))
      .to.emit(registry, "EventAttested");
    const atts = await registry.getEventAttestations(eventId);
    expect(atts.length).to.equal(1);
    expect(atts[0].attester).to.equal(dmv.address);
  });

  it(`fixed-path gas pinned: execution gas = ${PINNED_EXECUTION_GAS} ± 0 across event ids; gasUsed = 21,000 + calldata + execution`, async function () {
    const { registry, serviceCenter, dmv, vehicle } = await loadFixture(fixture);

    const seen = [];
    for (let i = 0; i < 6; i++) {
      await time.increase(1 + 37 * i); // different block timestamp => different eventId
      const eventId = await recordEvent(registry, serviceCenter, vehicle, 10_000 + i);
      const sig = await attestationSignature(registry, vehicle.address, eventId, dmv);
      const tx = await registry.connect(dmv).attestEvent(eventId, vehicle.address, sig);
      const receipt = await tx.wait();
      const cd = calldataGas(tx.data);
      const exec = receipt.gasUsed - TX_BASE_GAS - cd;
      seen.push({ eventId, gasUsed: receipt.gasUsed, calldata: cd, exec });
      expect(exec, `execution gas for eventId ${eventId}`).to.equal(PINNED_EXECUTION_GAS);
      expect(receipt.gasUsed).to.equal(TX_BASE_GAS + cd + PINNED_EXECUTION_GAS);
    }
    const totals = seen.map((s) => s.gasUsed);
    console.log(
      `        attestEvent gasUsed over ${seen.length} event ids: ` +
      `${totals.join(", ")} (execution ${PINNED_EXECUTION_GAS} each; spread is calldata zero bytes)`
    );
  });
});
