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
    
When you run the script, it will print a summary of how many failure mode codes were loaded from the vocabulary, how many RDF triples were generated, and how many warnings were recorded in the CSV report.

Be careful with file paths. May need to check if files are moved to different locations as the paths have been hardcoded for testing purposes. Adjust the paths in the command above as needed to point to the correct locations of your input CSV, vocabulary TTL, output TTL, and warning CSV files.    
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

#Functions for processing and normalising CSV values, building the failure mode lookup, writing warnings, and converting CSV rows to RDF.

def local_id(value: object, fallback: str = "unnamed") -> str:
    """Create a safe readable local IRI fragment from a CSV value.
        Example:
        "02777 Leach Air Vent" becomes something like:
        "02777_Leach_Air_Vent"

    Why this is needed:
        CSV values often contain spaces, punctuation, or missing values.
        IRIs need safe, predictable text.

    Parameters:
        value:
            The original value from the CSV cell.
        fallback:
            Text to use if the CSV cell is empty or missing.

    Returns:
        A cleaned string that can be used at the end of an IRI.
    
    """
    # If the value is missing, start with an empty string.
    # Otherwise convert the value to text and remove leading/trailing spaces.   
    text = "" if pd.isna(value) else str(value).strip()
    # If the result is empty, use the fallback value instead.
    if not text:
        text = fallback
    # Replace one or more whitespace characters with a single underscore.    
    text = re.sub(r"\s+", "_", text)
    # Replace characters that are not letters, numbers, underscores, or hyphens
    # with underscores. This removes punctuation that could cause IRI problems.
    text = re.sub(r"[^A-Za-z0-9_\-]", "_", text)
    # Replace repeated underscores with one underscore, then remove underscores
    # from the start and end.
    text = re.sub(r"_+", "_", text).strip("_")
    # URL-encode anything that still needs escaping.
    # The 'safe' characters are allowed to remain unchanged.
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
    """Add a literal triple only when the CSV value is non-empty e.g. when the supplied CSV value contains text.

    This prevents empty CSV cells from becoming empty RDF literals.

    Parameters:
        g:
            The RDF graph to add the triple to.
        s:
            The subject IRI of the triple.
        p:
            The predicate/property IRI of the triple.
        value:
            The CSV value to turn into a literal object."""
    # Only add the triple if the value is not missing and is not blank text.
    if not pd.isna(value) and str(value).strip():
        # Add the RDF triple: subject, predicate, object.
        # The object is a Literal because it is text data, not another IRI.
        g.add((s, p, Literal(str(value).strip())))

# This function binds the common prefixes to the RDF graph, which allows the serialized TTL output to use these prefixes instead of full IRIs. This makes the output more readable and compact. The prefixes include 'lis' for the LIS ontology, 'asset' for the assetCore ontology, 'mwo' for the mwoCore ontology, 'i14224' for the ISO 14224 ontology, 'inst' for the instance namespace, and standard RDF, RDFS, OWL, XSD, and DCTERMS prefixes.
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

# This function reads the vocabulary TTL file and builds a lookup dictionary that maps normalised ISO 14224 code labels to their corresponding FailureMode individuals in the RDF graph. It also identifies any duplicate labels that correspond to more than one individual, which would make matching ambiguous. The function returns both the lookup dictionary and the duplicates dictionary for use in the conversion process.
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
    # this code checks to see that the RDF file can be parsed to turtle format, and if not, it prints detailed error information to help diagnose the problem. This is useful because RDF parsing errors can sometimes be cryptic, and this way we can see exactly what went wrong.
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
    # this code iterates through all subjects in the RDF graph that are of type i14224:FailureMode, and for each of those subjects, it looks for their rdfs:label values. It normalises those labels using the normalise_code function, and if the normalised code is not empty, it adds the failure mode individual to a list in the label_to_entities dictionary under that code. This way, we can see which failure mode individuals correspond to each code label.
    # normalise code means to trim whitespace and uppercase the value so that ' brd ' and 'BRD' match the same controlled vocabulary entry. This is important for robust matching of codes from the CSV to the vocabulary, even if there are minor formatting differences.
    for failure_mode in vocab_graph.subjects(RDF.type, I14224.FailureMode):
        for label in vocab_graph.objects(failure_mode, RDFS.label):
            code = normalise_code(label)
            if code:
                label_to_entities[code].append(failure_mode)
    # this code then processes the label_to_entities dictionary to create a lookup dictionary that maps each code to a single FailureMode individual, but only if there is exactly one unique individual for that code. If there are multiple individuals with the same code label, it adds that code and the list of individuals to the duplicates dictionary instead, because it would be ambiguous to match to any one of them.
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
    # this code writes the warnings to a CSV file with the specified fieldnames. Each warning is a dictionary that should contain the keys 'row_number', 'work_order', 'failure_mode_code', 'issue', and 'details'. The CSV will have a header row with these field names, followed by one row for each warning in the warnings iterable.
    # A warning might indicate that a failure mode code from the CSV was not found in the vocabulary, or that it matched multiple entries in the vocabulary, making it ambiguous. This allows users to review and address any issues with the failure mode codes in their source data or vocabulary.
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
    # this code adds metadata about the ontology to the RDF graph, including its type and the ontologies it imports. This is important for making the generated RDF self-describing and for ensuring that it correctly references the relevant vocabularies for LIS14, assetCore, mwoCore, and ISO 14224. The imports statements indicate that this dataset relies on those ontologies for its classes and properties, and tools that process the RDF can automatically retrieve those ontologies if needed.
    ontology_iri = URIRef("https://example.org/autoclave/work-order/instances")
    g.add((ontology_iri, RDF.type, OWL.Ontology))
    g.add((ontology_iri, OWL.imports, URIRef("http://rds.posccaesar.org/ontology/lis14/ont/core")))
    g.add((ontology_iri, OWL.imports, URIRef("https://nlp-tlp.org/ontology/asset/ont/rdl/")))
    g.add((ontology_iri, OWL.imports, URIRef("https://nlp-tlp.org/ontology/mwo/ont/rdl/")))
    g.add((ontology_iri, OWL.imports, URIRef("https://iso14224.org/ontology/i14224/ont/appendixB/")))


def convert(csv_path: Path, vocab_path: Path, out_path: Path, warning_path: Path) -> None:
    """Convert CSV rows to RDF and validate failure mode codes."""
    # this code is the main function that orchestrates the conversion of the CSV data to RDF, while also validating the failure mode codes against the provided vocabulary. It first builds the failure mode lookup and identifies any duplicate codes in the vocabulary. Then it reads the CSV file into a pandas DataFrame and iterates through each row, creating RDF triples for the work order activity, asset, and other properties. When it encounters a failure mode code in the CSV, it uses the lookup to determine if it can link directly to a controlled vocabulary individual, or if it needs to create a local placeholder and record a warning. Finally, it serializes the RDF graph to a TTL file and writes any warnings to a CSV report.
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
        # This code is creating a new RDF individual for each work order activity, using the local_id function to generate a unique and safe IRI fragment based on the "MaintenanceWorkOrderActivity" column from the CSV. It then adds triples to the graph to indicate that this individual is of type MWO.MWOActivity, and it assigns an rdfs:label to it based on the same CSV value. It also adds a description if there is a "WODescription" value in the CSV. This sets up the main entity that represents the work order activity in the RDF graph, which will then be linked to other entities such as assets and failure mode codes.
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
        # This code is extracting the functional location from the CSV row, normalising it, and using it to create or reuse an asset individual in the RDF graph. It uses the local_id function to generate a unique IRI fragment for the asset based on the functional location. It then adds triples to indicate that this asset is of type ASSET.MaintainableAsset, and it assigns an rdfs:label based on the "AssetDescription" column if available, or the functional location if not. It also adds properties for functionalLocation, controlLoopID, and description based on the corresponding CSV columns. Finally, it links the work order activity to this asset using the LIS.hasParticipant property. This way, if multiple work orders reference the same functional location, they will be linked to the same asset individual in the RDF graph.
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

# This code defines the command-line interface for the script, allowing users to specify the input CSV file, the vocabulary TTL file, the output TTL file, and the warning CSV file via command-line arguments. It uses argparse to parse these arguments and provides default paths for testing purposes. The main function then calls the convert function with the provided arguments to perform the conversion and validation.
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

# This code defines the main entry point of the script. It parses the command-line arguments and then calls the convert function with the specified paths for the CSV input, vocabulary TTL, output TTL, and warning CSV. This allows the script to be run from the command line with different input and output files as needed.
def main() -> None:
    args = parse_args()
    convert(args.csv, args.failure_mode_vocab, args.out, args.warnings)

# This ensures that the main function is called when the script is executed directly. If this script is imported as a module in another script, the main function will not be executed automatically, which is a common Python convention for scripts that can be both run directly and imported.
if __name__ == "__main__":
    main()
