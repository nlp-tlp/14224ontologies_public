#!/usr/bin/env python3
"""
Convert AutoclaveControlLoopFMEA.csv rows to RDF/Turtle named individuals.

Dependencies:
    pip install pandas rdflib

Default folder layout:
    14224ontologies_public/
      inDevelopment/
        i14224_appendixA.ttl
        i14224_appendixB.ttl
        i14224_clause3.ttl
      experiments/experiment2/
        fmea_csv_to_ttl.py
        AutoclaveControlLoopFMEA.csv

Example from experiments/experiment2:
    python .\fmea_csv_to_ttl.py

Optional override example:
    python .\fmea_csv_to_ttl.py --csv .\SomeOtherFMEA.csv
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import pandas as pd
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import OWL, XSD, DCTERMS, SKOS

I14224 = Namespace("https://iso14224.org/ontology/i14224/rdl/")
FMEA = Namespace("https://example.org/ontology/fmea/ont/")
INST_DEFAULT = "https://example.org/data/autoclave-fmea/"


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def slug(value: str, fallback: str = "unnamed") -> str:
    value = clean_text(value)
    value = value.replace("&", " and ")
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return value or fallback


def local_name(uri: URIRef) -> str:
    s = str(uri)
    return re.split(r"[#/]", s.rstrip("/#"))[-1]


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_text(value).lower())


def load_reference_graph(paths: Iterable[Path]) -> Graph:
    g = Graph()
    for path in paths:
        g.parse(path, format="turtle")
    return g


def build_equipment_code_lookup(ref: Graph) -> Dict[str, URIRef]:
    """Return mapping from ISO 14224 equipment code literal, e.g. 'CL', to equipment class/type IRI."""
    lookup: Dict[str, URIRef] = {}
    for eq_class, _, code_ind in ref.triples((None, I14224.hasEquipmentCode, None)):
        code = None
        for label in ref.objects(code_ind, RDFS.label):
            code = clean_text(label)
            break
        if not code:
            # Fallback for code individuals whose local name is the code.
            code = local_name(code_ind)
        if code:
            lookup[code.upper()] = eq_class
    return lookup


def build_failure_mode_code_lookup(ref: Graph) -> Dict[str, URIRef]:
    """Return mapping from failure mode code, e.g. 'FTF', to ISO 14224 failure mode individual."""
    lookup: Dict[str, URIRef] = {}
    for subject in ref.subjects(RDF.type, I14224.FailureMode):
        for label in ref.objects(subject, RDFS.label):
            code = clean_text(label).upper()
            if re.fullmatch(r"[A-Z0-9]{2,5}", code):
                lookup[code] = subject
    return lookup


def build_failure_mechanism_class_lookup(ref: Graph) -> Dict[str, URIRef]:
    """Return normalized label -> ISO 14224 FailureMechanism subclass.

    The CSV contains text such as 'Out of adjustment', while Appendix B class labels often read
    'Out of adjustment failure mechanism'. The function indexes both forms.
    """
    lookup: Dict[str, URIRef] = {}
    for cls in ref.subjects(RDFS.subClassOf, I14224.FailureMechanism):
        for label in ref.objects(cls, RDFS.label):
            text = clean_text(label)
            lookup[norm(text)] = cls
            text_without_suffix = re.sub(r"\s+failure mechanism$", "", text, flags=re.I)
            lookup[norm(text_without_suffix)] = cls
    return lookup


def add_literal(g: Graph, s: URIRef, p: URIRef, value, datatype=None) -> None:
    text = clean_text(value)
    if text:
        g.add((s, p, Literal(text, datatype=datatype)))


def make_schema(g: Graph) -> None:
    """Add a small local vocabulary for FMEA-specific roles/properties not present in ISO 14224."""
    for cls, label in [
        (FMEA.FMEAEntry, "FMEA entry"),
        (FMEA.FunctionalLocation, "functional location"),
        (FMEA.MaintenanceStrategy, "maintenance strategy"),
        (FMEA.ControlMeasure, "control measure"),
        (FMEA.ControlGroup, "control group"),
    ]:
        g.add((cls, RDF.type, OWL.Class))
        g.add((cls, RDFS.label, Literal(label, lang="en")))

    for prop, label in [
        (FMEA.hasAsset, "has asset"),
        (FMEA.hasComponent, "has component"),
        (FMEA.isComponentOf, "is component of"),
        (FMEA.hasFunctionalLocation, "has functional location"),
        (FMEA.hasFunctionalPurpose, "has functional purpose"),
        (FMEA.hasFailureModeCodeLiteral, "has failure mode code literal"),
        (FMEA.hasFailureModeOriginalText, "has failure mode original text"),
        (FMEA.hasFailureModeDescriptionText, "has failure mode description text"),
        (FMEA.hasFailureMechanism, "has failure mechanism"),
        (FMEA.hasFailureMechanismCategoryText, "has failure mechanism category text"),
        (FMEA.hasFailureMechanismSubdivisionText, "has failure mechanism subdivision text"),
        (FMEA.hasOriginalFailureMechanismText, "has original failure mechanism text"),
        (FMEA.hasFailureEffectText, "has failure effect text"),
        (FMEA.hasConsequenceNote, "has consequence note"),
        (FMEA.hasMaintenanceStrategy, "has maintenance strategy"),
        (FMEA.hasControlMeasure, "has control measure"),
        (FMEA.hasControlFrequency, "has control frequency"),
        (FMEA.hasControlGroup, "has control group"),
        (FMEA.hasHiddenFailure, "has hidden failure"),
        (FMEA.hasSourceRowNumber, "has source row number"),
        (FMEA.hasSourceColumnValue, "has source column value"),
    ]:
        g.add((prop, RDF.type, OWL.ObjectProperty if prop in {
            FMEA.hasAsset, FMEA.hasComponent, FMEA.isComponentOf, FMEA.hasFunctionalLocation,
            FMEA.hasFailureMechanism, FMEA.hasMaintenanceStrategy, FMEA.hasControlMeasure,
            FMEA.hasControlGroup,
        } else OWL.DatatypeProperty))
        g.add((prop, RDFS.label, Literal(label, lang="en")))

    # The ISO 14224 source files define equipment classes and equipment codes,
    # but some local datasets need an explicit row-level link from the FMEA row
    # to the resolved equipment class. We declare the property here so the
    # generated TTL is self-documenting.
    g.add((I14224.hasEquipmentClass, RDF.type, OWL.ObjectProperty))
    g.add((I14224.hasEquipmentClass, RDFS.label, Literal("has equipment class", lang="en")))


def convert(csv_path: Path, iso_paths: Iterable[Path], out_path: Path, warnings_path: Path, base: str) -> None:
    ref = load_reference_graph(iso_paths)
    equipment_by_code = build_equipment_code_lookup(ref)
    failure_mode_by_code = build_failure_mode_code_lookup(ref)
    mechanism_by_label = build_failure_mechanism_class_lookup(ref)

    df = pd.read_csv(csv_path, dtype=str).fillna("")
    g = Graph()
    INST = Namespace(base)

    g.bind("inst", INST)
    g.bind("fmea", FMEA)
    g.bind("i14224", I14224)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("dcterms", DCTERMS)
    g.bind("skos", SKOS)

    ontology_iri = URIRef(base.rstrip("/#") + "/ontology")
    g.add((ontology_iri, RDF.type, OWL.Ontology))
    g.add((ontology_iri, OWL.imports, URIRef("https://iso14224.org/ontology/i14224/ont/appendixA")))
    g.add((ontology_iri, OWL.imports, URIRef("https://iso14224.org/ontology/i14224/ont/appendixB")))
    g.add((ontology_iri, OWL.imports, URIRef("https://iso14224.org/ontology/i14224/ont/clause3")))
    g.add((ontology_iri, DCTERMS.source, Literal(csv_path.name)))

    make_schema(g)

    warnings = []
    seen_assets = set()
    seen_components = set()
    seen_functional_locations = set()
    seen_maintenance_strategies = set()
    seen_control_measures = set()
    seen_control_groups = set()
    seen_mechanisms = set()

    for idx, row in df.iterrows():
        source_row = idx + 2  # CSV row 1 is the header row in spreadsheet terms.
        entry = INST[f"FMEAEntry_row_{source_row:04d}"]
        g.add((entry, RDF.type, FMEA.FMEAEntry))
        g.add((entry, RDFS.label, Literal(f"FMEA row {source_row}", lang="en")))
        g.add((entry, FMEA.hasSourceRowNumber, Literal(source_row, datatype=XSD.integer)))

        # Asset
        asset_id = clean_text(row.get("AssetID", ""))
        if asset_id:
            asset = INST[f"Asset_{slug(asset_id)}"]
            g.add((entry, FMEA.hasAsset, asset))
            if asset not in seen_assets:
                seen_assets.add(asset)
                g.add((asset, RDF.type, I14224.EquipmentUnit))
                g.add((asset, RDFS.label, Literal(asset_id)))
                add_literal(g, asset, FMEA.hasSourceColumnValue, row.get("AssetType", ""))

        # Functional location / tag number
        floc_text = clean_text(row.get("FunctionalLocation", ""))
        if floc_text:
            floc = INST[f"FunctionalLocation_{slug(floc_text)}"]
            g.add((entry, FMEA.hasFunctionalLocation, floc))
            if floc not in seen_functional_locations:
                seen_functional_locations.add(floc)
                g.add((floc, RDF.type, FMEA.FunctionalLocation))
                g.add((floc, RDF.type, I14224.TagNumber))
                g.add((floc, RDFS.label, Literal(floc_text)))

        add_literal(g, entry, FMEA.hasFunctionalPurpose, row.get("Functional Purpose", ""))

        # Component / maintainable item
        component_id = clean_text(row.get("Component_ID", ""))
        if component_id:
            component = INST[f"Component_{slug(component_id)}"]
            g.add((entry, FMEA.hasComponent, component))
            if asset_id:
                g.add((component, FMEA.isComponentOf, INST[f"Asset_{slug(asset_id)}"]))
            if component not in seen_components:
                seen_components.add(component)
                g.add((component, RDF.type, I14224.MaintainableItem))
                g.add((component, RDFS.label, Literal(component_id)))
                add_literal(g, component, RDFS.comment, row.get("Component information", ""))

            eq_code = clean_text(row.get("ISO14224 Equipment Class", "")).upper()
            if eq_code:
                eq_class = equipment_by_code.get(eq_code)
                if eq_class:
                    # Type the component/maintainable item as the resolved ISO 14224 equipment class.
                    g.add((component, RDF.type, eq_class))

                    # Add explicit row-level links, e.g.
                    # inst:FMEAEntry_row_0004
                    #     i14224:hasEquipmentClass i14224:InputDevice ;
                    #     i14224:hasEquipmentCode i14224:IP .
                    g.add((entry, I14224.hasEquipmentClass, eq_class))
                    g.add((entry, I14224.hasEquipmentCode, URIRef(str(I14224) + eq_code)))
                else:
                    warnings.append((source_row, "ISO14224 Equipment Class", eq_code, "No matching ISO 14224 equipment class/type code found in Appendix A"))
            else:
                warnings.append((source_row, "ISO14224 Equipment Class", "", "Blank equipment class code"))

        # Failure mode
        fm_code = clean_text(row.get("ISO14224 Failure Mode Code", "")).upper()
        if fm_code:
            add_literal(g, entry, FMEA.hasFailureModeCodeLiteral, fm_code)
            fm = failure_mode_by_code.get(fm_code)
            if fm:
                g.add((entry, I14224.hasFailureMode, fm))
            else:
                warnings.append((source_row, "ISO14224 Failure Mode Code", fm_code, "No matching ISO 14224 failure mode code found in Appendix B"))
        else:
            warnings.append((source_row, "ISO14224 Failure Mode Code", "", "Blank failure mode code"))

        add_literal(g, entry, FMEA.hasFailureModeDescriptionText, row.get("ISO14224 Failure Mode Description", ""))
        add_literal(g, entry, FMEA.hasFailureModeOriginalText, row.get("Original data entry for Failure Mode ", ""))

        # Failure mechanism: map subdivision/category text to ISO class when possible, and always preserve source text.
        mech_sub = clean_text(row.get("ISO14224 Failure Mechanism Subdivision", ""))
        mech_cat = clean_text(row.get("ISO14224 Failure Mechanism Category", ""))
        mech_original = clean_text(row.get("Original entry for Failure Mechanism ", ""))
        add_literal(g, entry, FMEA.hasFailureMechanismCategoryText, mech_cat)
        add_literal(g, entry, FMEA.hasFailureMechanismSubdivisionText, mech_sub)
        add_literal(g, entry, FMEA.hasOriginalFailureMechanismText, mech_original)

        mech_class = mechanism_by_label.get(norm(mech_sub)) or mechanism_by_label.get(norm(mech_cat))
        if mech_sub or mech_cat or mech_original:
            mech_key = slug(mech_sub or mech_cat or mech_original)
            mechanism = INST[f"FailureMechanism_{mech_key}"]
            g.add((entry, FMEA.hasFailureMechanism, mechanism))
            if mechanism not in seen_mechanisms:
                seen_mechanisms.add(mechanism)
                g.add((mechanism, RDF.type, mech_class if mech_class else I14224.FailureMechanism))
                g.add((mechanism, RDFS.label, Literal(mech_sub or mech_cat or mech_original)))

        # Effects, maintenance and controls
        add_literal(g, entry, FMEA.hasFailureEffectText, row.get("Original entry for Failure Effect", ""))
        add_literal(g, entry, FMEA.hasConsequenceNote, row.get("Unnamed: 20", ""))

        hidden = clean_text(row.get("HiddenFailure", "")).upper()
        if hidden in {"Y", "YES", "TRUE", "1"}:
            g.add((entry, FMEA.hasHiddenFailure, Literal(True, datatype=XSD.boolean)))
        elif hidden in {"N", "NO", "FALSE", "0"}:
            g.add((entry, FMEA.hasHiddenFailure, Literal(False, datatype=XSD.boolean)))

        ms_text = clean_text(row.get("MaintenanceStrategy", ""))
        if ms_text:
            ms = INST[f"MaintenanceStrategy_{slug(ms_text)}"]
            g.add((entry, FMEA.hasMaintenanceStrategy, ms))
            if ms not in seen_maintenance_strategies:
                seen_maintenance_strategies.add(ms)
                g.add((ms, RDF.type, FMEA.MaintenanceStrategy))
                g.add((ms, RDFS.label, Literal(ms_text)))

        cm_text = clean_text(row.get("ControlMeasure", ""))
        if cm_text:
            cm = INST[f"ControlMeasure_{slug(cm_text)}"]
            g.add((entry, FMEA.hasControlMeasure, cm))
            if cm not in seen_control_measures:
                seen_control_measures.add(cm)
                g.add((cm, RDF.type, FMEA.ControlMeasure))
                g.add((cm, RDFS.label, Literal(cm_text)))
        add_literal(g, entry, FMEA.hasControlFrequency, row.get("ControlFrequency", ""))

        cg_text = clean_text(row.get("ControlGroup ", ""))
        if cg_text:
            cg = INST[f"ControlGroup_{slug(cg_text)}"]
            g.add((entry, FMEA.hasControlGroup, cg))
            if cg not in seen_control_groups:
                seen_control_groups.add(cg)
                g.add((cg, RDF.type, FMEA.ControlGroup))
                g.add((cg, RDFS.label, Literal(cg_text)))

    out_path.write_text(g.serialize(format="turtle"), encoding="utf-8")

    with warnings_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_row", "column", "value", "warning"])
        writer.writerows(warnings)

    print(f"Wrote {out_path}")
    print(f"Wrote {warnings_path}")
    print(f"Rows converted: {len(df)}")
    print(f"Triples written: {len(g)}")
    print(f"Warnings: {len(warnings)}")


def main() -> None:
    script_dir = Path(__file__).resolve().parent

    # Expected project layout:
    # 14224ontologies_public/
    #   inDevelopment/
    #   experiments/experiment2/fmea_csv_to_ttl.py
    project_root = script_dir.parent.parent
    ontology_dir = project_root / "inDevelopment"

    default_csv = script_dir / "AutoclaveControlLoopFMEA.csv"
    default_iso_a = ontology_dir / "i14224_appendixA.ttl"
    default_iso_b = ontology_dir / "i14224_appendixB.ttl"
    default_iso_c = ontology_dir / "i14224_clause3.ttl"
    default_out = script_dir / "AutoclaveControlLoopFMEA_instances.ttl"
    default_warnings = script_dir / "AutoclaveControlLoopFMEA_warnings.csv"

    parser = argparse.ArgumentParser(
        description="Convert the Autoclave Control Loop FMEA CSV to RDF/Turtle."
    )
    parser.add_argument("--csv", default=default_csv, type=Path)
    parser.add_argument("--iso-a", default=default_iso_a, type=Path)
    parser.add_argument("--iso-b", default=default_iso_b, type=Path)
    parser.add_argument("--iso-c", default=default_iso_c, type=Path)
    parser.add_argument("--out", default=default_out, type=Path)
    parser.add_argument("--warnings", default=default_warnings, type=Path)
    parser.add_argument("--base", default=INST_DEFAULT)
    args = parser.parse_args()

    required_files = [args.csv, args.iso_a, args.iso_b, args.iso_c]
    missing_files = [path for path in required_files if not path.exists()]
    if missing_files:
        print("ERROR: The following required files were not found:")
        for path in missing_files:
            print(f"  - {path}")
        print("\nCheck that you are using this folder layout:")
        print(r"  C:\Users\00040628\LocalData\GitHub\14224ontologies_public\inDevelopment")
        print(r"  C:\Users\00040628\LocalData\GitHub\14224ontologies_public\experiments\experiment2")
        raise SystemExit(1)

    convert(
        csv_path=args.csv,
        iso_paths=[args.iso_a, args.iso_b, args.iso_c],
        out_path=args.out,
        warnings_path=args.warnings,
        base=args.base,
    )


if __name__ == "__main__":
    main()
