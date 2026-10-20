import { EthrDID } from 'ethr-did'

const keypair = EthrDID.createKeyPair()
const ethrDid = new EthrDID({...keypair})
// this creates a DID like:
// did:ethr:0x02ac49094591d32a4e2f93f3368da2d7d827e987ce6cdb3bd3b8a3390fde8fc33b
console.log(ethrDid)
//---------------------
let chainNameOrId = 'goerli' // you can use the network name for the most popular [test] networks.
const ethrDidOnGoerliNamed = new EthrDID({...keypair, chainNameOrId})
// did:ethr:goerli:0x02ac49094591d32a4e2f93f3368da2d7d827e987ce6cdb3bd3b8a3390fde8fc33b
console.log(ethrDidOnGoerliNamed)


//----------------------
import { Resolver } from 'did-resolver'
import { getResolver } from 'ethr-did-resolver'

// RPC endpoint is supplied by the environment; no credential is committed.
const rpcUrl = process.env.ETH_RPC_URL;
const didResolver = new Resolver(getResolver({ rpcUrl, name: "goerli" }));

const didDocument = (await didResolver.resolve(ethrDidOnGoerliNamed.did)).didDocument
console.log(didDocument)

//--------------------
// const { Web3 } = require('web3');
import { Web3 } from 'web3'
const web3 = new Web3('https://ethereum-goerli.publicnode.com');
const didGoerliOwner = await ethrDidOnGoerliNamed.lookupOwner()
console.log(didGoerliOwner)

