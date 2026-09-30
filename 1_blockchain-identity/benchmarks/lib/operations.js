"use strict";
// Canonical operation catalogue (docs/CVIN-DATA-COLLECTION-FRAMEWORK.md §2).
// Order here is the row order of every comparison table.

const OPERATIONS = [
  { id: "C1_create_identity",          cls: "CREATE", kind: "tx",   core: true,  semantic: "Create vehicle identity bound to VIN" },
  { id: "C2_create_with_attributes",   cls: "CREATE", kind: "tx",   core: true,  semantic: "Create + MOBI VID-I birth-certificate attributes" },
  { id: "R1_resolve_owner",            cls: "READ",   kind: "read", core: true,  semantic: "Resolve controller of identity" },
  { id: "R2_resolve_by_vin",           cls: "READ",   kind: "read", core: true,  semantic: "VIN → identity" },
  { id: "R3_resolve_document",         cls: "READ",   kind: "read", core: true,  semantic: "Build full DID Document" },
  { id: "R4_verify_delegate",          cls: "READ",   kind: "read", core: true,  semantic: "Is key authorised to sign?" },
  { id: "U1_rotate_controller",        cls: "UPDATE", kind: "tx",   core: true,  semantic: "Change controlling key" },
  { id: "U2_add_delegate",             cls: "UPDATE", kind: "tx",   core: true,  semantic: "Authorise additional signing key (with TTL)" },
  { id: "U3_set_attribute",            cls: "UPDATE", kind: "tx",   core: true,  semantic: "Publish/change one attribute (64 B)" },
  { id: "U4_transfer_vehicle",         cls: "UPDATE", kind: "tx",   core: true,  semantic: "Ownership transfer (MOBI VID-II)" },
  { id: "U5_meta_tx",                  cls: "UPDATE", kind: "tx",   core: false, semantic: "Relayed signed attribute update" },
  { id: "D1_revoke_delegate",          cls: "DELETE", kind: "tx",   core: true,  semantic: "Remove signing key" },
  { id: "D2_revoke_attribute",         cls: "DELETE", kind: "tx",   core: true,  semantic: "Retract attribute" },
  { id: "D3_deactivate_identity",      cls: "DELETE", kind: "tx",   core: true,  semantic: "End-of-life deactivation" },
  { id: "V1_issuer_key_anchor",        cls: "CREATE", kind: "tx",   core: true,  semantic: "Issuer publishes verification key" },
  { id: "V3_anchor_status",            cls: "CREATE", kind: "tx",   core: true,  semantic: "Anchor credential status on-chain" },
  { id: "V5_revoke_credential",        cls: "DELETE", kind: "tx",   core: true,  semantic: "Revoke credential" },
  { id: "V6_status_check",             cls: "READ",   kind: "read", core: true,  semantic: "Is credential revoked?" },
];

const byId = Object.fromEntries(OPERATIONS.map((o) => [o.id, o]));

module.exports = { OPERATIONS, byId };
