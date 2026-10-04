#!/usr/bin/env python3
"""
Generate W3C DID Test Suite implementation files from this project's resolver.

The official suite (https://github.com/w3c/did-test-suite) tests static test
vectors: for each registered DID method it needs the DID document data model,
its representation and the resolution/document metadata; for each resolver it
needs recorded `resolve` / `resolveRepresentation` executions.

Every value written here is taken UNCHANGED from
    2_w3c-ssi-layer/did-resolution/did_resolver.py ::
        DIDResolver.resolve(did)                      (resolve executions)
        DIDResolver.resolve_representation(did, accept) (resolveRepresentation
                                                         executions, method files)
via DIDResolutionResult.to_dict(). Nothing is edited to make tests pass: the
metadata structures (`retrieved`, the XML-Datetime `created`, `versionId`,
the `error` / `errorMessage` pair on failures), the serialised document and
the placeholder key material (`publicKeyHex: "0x..."`) are exactly what the
resolver emits.

Mapping to the suite's input format (see did-example-didwg.json and
resolver-example-didwg.json in the suite):

  * didDocumentDataModel.properties  = didDocument minus "@context"
  * representationSpecificEntries    = {"@context": didDocument["@context"]}
  * representation / didDocumentStream = didDocumentStream of
    resolve_representation(), i.e. json.dumps(didDocument) - the same
    serialization the resolver CLI prints (main() -> json.dumps(to_dict()))
  * supportedContentTypes = [didResolutionMetadata.contentType of the
    resolveRepresentation result] - the resolver only ever produces
    "application/did+ld+json".
  * `resolve` executions use the raw resolve() output (no contentType).
  * `resolveRepresentation` executions use the raw resolve_representation()
    output (didDocumentStream + contentType).
  * The method file's per-content-type block carries the metadata of the
    resolveRepresentation result (which includes contentType), as in the
    WG example.

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
entries are not affected. Without the flag the output is unchanged.
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
    """Call the project's resolve() and return the raw dict it produces."""
    return resolver.resolve(did).to_dict()


def resolve_representation(resolver, did, accept=None):
    """Call the project's resolve_representation() and return the raw dict."""
    return resolver.resolve_representation(did, accept).to_dict()


def method_file(method, did, result, representation):
    doc = deepcopy(result["didDocument"])
    context = doc.pop("@context")
    content_type = representation["didResolutionMetadata"]["contentType"]
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
                "representation": representation["didDocumentStream"],
                "didDocumentMetadata": representation["didDocumentMetadata"],
                "didResolutionMetadata": representation["didResolutionMetadata"],
            },
        },
    }


def resolver_file(method, did, result, representation, resolver):
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
    content_type = representation["didResolutionMetadata"]["contentType"]
    outcomes["defaultOutcome"].append(len(executions))
    executions.append({
        "function": "resolveRepresentation",
        "input": {"did": did, "resolutionOptions": {"accept": content_type}},
        "output": {
            "didResolutionMetadata": representation["didResolutionMetadata"],
            "didDocumentStream": representation["didDocumentStream"],
            "didDocumentMetadata": representation["didDocumentMetadata"],
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
        representation = resolve_representation(resolver, cfg["did"])
        assert "error" not in representation["didResolutionMetadata"], representation
        for name, data in (
            (f"cvin-did-{method}.json",
             method_file(method, cfg["did"], result, representation)),
            (f"cvin-resolver-{method}.json",
             resolver_file(method, cfg["did"], result, representation, resolver)),
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
