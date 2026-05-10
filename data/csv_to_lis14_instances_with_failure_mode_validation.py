"""
Generate LIS14/assetCore/mwoCore-aligned RDF instance data from a CSV file,
while validating ISO 14224 failure mode codes against a controlled vocabulary TTL file.

What this script does
---------------------
1. Loads the work order CSV file.
2. Loads an ISO 14224 vocabulary TTL file, for example vocab14224_appendixB.ttl.
3. Builds a lookup table from rdfs:label codes, for example "BRD", to ISO 14224
   failure mode individuals, for example i14224:breakdown.
4. For each CSV row:
   - creates a work order activity individual;
   - creates or reuses the asset individual;
   - validates ISO14224FailureModeCode;
   - if the code is valid, links the work order directly to the ISO 14224 individual;
   - if the code is not valid, creates a local placeholder code individual and records
     the problem in a warning CSV report.

Typical usage
-------------
pip install pandas rdflib
Make sure the input CSV and vocabulary TTL files are available at the specified paths, then run:

python csv_to_lis14_instances_with_failure_mode_validation.py `
    --csv "C:\\Users\\00040628\\LocalData\\GitHub\\14224ontologies_public\\data\\AutoclaveWorkOrderData.csv" `
    --failure-mode-vocab "C:\\Users\\00040628\\LocalData\\GitHub\\14224ontologies_public\\inDevelopment\\vocab14224_appendixB.ttl" `
    --out "C:\\Users\\00040628\\LocalData\\GitHub\\14224ontologies_public\\data\\autoclave-workorder-instances.ttl" `
    --warnings "C:\\Users\\00040628\\LocalData\\GitHub\\14224ontologies_public\\data\\unmapped-failure-mode-codes.csv"
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from urllib.parse import quote

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD

# Ontology namespaces
LIS = Namespace("http://rds.posccaesar.org/ontology/lis14/rdl/")
ASSET = Namespace("https://nlp-tlp.org/ontology/asset/rdl/")
MWO = Namespace("https://nlp-tlp.org/ontology/mwo/rdl/")
I14224 = Namespace("https://iso14224.org/ontology/i14224/rdl/")

# Instance namespace for this generated dataset. Change to your own persistent base IRI.
INST = Namespace("https://example.org/autoclave/work-order/instance/")


def local_id(value: object, fallback: str = "unnamed") -> str:
    """Create a safe readable local IRI fragment from a CSV value."""
    text = "" if pd.isna(value) else str(value).strip()
    if not text:
        text = fallback
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^A-Za-z0-9_\-]", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return quote(text or fallback, safe="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-.")


def normalise_code(value: object) -> str:
    """Normalise a code value for lookup.

    ISO 14224 failure mode codes are usually uppercase strings such as BRD.
    This function trims whitespace and uppercases the value so that ' brd ' and
    'BRD' match the same controlled vocabulary entry.
    """
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def add_if_text(g: Graph, s: URIRef, p: URIRef, value: object) -> None:
    """Add a literal triple only when the CSV value is non-empty."""
    if not pd.isna(value) and str(value).strip():
        g.add((s, p, Literal(str(value).strip())))


def bind_prefixes(g: Graph) -> None:
    """Bind common prefixes used in the generated TTL output."""
    g.bind("lis", LIS)
    g.bind("asset", ASSET)
    g.bind("mwo", MWO)
    g.bind("i14224", I14224)
    g.bind("inst", INST)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("dcterms", DCTERMS)


def build_failure_mode_lookup(vocab_path: Path) -> Tuple[Dict[str, URIRef], Dict[str, List[URIRef]]]:
    """Build a lookup from ISO 14224 code label to FailureMode individual.

    Returns
    -------
    lookup:
        A dictionary such as {'BRD': URIRef('.../breakdown')}.
    duplicates:
        Any labels that occur on more than one FailureMode individual. Duplicate
        labels are not used for matching because they are ambiguous.
    """
    """
    vocab_graph = Graph()
    vocab_graph.parse(vocab_path, format="turtle")
    """
    vocab_graph = Graph()
    
    try:
        vocab_graph.parse(vocab_path, format="turtle")
    except Exception as e:
        import traceback

        print(f"\nCould not parse RDF file: {vocab_path}")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception: {e}")

        traceback.print_exc()

        raise

    label_to_entities: Dict[str, List[URIRef]] = defaultdict(list)

    for failure_mode in vocab_graph.subjects(RDF.type, I14224.FailureMode):
        for label in vocab_graph.objects(failure_mode, RDFS.label):
            code = normalise_code(label)
            if code:
                label_to_entities[code].append(failure_mode)

    lookup: Dict[str, URIRef] = {}
    duplicates: Dict[str, List[URIRef]] = {}

    for code, entities in label_to_entities.items():
        unique_entities = list(dict.fromkeys(entities))
        if len(unique_entities) == 1:
            lookup[code] = unique_entities[0]
        else:
            duplicates[code] = unique_entities

    return lookup, duplicates


def write_warnings(path: Path, warnings: Iterable[dict]) -> None:
    """Write validation warnings to CSV."""
    fieldnames = [
        "row_number",
        "work_order",
        "failure_mode_code",
        "issue",
        "details",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(warnings)


def add_ontology_header(g: Graph) -> None:
    """Add ontology metadata and imports to the generated graph."""
    ontology_iri = URIRef("https://example.org/autoclave/work-order/instances")
    g.add((ontology_iri, RDF.type, OWL.Ontology))
    g.add((ontology_iri, OWL.imports, URIRef("http://rds.posccaesar.org/ontology/lis14/ont/core")))
    g.add((ontology_iri, OWL.imports, URIRef("https://nlp-tlp.org/ontology/asset/ont/rdl/")))
    g.add((ontology_iri, OWL.imports, URIRef("https://nlp-tlp.org/ontology/mwo/ont/rdl/")))
    g.add((ontology_iri, OWL.imports, URIRef("https://iso14224.org/ontology/i14224/ont/appendixB/")))


def convert(csv_path: Path, vocab_path: Path, out_path: Path, warning_path: Path) -> None:
    """Convert CSV rows to RDF and validate failure mode codes."""
    failure_mode_lookup, duplicate_failure_mode_codes = build_failure_mode_lookup(vocab_path)

    df = pd.read_csv(csv_path)

    g = Graph()
    bind_prefixes(g)
    add_ontology_header(g)

    warnings: List[dict] = []

    # Record duplicate controlled-vocabulary labels as warnings because they make
    # label-based matching ambiguous.
    for code, entities in duplicate_failure_mode_codes.items():
        warnings.append(
            {
                "row_number": "",
                "work_order": "",
                "failure_mode_code": code,
                "issue": "DUPLICATE_CONTROLLED_VOCABULARY_LABEL",
                "details": "More than one i14224:FailureMode individual has this rdfs:label: "
                + "; ".join(str(e) for e in entities),
            }
        )

    for i, row in df.iterrows():
        csv_row_number = i + 2  # +2 because pandas is zero-based and CSV row 1 is the header.
        wo_label = str(row["MaintenanceWorkOrderActivity"]).strip()
        wo_id = local_id(wo_label, f"WO_{i + 1}")
        wo = INST[wo_id]

        # Main row anchor: one work order activity per CSV row.
        g.add((wo, RDF.type, MWO.MWOActivity))
        g.add((wo, RDFS.label, Literal(wo_label)))
        add_if_text(g, wo, DCTERMS.description, row.get("WODescription"))

        # Date as a LIS temporal region plus a temporal datum.
        if not pd.isna(row.get("Date")) and str(row["Date"]).strip():
            date_text = str(row["Date"]).strip()
            instant = INST[f"Instant_{wo_id}"]
            date_datum = INST[f"DateDatum_{wo_id}"]
            g.add((instant, RDF.type, LIS.InstantRegion))
            g.add((instant, RDFS.label, Literal(f"date of {wo_label}")))
            g.add((wo, LIS.hasTemporalRegion, instant))
            g.add((date_datum, RDF.type, LIS.TemporalDatum))
            g.add((date_datum, RDFS.label, Literal(f"date datum for {wo_label}")))
            g.add((date_datum, LIS.temporalValue, Literal(date_text, datatype=XSD.date)))
            g.add((date_datum, LIS.quantifiesTemporalRegion, instant))
            g.add((wo, LIS.representedIn, date_datum))

        # Asset from FunctionalLocation; reuse same asset node across rows.
        floc_raw = row.get("FunctionalLocation")
        floc = "" if pd.isna(floc_raw) else str(floc_raw).strip()
        asset_id = local_id(floc, f"Asset_{i + 1}")
        asset = INST[f"Asset_{asset_id}"]
        g.add((asset, RDF.type, ASSET.MaintainableAsset))
        label = str(row.get("AssetDescription", "")).strip() if not pd.isna(row.get("AssetDescription")) else floc
        if label:
            g.add((asset, RDFS.label, Literal(label)))
        add_if_text(g, asset, ASSET.functionalLocation, floc)
        add_if_text(g, asset, ASSET.controlLoopID, row.get("ControlLoopID"))
        add_if_text(g, asset, DCTERMS.description, row.get("AssetDescription"))
        g.add((wo, LIS.hasParticipant, asset))

        # Work order type as reusable named individual/code object.
        if not pd.isna(row.get("WOOrderType")) and str(row["WOOrderType"]).strip():
            code = str(row["WOOrderType"]).strip()
            wo_type = INST[f"WOOrderType_{local_id(code)}"]
            g.add((wo_type, RDF.type, MWO.MWOActivityType))
            g.add((wo_type, RDFS.label, Literal(code)))
            g.add((wo, MWO.hasWorkOrderType, wo_type))

        # Failure mode validation and linking.
        raw_failure_mode_code = row.get("ISO14224FailureModeCode")
        failure_mode_code = normalise_code(raw_failure_mode_code)

        if failure_mode_code:
            if failure_mode_code in failure_mode_lookup:
                # Preferred result: link directly to the controlled vocabulary individual.
                # Example: inst:WO_123 mwo:hasFailureModeCode i14224:breakdown .
                g.add((wo, MWO.hasFailureModeCode, failure_mode_lookup[failure_mode_code]))
            elif failure_mode_code in duplicate_failure_mode_codes:
                # Do not guess when the controlled vocabulary contains duplicate labels.
                local_failure_code = INST[f"UnresolvedFailureModeCode_{local_id(failure_mode_code)}"]
                g.add((local_failure_code, RDF.type, MWO.MWOFailureModeCode))
                g.add((local_failure_code, RDFS.label, Literal(failure_mode_code)))
                g.add((wo, MWO.hasFailureModeCode, local_failure_code))
                warnings.append(
                    {
                        "row_number": csv_row_number,
                        "work_order": wo_label,
                        "failure_mode_code": failure_mode_code,
                        "issue": "AMBIGUOUS_FAILURE_MODE_CODE",
                        "details": "The code exists in the vocabulary but matches more than one i14224:FailureMode individual.",
                    }
                )
            else:
                # Keep the source data visible in the RDF, but mark it as unresolved
                # and report it in the warning CSV.
                local_failure_code = INST[f"UnmappedFailureModeCode_{local_id(failure_mode_code)}"]
                g.add((local_failure_code, RDF.type, MWO.MWOFailureModeCode))
                g.add((local_failure_code, RDFS.label, Literal(failure_mode_code)))
                g.add((wo, MWO.hasFailureModeCode, local_failure_code))
                warnings.append(
                    {
                        "row_number": csv_row_number,
                        "work_order": wo_label,
                        "failure_mode_code": failure_mode_code,
                        "issue": "UNMAPPED_FAILURE_MODE_CODE",
                        "details": "No i14224:FailureMode individual with this rdfs:label was found in the vocabulary file.",
                    }
                )

        # Actual cost as a datum node.
        if not pd.isna(row.get("ActualCost")):
            cost = INST[f"ActualCostDatum_{wo_id}"]
            g.add((cost, RDF.type, MWO.ActualCostDatum))
            g.add((cost, RDFS.label, Literal(f"actual cost for {wo_label}")))
            g.add((cost, LIS.datumValue, Literal(row["ActualCost"], datatype=XSD.decimal)))
            g.add((wo, MWO.hasActualCost, cost))

        # Work hours as a datum node.
        if not pd.isna(row.get("WorkHours")):
            hours = INST[f"WorkHoursDatum_{wo_id}"]
            g.add((hours, RDF.type, MWO.WorkHoursDatum))
            g.add((hours, RDFS.label, Literal(f"work hours for {wo_label}")))
            g.add((hours, LIS.datumValue, Literal(row["WorkHours"], datatype=XSD.decimal)))
            g.add((wo, MWO.hasWorkHours, hours))

    g.serialize(destination=out_path, format="turtle")
    write_warnings(warning_path, warnings)

    print(f"Loaded {len(failure_mode_lookup)} unique ISO 14224 failure mode codes from {vocab_path}")
    print(f"Wrote RDF: {out_path} with {len(g)} triples")
    print(f"Wrote warning report: {warning_path} with {len(warnings)} warning rows")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert work order CSV data to LIS14/assetCore/mwoCore-aligned RDF and validate ISO 14224 failure mode codes."
    )
    parser.add_argument("--csv", type=Path, default=Path("C:\\Users\\00040628\\LocalData\\GitHub\\14224ontologies_public\\data\\AutoclaveWorkOrderData.csv"), help="Input work order CSV file")
    parser.add_argument(
        "--failure-mode-vocab",
        type=Path,
        default=Path("C:\\Users\\00040628\\LocalData\\GitHub\\14224ontologies_public\\inDevelopment\\vocab14224_appendixB.ttl"),
        help="ISO 14224 failure mode vocabulary TTL file",
    )
    parser.add_argument("--out", type=Path, default=Path("C:\\Users\\00040628\\LocalData\\GitHub\\14224ontologies_public\\data\\autoclave-workorder-instances.ttl"), help="Output TTL file")
    parser.add_argument(
        "--warnings",
        type=Path,
        default=Path("C:\\Users\\00040628\\LocalData\\GitHub\\14224ontologies_public\\data\\unmapped-failure-mode-codes.csv"),
        help="Output CSV report for unmapped or ambiguous failure mode codes",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    convert(args.csv, args.failure_mode_vocab, args.out, args.warnings)


if __name__ == "__main__":
    main()
