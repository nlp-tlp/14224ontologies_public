"""
Generate LIS14/assetCore/mwoCore-aligned RDF instance data from
AutoclaveWorkOrderData.csv.

Usage:
    pip install pandas rdflib
    python csv_to_lis14_instances.py
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD

CSV_PATH = Path("AutoclaveWorkOrderData.csv")
OUT_PATH = Path("autoclave-workorder-instances.ttl")

# Ontology namespaces
LIS = Namespace("http://rds.posccaesar.org/ontology/lis14/rdl/")
ASSET = Namespace("https://nlp-tlp.org/ontology/asset/rdl/")
MWO = Namespace("https://nlp-tlp.org/ontology/mwo/rdl/")

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


def add_if_text(g: Graph, s: URIRef, p: URIRef, value: object) -> None:
    if not pd.isna(value) and str(value).strip():
        g.add((s, p, Literal(str(value).strip())))


def main() -> None:
    df = pd.read_csv(CSV_PATH)

    g = Graph()
    g.bind("lis", LIS)
    g.bind("asset", ASSET)
    g.bind("mwo", MWO)
    g.bind("inst", INST)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("dcterms", DCTERMS)

    ontology_iri = URIRef("https://example.org/autoclave/work-order/instances")
    g.add((ontology_iri, RDF.type, OWL.Ontology))
    g.add((ontology_iri, OWL.imports, URIRef("http://rds.posccaesar.org/ontology/lis14/ont/core")))
    g.add((ontology_iri, OWL.imports, URIRef("https://nlp-tlp.org/ontology/asset/ont/rdl/")))
    g.add((ontology_iri, OWL.imports, URIRef("https://nlp-tlp.org/ontology/mwo/ont/rdl/")))

    for i, row in df.iterrows():
        wo_id = local_id(row["MaintenanceWorkOrderActivity"], f"WO_{i+1}")
        wo = INST[wo_id]

        # Main row anchor: one work order activity per CSV row.
        g.add((wo, RDF.type, MWO.MWOActivity))
        g.add((wo, RDFS.label, Literal(str(row["MaintenanceWorkOrderActivity"]).strip())))
        add_if_text(g, wo, DCTERMS.description, row.get("WODescription"))

        # Date as a LIS temporal region plus a temporal datum.
        if not pd.isna(row.get("Date")) and str(row["Date"]).strip():
            date_text = str(row["Date"]).strip()
            instant = INST[f"Instant_{wo_id}"]
            date_datum = INST[f"DateDatum_{wo_id}"]
            g.add((instant, RDF.type, LIS.InstantRegion))
            g.add((instant, RDFS.label, Literal(f"date of {row['MaintenanceWorkOrderActivity']}")))
            g.add((wo, LIS.hasTemporalRegion, instant))
            g.add((date_datum, RDF.type, LIS.TemporalDatum))
            g.add((date_datum, RDFS.label, Literal(f"date datum for {row['MaintenanceWorkOrderActivity']}")))
            g.add((date_datum, LIS.temporalValue, Literal(date_text, datatype=XSD.date)))
            g.add((date_datum, LIS.quantifiesTemporalRegion, instant))
            g.add((wo, LIS.representedIn, date_datum))

        # Asset from FunctionalLocation; reuse same asset node across rows.
        floc_raw = row.get("FunctionalLocation")
        floc = "" if pd.isna(floc_raw) else str(floc_raw).strip()
        asset_id = local_id(floc, f"Asset_{i+1}")
        asset = INST[f"Asset_{asset_id}"]
        g.add((asset, RDF.type, ASSET.MaintainableAsset))
        label = str(row.get("AssetDescription", "")).strip() if not pd.isna(row.get("AssetDescription")) else floc
        if label:
            g.add((asset, RDFS.label, Literal(label)))
        add_if_text(g, asset, ASSET.functionalLocation, floc)
        add_if_text(g, asset, ASSET.controlLoopID, row.get("ControlLoopID"))
        g.add((wo, LIS.hasParticipant, asset))

        # AssetDescription is treated as descriptive text for the asset,
        # not as a separate AssetDescription individual.
        # This prevents duplicate labelled individuals such as:
        #   inst:Asset_SCE_02777 and inst:AssetDescription_SCE_02777
        # both having the same rdfs:label.
        add_if_text(g, asset, DCTERMS.description, row.get("AssetDescription"))

        # Work order type as reusable named individual/code object.
        if not pd.isna(row.get("WOOrderType")) and str(row["WOOrderType"]).strip():
            code = str(row["WOOrderType"]).strip()
            wo_type = INST[f"WOOrderType_{local_id(code)}"]
            g.add((wo_type, RDF.type, MWO.MWOActivityType))
            g.add((wo_type, RDFS.label, Literal(code)))
            g.add((wo, MWO.hasWorkOrderType, wo_type))

        # ISO 14224 failure mode code as reusable named individual/code object.
        if not pd.isna(row.get("ISO14224FailureModeCode")) and str(row["ISO14224FailureModeCode"]).strip():
            code = str(row["ISO14224FailureModeCode"]).strip()
            failure_code = INST[f"FailureModeCode_{local_id(code)}"]
            g.add((failure_code, RDF.type, MWO.MWOFailureModeCode))
            g.add((failure_code, RDFS.label, Literal(code)))
            g.add((wo, MWO.hasFailureModeCode, failure_code))

        # Actual cost as a datum node.
        if not pd.isna(row.get("ActualCost")):
            cost = INST[f"ActualCostDatum_{wo_id}"]
            g.add((cost, RDF.type, MWO.ActualCostDatum))
            g.add((cost, RDFS.label, Literal(f"actual cost for {row['MaintenanceWorkOrderActivity']}")))
            g.add((cost, LIS.datumValue, Literal(row["ActualCost"], datatype=XSD.decimal)))
            g.add((wo, MWO.hasActualCost, cost))

        # Work hours as a datum node.
        if not pd.isna(row.get("WorkHours")):
            hours = INST[f"WorkHoursDatum_{wo_id}"]
            g.add((hours, RDF.type, MWO.WorkHoursDatum))
            g.add((hours, RDFS.label, Literal(f"work hours for {row['MaintenanceWorkOrderActivity']}")))
            g.add((hours, LIS.datumValue, Literal(row["WorkHours"], datatype=XSD.decimal)))
            g.add((wo, MWO.hasWorkHours, hours))

    g.serialize(destination=OUT_PATH, format="turtle")
    print(f"Wrote {OUT_PATH} with {len(g)} triples")


if __name__ == "__main__":
    main()
