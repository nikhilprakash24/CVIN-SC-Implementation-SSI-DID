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
    python3 docs/conformance/generate_implementations.py <output-dir>
"""

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


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "implementations")
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
