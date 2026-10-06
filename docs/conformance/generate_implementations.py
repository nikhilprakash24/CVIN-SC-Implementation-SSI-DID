#!/usr/bin/env python3
"""
Generate W3C DID Test Suite implementation files from this project's resolver.

The official suite (https://github.com/w3c/did-test-suite) tests static test
vectors: for each registered DID method it needs the DID document data model,
its representation and the resolution/document metadata; for each resolver it
needs recorded `resolve` / `resolveRepresentation` executions.

Every value written here is taken UNCHANGED from
    2_w3c-ssi-layer/did-resolution/did_resolver.py :: DIDResolver.resolve(did)
via DIDResolutionResult.to_dict(), and (since stream G-R, 2026-10-04) from
    DIDResolver.resolve_representation(did) via DIDRepresentationResult.to_dict()
for the resolveRepresentation executions and the method file's representation.
Nothing is edited to make tests pass: the metadata keys, the timestamps and
the placeholder key material (`publicKeyHex: "0x..."`) are exactly what the
resolver emits.

G-R adaptation (the only change; inputs, vectors and mapping unchanged): the
resolver no longer emits `error: null` or a `contentType` on resolve(), and
it now has a resolveRepresentation function. So (a) the success assertion
tests for an absent `error` key instead of `error is None`, and (b)
`supportedContentTypes`, the method file's representation entry and the
`resolveRepresentation` execution are taken from resolve_representation()
instead of re-labelling the resolve() output.

Mapping to the suite's input format (see did-example-didwg.json and
resolver-example-didwg.json in the suite):

  * didDocumentDataModel.properties  = didDocument minus "@context"
  * representationSpecificEntries    = {"@context": didDocument["@context"]}
  * representation / didDocumentStream = json.dumps(didDocument), i.e. the
    same serialization the resolver CLI prints (main() -> json.dumps(to_dict()))
  * supportedContentTypes = [contentType of resolve_representation()] - the
    resolver only ever produces "application/did+ld+json".
  * `resolve` executions use the raw resolve() output.
  * `resolveRepresentation` executions use the raw resolve_representation()
    output (default accept). Before G-R the project had no such function and
    the resolve() output, which then carried a contentType, was registered
    under both function names.

No `didParameters` (the resolver does not parse DID URL query parameters), no
`conformingConsumers` (there is no consumer function) and no dereferencer file
(there is no dereference function) are registered.

Usage:
    python3 docs/conformance/generate_implementations.py [<output-dir>] [--ethr-did <did>]

By default the did:ethr entry uses the static fixture
did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678. `--ethr-did` (or the
environment variable CVIN_ETHR_DID) replaces that identifier in the did:ethr
method file and in its resolver executions, e.g. with a DID minted by
MOBIVIDRegistry.getVehicleDID() on a Hardhat chain
(did:ethr:0x7a69:0x<40 hex>). The error-case inputs and the did:mobi / did:nft
entries are not affected. Without the flag the output is unchanged. (Ported
from the sandbox lineage's generator at the 2026-10-06 merge, S7.)
"""

import argparse
import json
import os
import sys
from copy import deepcopy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "2_w3c-ssi-layer", "did-resolution"))

from did_resolver import DIDResolver  # noqa: E402

IMPLEMENTER = "CVIN-SC-Implementation-SSI-DID (Nikhil Prakash, UBC ECE MASc thesis)"

METHODS = {
    "ethr": {
        "did": "did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678",
        "label": "ERC-1056",
        # inputs that exercise the resolver's error path; the expected outcome
        # is what DID Core / DID Resolution say a resolver MUST return.
        "error_cases": [
            ("did:ethr_0x1234", "invalidDidErrorOutcome"),
            ("did:web:example.com", "methodNotSupportedErrorOutcome"),
        ],
    },
    "mobi": {
        "did": "did:mobi:5YJ3E1EA0PF123456",
        "label": "MOBI VID",
        "error_cases": [
            ("did:mobi:", "invalidDidErrorOutcome"),
        ],
    },
    "nft": {
        "did": "did:nft:0x1:0xabc:123",
        "label": "ERC-721",
        "error_cases": [
            ("did:nft:0x1:0xabc", "invalidDidErrorOutcome"),
        ],
    },
}


def resolve(resolver, did):
    """Call the project's resolver and return the raw dict it produces."""
    return resolver.resolve(did).to_dict()


def method_file(method, did, result, rep):
    doc = deepcopy(result["didDocument"])
    context = doc.pop("@context")
    content_type = rep["didResolutionMetadata"]["contentType"]
    return {
        "didMethod": f"did:{method}",
        "implementation": f"CVIN did_resolver.py ({METHODS[method]['label']})",
        "implementer": IMPLEMENTER,
        "supportedContentTypes": [content_type],
        "dids": [did],
        did: {
            "didDocumentDataModel": {"properties": doc},
            content_type: {
                "didDocumentDataModel": {
                    "representationSpecificEntries": {"@context": context}
                },
                "representation": rep["didDocumentStream"],
                "didDocumentMetadata": rep["didDocumentMetadata"],
                "didResolutionMetadata": rep["didResolutionMetadata"],
            },
        },
    }


def resolver_file(method, did, result, rep, resolver):
    executions = []
    outcomes = {
        "defaultOutcome": [],
        "invalidDidErrorOutcome": [],
        "notFoundErrorOutcome": [],
        "representationNotSupportedErrorOutcome": [],
        "methodNotSupportedErrorOutcome": [],
        "deactivatedOutcome": [],
    }

    # 0: resolve()
    outcomes["defaultOutcome"].append(len(executions))
    executions.append({
        "function": "resolve",
        "input": {"did": did, "resolutionOptions": {}},
        "output": {
            "didResolutionMetadata": result["didResolutionMetadata"],
            "didDocument": result["didDocument"],
            "didDocumentMetadata": result["didDocumentMetadata"],
        },
    })

    # 1: resolveRepresentation()
    content_type = rep["didResolutionMetadata"]["contentType"]
    outcomes["defaultOutcome"].append(len(executions))
    executions.append({
        "function": "resolveRepresentation",
        "input": {"did": did, "resolutionOptions": {"accept": content_type}},
        "output": {
            "didResolutionMetadata": rep["didResolutionMetadata"],
            "didDocumentStream": rep["didDocumentStream"],
            "didDocumentMetadata": rep["didDocumentMetadata"],
        },
    })

    # error cases
    for bad_did, outcome in METHODS[method]["error_cases"]:
        r = resolve(resolver, bad_did)
        outcomes[outcome].append(len(executions))
        executions.append({
            "function": "resolve",
            "input": {"did": bad_did, "resolutionOptions": {}},
            "output": {
                "didResolutionMetadata": r["didResolutionMetadata"],
                "didDocument": r["didDocument"],
                "didDocumentMetadata": r["didDocumentMetadata"],
            },
        })

    return {
        "implementation": f"CVIN did_resolver.py ({METHODS[method]['label']})",
        "implementer": IMPLEMENTER,
        "didMethod": f"did:{method}",
        "expectedOutcomes": outcomes,
        "executions": executions,
    }


ETHR_DID_ENV = "CVIN_ETHR_DID"


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Generate W3C DID Test Suite implementation files from did_resolver.py")
    parser.add_argument("output_dir", nargs="?", default=os.path.join(HERE, "implementations"))
    parser.add_argument(
        "--ethr-did", default=os.environ.get(ETHR_DID_ENV) or None, metavar="DID",
        help="did:ethr identifier to register instead of the static fixture "
             f"(default: {METHODS['ethr']['did']}; env {ETHR_DID_ENV})")
    args = parser.parse_args(argv)
    if args.ethr_did is not None and not args.ethr_did.startswith("did:ethr:"):
        parser.error(f"--ethr-did must be a did:ethr identifier, got {args.ethr_did!r}")
    return args


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    out_dir = args.output_dir
    if args.ethr_did:
        # Only the identifier changes; the error cases and the other methods
        # are the same as in the default run.
        METHODS["ethr"]["did"] = args.ethr_did
    os.makedirs(out_dir, exist_ok=True)
    resolver = DIDResolver()
    written = []
    for method, cfg in METHODS.items():
        result = resolve(resolver, cfg["did"])
        assert "error" not in result["didResolutionMetadata"], result
        rep = resolver.resolve_representation(cfg["did"]).to_dict()
        assert "error" not in rep["didResolutionMetadata"], rep
        for name, data in (
            (f"cvin-did-{method}.json", method_file(method, cfg["did"], result, rep)),
            (f"cvin-resolver-{method}.json", resolver_file(method, cfg["did"], result, rep, resolver)),
        ):
            path = os.path.join(out_dir, name)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
            written.append(path)
    for p in written:
        print("wrote", p)


if __name__ == "__main__":
    main()
