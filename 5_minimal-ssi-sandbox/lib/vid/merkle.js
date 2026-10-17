// Sorted-pair keccak Merkle tree matching BatchAnchorRegistry.verifyInclusion.
// Leaves are bytes32 hex strings. Odd levels duplicate the last node.
const { ethers } = require("ethers");

function pairHash(a, b) {
  const [x, y] = a.toLowerCase() < b.toLowerCase() ? [a, b] : [b, a];
  return ethers.keccak256(ethers.concat([x, y]));
}

function buildTree(leaves) {
  if (leaves.length === 0) throw new Error("empty tree");
  const levels = [[...leaves]];
  while (levels[levels.length - 1].length > 1) {
    const prev = levels[levels.length - 1], next = [];
    for (let i = 0; i < prev.length; i += 2) next.push(pairHash(prev[i], prev[i + 1] ?? prev[i]));
    levels.push(next);
  }
  return { root: levels[levels.length - 1][0], levels };
}

function proofFor(tree, index) {
  const proof = [];
  let i = index;
  for (let l = 0; l < tree.levels.length - 1; l++) {
    const level = tree.levels[l];
    const sib = i ^ 1;
    proof.push(level[sib] ?? level[i]);
    i = Math.floor(i / 2);
  }
  return proof;
}

function verify(root, leaf, proof) {
  let h = leaf;
  for (const p of proof) h = pairHash(h, p);
  return h === root;
}

module.exports = { pairHash, buildTree, proofFor, verify };
