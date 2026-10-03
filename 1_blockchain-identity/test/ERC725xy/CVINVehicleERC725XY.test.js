const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CVINVehicleERC725XY (full ERC-725 X+Y smart account, representative)", function () {
    let account, target;
    let owner, newOwner, attacker;

    const TEST_VIN = "1HGBH41JXMN109186";
    const VIN_KEY = ethers.keccak256(ethers.toUtf8Bytes("cvin:vin"));
    const MAKE_KEY = ethers.keccak256(ethers.toUtf8Bytes("cvin:make"));
    const MODEL_KEY = ethers.keccak256(ethers.toUtf8Bytes("cvin:model"));
    const YEAR_KEY = ethers.keccak256(ethers.toUtf8Bytes("cvin:year"));

    // ERC-725 canonical interface IDs (must match the @erc725 reference).
    const IID_ERC165 = "0x01ffc9a7";
    const IID_ERC725X = "0x7545acac";
    const IID_ERC725Y = "0x629aa694";

    beforeEach(async function () {
        [owner, newOwner, attacker] = await ethers.getSigners();

        const Account = await ethers.getContractFactory("CVINVehicleERC725XY");
        account = await Account.connect(owner).deploy(owner.address);
        await account.waitForDeployment();

        const Target = await ethers.getContractFactory("CVINExecuteTarget");
        target = await Target.connect(owner).deploy();
        await target.waitForDeployment();
    });

    describe("Deployment", function () {
        it("deploys with the given initial owner and advertises ERC-725X/Y + ERC-165 (gas sanity)", async function () {
            const receipt = await account.deploymentTransaction().wait();
            console.log(`        [gas] ERC725xy deploy (create identity): ${receipt.gasUsed.toString()}`);

            expect(await account.owner()).to.equal(owner.address);
            expect(await account.supportsInterface(IID_ERC165)).to.be.true;
            expect(await account.supportsInterface(IID_ERC725X)).to.be.true;
            expect(await account.supportsInterface(IID_ERC725Y)).to.be.true;
            expect(await account.supportsInterface("0xffffffff")).to.be.false;
        });

        it("rejects the zero address as initial owner", async function () {
            const Account = await ethers.getContractFactory("CVINVehicleERC725XY");
            await expect(Account.deploy(ethers.ZeroAddress)).to.be.revertedWith(
                "ERC725: owner is the zero address"
            );
        });
    });

    describe("ERC-725Y data store", function () {
        it("setData / getData round-trip and emits DataChanged", async function () {
            const key = ethers.keccak256(ethers.toUtf8Bytes("cvin:firmwareHash"));
            const value = ethers.toUtf8Bytes("sha256:9f86d0818b");

            const tx = await account.connect(owner).setData(key, value);
            const receipt = await tx.wait();
            console.log(`        [gas] ERC725xy setData (update attribute): ${receipt.gasUsed.toString()}`);

            await expect(tx)
                .to.emit(account, "DataChanged")
                .withArgs(key, ethers.hexlify(value));

            expect(await account.getData(key)).to.equal(ethers.hexlify(value));
        });

        it("returns empty bytes for an unset data key", async function () {
            const key = ethers.keccak256(ethers.toUtf8Bytes("cvin:unset"));
            expect(await account.getData(key)).to.equal("0x");
        });

        it("setDataBatch writes multiple keys atomically and getDataBatch reads them back", async function () {
            const keys = [MAKE_KEY, MODEL_KEY, YEAR_KEY];
            const values = [
                ethers.toUtf8Bytes("Honda"),
                ethers.toUtf8Bytes("Civic"),
                ethers.AbiCoder.defaultAbiCoder().encode(["uint256"], [2024]),
            ];

            const tx = await account.connect(owner).setDataBatch(keys, values);
            await tx.wait();

            const readBack = await account.getDataBatch(keys);
            expect(readBack[0]).to.equal(ethers.hexlify(values[0]));
            expect(readBack[1]).to.equal(ethers.hexlify(values[1]));
            expect(readBack[2]).to.equal(ethers.hexlify(values[2]));

            expect(ethers.toUtf8String(await account.getData(MAKE_KEY))).to.equal("Honda");
            expect(ethers.toUtf8String(await account.getData(MODEL_KEY))).to.equal("Civic");
        });

        it("setDataBatch reverts on keys/values length mismatch", async function () {
            await expect(
                account.connect(owner).setDataBatch([MAKE_KEY, MODEL_KEY], [ethers.toUtf8Bytes("x")])
            ).to.be.revertedWith("ERC725Y: keys/values length mismatch");
        });

        it("unauthorized setData reverts (non-owner)", async function () {
            const key = ethers.keccak256(ethers.toUtf8Bytes("cvin:attack"));
            await expect(
                account.connect(attacker).setData(key, ethers.toUtf8Bytes("evil"))
            ).to.be.revertedWith("ERC725: caller is not the owner");
        });
    });

    describe("CVIN vehicle birth attributes", function () {
        it("setVehicleBirthAttributes stores VIN/make/model/year; VIN reads back as a string", async function () {
            await (
                await account
                    .connect(owner)
                    .setVehicleBirthAttributes(TEST_VIN, "Honda", "Civic", 2024)
            ).wait();

            // VIN attribute read-back via the raw ERC-725Y store...
            const storedVin = await account.getData(VIN_KEY);
            expect(ethers.toUtf8String(storedVin)).to.equal(TEST_VIN);
            // ...and via the convenience view.
            expect(await account.getVehicleVIN()).to.equal(TEST_VIN);

            expect(ethers.toUtf8String(await account.getData(MAKE_KEY))).to.equal("Honda");
            expect(ethers.toUtf8String(await account.getData(MODEL_KEY))).to.equal("Civic");
            const yearDecoded = ethers.AbiCoder.defaultAbiCoder().decode(
                ["uint256"],
                await account.getData(YEAR_KEY)
            )[0];
            expect(yearDecoded).to.equal(2024n);
        });

        it("unauthorized setVehicleBirthAttributes reverts (non-owner)", async function () {
            await expect(
                account.connect(attacker).setVehicleBirthAttributes(TEST_VIN, "Honda", "Civic", 2024)
            ).to.be.revertedWith("ERC725: caller is not the owner");
        });
    });

    describe("ERC-725X generic executor", function () {
        it("execute CALL mutates the target contract's state (real side effect)", async function () {
            const OPERATION_CALL = 0;
            const inner = target.interface.encodeFunctionData("setValue", [42]);

            const tx = await account
                .connect(owner)
                .execute(OPERATION_CALL, await target.getAddress(), 0, inner);
            const receipt = await tx.wait();
            console.log(`        [gas] ERC725xy execute CALL: ${receipt.gasUsed.toString()}`);

            // The target's state actually changed...
            expect(await target.value()).to.equal(42n);
            // ...and the caller the target saw was THIS account (proxy execution).
            expect(await target.lastCaller()).to.equal(await account.getAddress());

            await expect(tx)
                .to.emit(account, "Executed")
                .withArgs(
                    OPERATION_CALL,
                    await target.getAddress(),
                    0,
                    inner.slice(0, 10) // 4-byte selector
                );
        });

        it("execute bubbles up the target's revert reason", async function () {
            const OPERATION_CALL = 0;
            const inner = target.interface.encodeFunctionData("willRevert", []);
            await expect(
                account.connect(owner).execute(OPERATION_CALL, await target.getAddress(), 0, inner)
            ).to.be.revertedWith("CVINExecuteTarget: forced revert");
        });

        it("execute reverts on an unknown operation type", async function () {
            await expect(
                account.connect(owner).execute(9, await target.getAddress(), 0, "0x")
            ).to.be.revertedWith("ERC725X: unknown operation type");
        });

        it("unauthorized execute reverts (non-owner)", async function () {
            const inner = target.interface.encodeFunctionData("setValue", [7]);
            await expect(
                account.connect(attacker).execute(0, await target.getAddress(), 0, inner)
            ).to.be.revertedWith("ERC725: caller is not the owner");
            // ...and the target was never touched.
            expect(await target.value()).to.equal(0n);
        });
    });

    describe("Ownership transfer (key rotation)", function () {
        it("transferOwnership rotates control: new owner can setData, old owner cannot", async function () {
            const tx = await account.connect(owner).transferOwnership(newOwner.address);
            const receipt = await tx.wait();
            console.log(`        [gas] ERC725xy transferOwnership: ${receipt.gasUsed.toString()}`);

            await expect(tx)
                .to.emit(account, "OwnershipTransferred")
                .withArgs(owner.address, newOwner.address);
            expect(await account.owner()).to.equal(newOwner.address);

            // New owner CAN write data.
            const key = ethers.keccak256(ethers.toUtf8Bytes("cvin:postRotation"));
            await expect(account.connect(newOwner).setData(key, ethers.toUtf8Bytes("ok"))).to.not.be
                .reverted;
            expect(ethers.toUtf8String(await account.getData(key))).to.equal("ok");

            // Old owner CANNOT write data anymore.
            await expect(
                account.connect(owner).setData(key, ethers.toUtf8Bytes("stale"))
            ).to.be.revertedWith("ERC725: caller is not the owner");

            // Old owner also cannot execute.
            const inner = target.interface.encodeFunctionData("setValue", [99]);
            await expect(
                account.connect(owner).execute(0, await target.getAddress(), 0, inner)
            ).to.be.revertedWith("ERC725: caller is not the owner");
        });

        it("transferOwnership rejects the zero address and non-owner callers", async function () {
            await expect(
                account.connect(owner).transferOwnership(ethers.ZeroAddress)
            ).to.be.revertedWith("ERC725: new owner is the zero address");
            await expect(
                account.connect(attacker).transferOwnership(attacker.address)
            ).to.be.revertedWith("ERC725: caller is not the owner");
        });
    });
});
