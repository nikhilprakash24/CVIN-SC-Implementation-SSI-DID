"use strict";
const { ERC1056Adapter } = require("./erc1056.adapter");
const { ERC1056WrapperAdapter } = require("./erc1056w.adapter");
const { ERC721Adapter } = require("./erc721.adapter");
const { ERC725Adapter } = require("./erc725.adapter");
const { ERC735Adapter } = require("./erc735.adapter");
const { ERC1155Adapter } = require("./erc1155.adapter");

// Column order of every comparison table. Substrates without an adapter on the
// trunk are listed so tables print an explicit "not implemented" cell (audit F1).
const ALL_SUBSTRATES = [
  { id: "erc1056", label: "ERC-1056" },
  { id: "erc1056w", label: "ERC-1056 (wrapper)" },
  { id: "erc721", label: "ERC-721" },
  { id: "erc725", label: "ERC-725" },
  { id: "erc735", label: "ERC-735" },
  { id: "erc1155", label: "ERC-1155" },
  { id: "erc725xy", label: "ERC-725xy" },
  { id: "lsp8", label: "LSP8" },
  { id: "erc4337", label: "ERC-4337" },
  { id: "cvin", label: "CVIN-Combined" },
];

const ADAPTERS = { erc1056: ERC1056Adapter, erc1056w: ERC1056WrapperAdapter, erc721: ERC721Adapter, erc725: ERC725Adapter, erc735: ERC735Adapter, erc1155: ERC1155Adapter };

module.exports = { ADAPTERS, ALL_SUBSTRATES };
