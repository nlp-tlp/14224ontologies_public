from pathlib import Path
import argparse
import csv
import re
import sys

from rdflib import Graph, Namespace, RDF, RDFS, URIRef


FMEA = Namespace("https://example.org/ontology/fmea/ont/")
I14224 = Namespace("https://iso14224.org/ontology/i14224/rdl/")


REPORT_ROWS = [
    "1. FM code blank",
    "2. FM code not in ISO 14224 Annex B",
    "3. FM valid but not allowed for equipment class",
    "4. FM valid but class-specific check could not run (equipment class blank/unresolved)",
    "5. Compliant (FM defined and allowed for equipment class)",
    "6. Total worksheet rows checked",
]


# Default mapping for the equipment codes present in the current FMEA TTL file.
# Add to this dictionary if your data starts using more ISO 14224 equipment codes.
DEFAULT_EQUIPMENT_CODE_TO_CLASS = {
    "CL": "ControlUnit",
    "VA": "Valve",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Summarise ISO 14224 FMEA failure-mode validation results as a CSV table. "
            "This version checks compliance directly from the RDF triples and does not require pyshacl."
        )
    )

    parser.add_argument(
        "--data",
        required=True,
        help="FMEA instance TTL file, e.g. AutoclaveControlLoopFMEA_instances.ttl",
    )

    parser.add_argument(
        "--allowed",
        required=True,
        help="Allowed failure modes TTL file, e.g. i14224_appendixB_allowed_failure_modes.ttl",
    )

    parser.add_argument(
        "--out",
        default="ISO14224_FM_Code_Check_report_completed.csv",
        help="Output CSV report filename",
    )

    parser.add_argument(
        "--details-out",
        default="ISO14224_FM_Code_Check_row_details.csv",
        help="Optional row-by-row details CSV filename",
    )

    parser.add_argument(
        "--use-component-type-fallback",
        action="store_true",
        help=(
            "Also use fmea:hasComponent / rdf:type as the equipment class when no "
            "i14224:hasEquipmentClass, i14224:hasFailedEquipment, or i14224:hasEquipmentCode is present. "
            "By default this is off, so the report matches spreadsheet equipment-code checking."
        ),
    )

    return parser.parse_args()


def require_file(path_string):
    path = Path(path_string)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path


def local_name(uri):
    text = str(uri)
    if "#" in text:
        return text.rsplit("#", 1)[1]
    return text.rstrip("/").rsplit("/", 1)[-1]


def code_uri_to_class_uri(code_uri):
    code = local_name(code_uri)
    class_name = DEFAULT_EQUIPMENT_CODE_TO_CLASS.get(code)
    if class_name is None:
        return None
    return I14224[class_name]


def get_row_number(graph, subject):
    row_values = list(graph.objects(subject, FMEA.hasSourceRowNumber))
    if row_values:
        try:
            return int(str(row_values[0]))
        except ValueError:
            return str(row_values[0])

    match = re.search(r"row[_-](\d+)", str(subject), flags=re.IGNORECASE)
    if match:
        return int(match.group(1))

    return str(subject)


def sort_rows(row_numbers):
    def sort_key(value):
        try:
            return (0, int(value))
        except Exception:
            return (1, str(value))

    return sorted(set(row_numbers), key=sort_key)


def format_row_numbers(row_numbers):
    return ", ".join(str(r) for r in sort_rows(row_numbers))


def get_fmea_entries(graph):
    entries = set(graph.subjects(RDF.type, FMEA.FMEAEntry))
    if not entries:
        entries = set(graph.subjects(FMEA.hasSourceRowNumber, None))
    return entries


def get_literal_value(graph, subject, predicate):
    values = list(graph.objects(subject, predicate))
    if not values:
        return ""
    return str(values[0]).strip()


def has_blank_fm_code(graph, entry):
    values = list(graph.objects(entry, FMEA.hasFailureModeCodeLiteral))
    if not values:
        return True
    return not any(str(value).strip() for value in values)


def get_failure_modes(graph, entry):
    return list(graph.objects(entry, I14224.hasFailureMode))


def get_equipment_classes(graph, entry, use_component_type_fallback=False):
    """
    Find the ISO 14224 equipment class for an FMEA row.

    Supported patterns:

    1. Direct class on the row:
       ?entry i14224:hasEquipmentClass ?equipmentClass .

    2. Failed equipment typed with the class:
       ?entry i14224:hasFailedEquipment ?equipment .
       ?equipment rdf:type ?equipmentClass .

    3. Equipment code on the row, mapped here to the class:
       ?entry i14224:hasEquipmentCode i14224:VA .
       VA -> i14224:Valve

    4. Optional component type fallback, only when --use-component-type-fallback is supplied:
       ?entry fmea:hasComponent ?component .
       ?component rdf:type ?equipmentClass .
    """

    equipment_classes = set()

    # 1. Direct equipment class
    equipment_classes.update(graph.objects(entry, I14224.hasEquipmentClass))

    # 2. Failed equipment type
    for equipment in graph.objects(entry, I14224.hasFailedEquipment):
        equipment_classes.update(graph.objects(equipment, RDF.type))

    # 3. Equipment code mapped to equipment class
    for code_uri in graph.objects(entry, I14224.hasEquipmentCode):
        class_uri = code_uri_to_class_uri(code_uri)
        if class_uri is not None:
            equipment_classes.add(class_uri)

    # 4. Optional component type fallback
    if use_component_type_fallback:
        for component in graph.objects(entry, FMEA.hasComponent):
            for component_type in graph.objects(component, RDF.type):
                if component_type != I14224.MaintainableItem:
                    equipment_classes.add(component_type)

    return sorted(equipment_classes, key=str)


def superclass_closure(graph, class_uri):
    """Return class_uri plus all its rdfs:subClassOf superclasses known in the graph."""
    closure = {class_uri}
    for superclass in graph.transitive_objects(class_uri, RDFS.subClassOf):
        closure.add(superclass)
    return closure


def is_failure_mode_allowed(combined_graph, allowed_pairs, equipment_class, failure_mode):
    """
    A failure mode is allowed if the equipment class itself, or one of its
    rdfs:subClassOf* superclasses, has i14224:hasAllowedFailureMode failure_mode.
    """
    for candidate_class in superclass_closure(combined_graph, equipment_class):
        if (candidate_class, failure_mode) in allowed_pairs:
            return True
    return False


def classify_entries(data_graph, allowed_graph, use_component_type_fallback=False):
    combined_graph = data_graph + allowed_graph
    allowed_pairs = set(allowed_graph.subject_objects(I14224.hasAllowedFailureMode))

    entries = get_fmea_entries(data_graph)
    if not entries:
        raise RuntimeError(
            "No FMEA entries found. Expected rows typed as fmea:FMEAEntry "
            "or rows with fmea:hasSourceRowNumber."
        )

    summary = {category: [] for category in REPORT_ROWS}
    detail_rows = []

    for entry in sorted(entries, key=lambda e: get_row_number(data_graph, e)):
        row_number = get_row_number(data_graph, entry)
        summary["6. Total worksheet rows checked"].append(row_number)

        fm_code_literal = get_literal_value(data_graph, entry, FMEA.hasFailureModeCodeLiteral)
        failure_modes = get_failure_modes(data_graph, entry)
        equipment_classes = get_equipment_classes(
            data_graph,
            entry,
            use_component_type_fallback=use_component_type_fallback,
        )

        category = None
        allowed_match = False

        if has_blank_fm_code(data_graph, entry):
            category = "1. FM code blank"

        elif not failure_modes:
            category = "2. FM code not in ISO 14224 Annex B"

        elif not equipment_classes:
            category = "4. FM valid but class-specific check could not run (equipment class blank/unresolved)"

        else:
            for equipment_class in equipment_classes:
                for failure_mode in failure_modes:
                    if is_failure_mode_allowed(
                        combined_graph=combined_graph,
                        allowed_pairs=allowed_pairs,
                        equipment_class=equipment_class,
                        failure_mode=failure_mode,
                    ):
                        allowed_match = True
                        break
                if allowed_match:
                    break

            if allowed_match:
                category = "5. Compliant (FM defined and allowed for equipment class)"
            else:
                category = "3. FM valid but not allowed for equipment class"

        summary[category].append(row_number)

        detail_rows.append(
            {
                "Worksheet Row Number": row_number,
                "Category": category,
                "FM Code Literal": fm_code_literal,
                "Mapped Failure Mode": "; ".join(local_name(fm) for fm in failure_modes),
                "Equipment Class Used": "; ".join(local_name(ec) for ec in equipment_classes),
                "FMEA Entry URI": str(entry),
            }
        )

    return summary, detail_rows


def write_summary_csv(output_path, summary):
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Total Rows", "Worksheet Row Numbers"])
        for category in REPORT_ROWS:
            rows = summary.get(category, [])
            writer.writerow([category, len(set(rows)), format_row_numbers(rows)])


def write_details_csv(output_path, detail_rows):
    fieldnames = [
        "Worksheet Row Number",
        "Category",
        "FM Code Literal",
        "Mapped Failure Mode",
        "Equipment Class Used",
        "FMEA Entry URI",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detail_rows)


def main():
    args = parse_args()

    data_path = require_file(args.data)
    allowed_path = require_file(args.allowed)
    output_path = Path(args.out)
    details_path = Path(args.details_out)

    data_graph = Graph()
    data_graph.parse(data_path, format="turtle")

    allowed_graph = Graph()
    allowed_graph.parse(allowed_path, format="turtle")

    summary, detail_rows = classify_entries(
        data_graph,
        allowed_graph,
        use_component_type_fallback=args.use_component_type_fallback,
    )

    write_summary_csv(output_path, summary)
    write_details_csv(details_path, detail_rows)

    print(f"Wrote summary CSV: {output_path}")
    print(f"Wrote row details CSV: {details_path}")
    print()
    print("Summary:")
    for category in REPORT_ROWS:
        rows = summary[category]
        print(f"{category}: {len(set(rows))}")
        if rows:
            print(f"  Rows: {format_row_numbers(rows)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
