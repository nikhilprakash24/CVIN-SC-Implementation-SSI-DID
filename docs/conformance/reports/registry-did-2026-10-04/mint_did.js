// Deploys MOBIVIDRegistry on the in-process Hardhat network (chainId 31337),
// registers a vehicle birth and prints the DID the contract mints for it.
//   cd 1_blockchain-identity && npx hardhat run <this file>
// The script lives outside the Hardhat project, so `require("hardhat")` is not
// resolvable from here; `hardhat run` injects the environment as global `hre`.
const hre = globalThis.hre || require("hardhat");
const { ethers } = hre;

async function main() {
  const [deployer] = await ethers.getSigners();
  const Registry = await ethers.getContractFactory(
    "contracts/MOBI/MOBIVIDRegistry.sol:MOBIVIDRegistry"
  );
  const registry = await Registry.deploy();
  await registry.waitForDeployment();

  const vehicle = ethers.Wallet.createRandom().address;
  const firstOwner = deployer.address;
  const vinHash = ethers.keccak256(ethers.toUtf8Bytes("1HGBH41JXMN109186:salt"));
  const certHash = ethers.keccak256(ethers.toUtf8Bytes("cert"));

  const tx = await registry.registerVehicleBirth(
    vehicle, vinHash, "enc:vin", certHash, firstOwner, "0x"
  );
  const receipt = await tx.wait();

  const did = await registry.getVehicleDID(vehicle);
  const { chainId } = await ethers.provider.getNetwork();

  console.log(JSON.stringify({
    contract: "contracts/MOBI/MOBIVIDRegistry.sol:MOBIVIDRegistry",
    registry: await registry.getAddress(),
    deployer: deployer.address,
    vehicle,
    firstOwner,
    vinHash,
    birthCertHash: certHash,
    registerTxHash: receipt.hash,
    registerBlock: receipt.blockNumber,
    chainId: chainId.toString(),
    chainIdHex: "0x" + chainId.toString(16),
    did,
  }, null, 2));
}

main().catch((e) => { console.error(e); process.exit(1); });
