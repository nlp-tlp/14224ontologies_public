"""
Generate LIS14/assetCore/mwoCore-aligned RDF instance data from
AutoclaveWorkOrderData.csv.

In plain English:
    This script reads a CSV file of maintenance work order data and turns each
    row into RDF triples. The RDF is saved as a Turtle (.ttl) file.

Usage:
    pip install pandas rdflib
    python csv_to_lis14_instances.py
"""

# This import allows newer Python type-hint behaviour to work consistently.
# It is not essential to understanding the script logic.
from __future__ import annotations

# re is Python's regular-expression library. Here it is used to clean text so
# it can safely be used in an IRI/local identifier.
import re

# Path gives a clean, cross-platform way to refer to file paths.
from pathlib import Path

# quote converts unsafe URL/IRI characters into escaped characters.
# This helps prevent invalid IRIs.
from urllib.parse import quote

# pandas is used to read and work with the CSV file as a table.
import pandas as pd

# rdflib is the main RDF library used here.
# Graph stores triples.
# Literal stores literal values such as strings, dates, and decimals.
# Namespace helps build IRIs from namespace bases.
# URIRef represents an IRI resource.
from rdflib import Graph, Literal, Namespace, URIRef

# These are common RDF/OWL namespaces supplied by rdflib.
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD


# -----------------------------------------------------------------------------
# Input and output files
# -----------------------------------------------------------------------------

# The CSV file to read. It must be in the same folder where the script is run,
# unless you change this path.
CSV_PATH = Path("AutoclaveWorkOrderData.csv")

# The Turtle file that will be created by the script.
OUT_PATH = Path("autoclave-workorder-instances.ttl")


# -----------------------------------------------------------------------------
# Ontology namespaces
# -----------------------------------------------------------------------------

# These namespace objects let the code create full IRIs using short names.
# For example, MWO.MWOActivity becomes:
# https://nlp-tlp.org/ontology/mwo/rdl/MWOActivity
LIS = Namespace("http://rds.posccaesar.org/ontology/lis14/rdl/")
ASSET = Namespace("https://nlp-tlp.org/ontology/asset/rdl/")
MWO = Namespace("https://nlp-tlp.org/ontology/mwo/rdl/")

# This is the namespace for the new individuals created from your CSV data.
# In production, replace example.org with a real persistent namespace that you own
# or control.
INST = Namespace("https://example.org/autoclave/work-order/instance/")


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def local_id(value: object, fallback: str = "unnamed") -> str:
    """
    Convert a CSV value into a safe local identifier for an IRI.

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


def add_if_text(g: Graph, s: URIRef, p: URIRef, value: object) -> None:
    """
    Add a triple only if the supplied CSV value contains text.

    This prevents empty CSV cells from becoming empty RDF literals.

    Parameters:
        g:
            The RDF graph to add the triple to.
        s:
            The subject IRI of the triple.
        p:
            The predicate/property IRI of the triple.
        value:
            The CSV value to turn into a literal object.
    """

    # Only add the triple if the value is not missing and is not blank text.
    if not pd.isna(value) and str(value).strip():
        # Add the RDF triple: subject, predicate, object.
        # The object is a Literal because it is text data, not another IRI.
        g.add((s, p, Literal(str(value).strip())))


# -----------------------------------------------------------------------------
# Main script logic
# -----------------------------------------------------------------------------

def main() -> None:
    """
    Read the CSV, build an RDF graph, and write the graph to a Turtle file.
    """

    # Read the CSV into a pandas DataFrame.
    # Think of df as a table where each row is a work order record.
    df = pd.read_csv(CSV_PATH)

    # Create an empty RDF graph. Triples will be added to this graph.
    g = Graph()

    # Bind prefixes so the output Turtle file is readable.
    # Without these, the output would contain many long full IRIs.
    g.bind("lis", LIS)
    g.bind("asset", ASSET)
    g.bind("mwo", MWO)
    g.bind("inst", INST)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("dcterms", DCTERMS)

    # Create an IRI for the generated ontology/file itself.
    ontology_iri = URIRef("https://example.org/autoclave/work-order/instances")

    # Say that this generated file is an OWL ontology.
    g.add((ontology_iri, RDF.type, OWL.Ontology))

    # Add owl:imports statements so tools know this generated data depends on
    # LIS14, assetCore, and mwoCore.
    g.add((ontology_iri, OWL.imports, URIRef("http://rds.posccaesar.org/ontology/lis14/ont/core")))
    g.add((ontology_iri, OWL.imports, URIRef("https://nlp-tlp.org/ontology/asset/ont/rdl/")))
    g.add((ontology_iri, OWL.imports, URIRef("https://nlp-tlp.org/ontology/mwo/ont/rdl/")))

    # Loop through every row in the CSV table.
    # i is the row number; row contains the values for that CSV row.
    for i, row in df.iterrows():

        # Create a safe identifier for the work order activity using the
        # MaintenanceWorkOrderActivity column. If that value is missing,
        # use WO_1, WO_2, etc. as a fallback.
        wo_id = local_id(row["MaintenanceWorkOrderActivity"], f"WO_{i+1}")

        # Create the full IRI for the work order individual.
        wo = INST[wo_id]

        # ---------------------------------------------------------------------
        # Work order activity individual
        # ---------------------------------------------------------------------

        # Main row anchor: one work order activity per CSV row.
        # This says: the work order individual is an instance of mwo:MWOActivity.
        g.add((wo, RDF.type, MWO.MWOActivity))

        # Add a human-readable label for the work order.
        g.add((wo, RDFS.label, Literal(str(row["MaintenanceWorkOrderActivity"]).strip())))

        # Add the work order description if the WODescription cell has text.
        add_if_text(g, wo, DCTERMS.description, row.get("WODescription"))

        # ---------------------------------------------------------------------
        # Date information
        # ---------------------------------------------------------------------

        # If the Date cell is present and not blank, create RDF date information.
        if not pd.isna(row.get("Date")) and str(row["Date"]).strip():
            date_text = str(row["Date"]).strip()

            # Create two related individuals:
            # 1. an instant/temporal region representing the time itself;
            # 2. a date datum representing the recorded date value.
            instant = INST[f"Instant_{wo_id}"]
            date_datum = INST[f"DateDatum_{wo_id}"]

            # Type and label the temporal region.
            g.add((instant, RDF.type, LIS.InstantRegion))
            g.add((instant, RDFS.label, Literal(f"date of {row['MaintenanceWorkOrderActivity']}")))

            # Link the work order activity to its temporal region.
            g.add((wo, LIS.hasTemporalRegion, instant))

            # Type and label the date datum.
            g.add((date_datum, RDF.type, LIS.TemporalDatum))
            g.add((date_datum, RDFS.label, Literal(f"date datum for {row['MaintenanceWorkOrderActivity']}")))

            # Store the actual date value as an xsd:date literal.
            # This assumes the CSV date value is already in a valid date format,
            # preferably YYYY-MM-DD.
            g.add((date_datum, LIS.temporalValue, Literal(date_text, datatype=XSD.date)))

            # Say that the date datum quantifies/describes the temporal region.
            g.add((date_datum, LIS.quantifiesTemporalRegion, instant))

            # Link the work order to the date datum representation.
            g.add((wo, LIS.representedIn, date_datum))

        # ---------------------------------------------------------------------
        # Asset information
        # ---------------------------------------------------------------------

        # Get the FunctionalLocation value from the row.
        floc_raw = row.get("FunctionalLocation")

        # Convert missing values to an empty string; otherwise clean spaces.
        floc = "" if pd.isna(floc_raw) else str(floc_raw).strip()

        # Create a stable asset ID from FunctionalLocation.
        # Because this uses FunctionalLocation, the same asset IRI can be reused
        # across multiple work order rows.
        asset_id = local_id(floc, f"Asset_{i+1}")
        asset = INST[f"Asset_{asset_id}"]

        # Type the asset as an asset:MaintainableAsset.
        g.add((asset, RDF.type, ASSET.MaintainableAsset))

        # Prefer AssetDescription as the human-readable asset label.
        # If AssetDescription is missing, use the FunctionalLocation instead.
        label = str(row.get("AssetDescription", "")).strip() if not pd.isna(row.get("AssetDescription")) else floc

        # Add the asset label only if there is something to add.
        if label:
            g.add((asset, RDFS.label, Literal(label)))

        # Add FunctionalLocation and ControlLoopID as text properties on the asset.
        add_if_text(g, asset, ASSET.functionalLocation, floc)
        add_if_text(g, asset, ASSET.controlLoopID, row.get("ControlLoopID"))

        # Link the work order activity to the asset involved in the work order.
        g.add((wo, LIS.hasParticipant, asset))

        # AssetDescription is treated as descriptive text for the asset,
        # not as a separate AssetDescription individual.
        # This prevents duplicate labelled individuals such as:
        #   inst:Asset_SCE_02777 and inst:AssetDescription_SCE_02777
        # both having the same rdfs:label.
        add_if_text(g, asset, DCTERMS.description, row.get("AssetDescription"))

        # ---------------------------------------------------------------------
        # Work order type code
        # ---------------------------------------------------------------------

        # If there is a work order type code, create/reuse a code individual.
        if not pd.isna(row.get("WOOrderType")) and str(row["WOOrderType"]).strip():
            code = str(row["WOOrderType"]).strip()

            # Create an IRI such as inst:WOOrderType_PM01.
            wo_type = INST[f"WOOrderType_{local_id(code)}"]

            # Type the code individual and give it a label.
            g.add((wo_type, RDF.type, MWO.MWOActivityType))
            g.add((wo_type, RDFS.label, Literal(code)))

            # Link the work order activity to this work order type.
            g.add((wo, MWO.hasWorkOrderType, wo_type))

        # ---------------------------------------------------------------------
        # ISO 14224 failure mode code
        # ---------------------------------------------------------------------

        # If there is a failure mode code, create/reuse a code individual.
        if not pd.isna(row.get("ISO14224FailureModeCode")) and str(row["ISO14224FailureModeCode"]).strip():
            code = str(row["ISO14224FailureModeCode"]).strip()

            # Create an IRI such as inst:FailureModeCode_AIR.
            failure_code = INST[f"FailureModeCode_{local_id(code)}"]

            # Type the code individual and give it a label.
            g.add((failure_code, RDF.type, MWO.MWOFailureModeCode))
            g.add((failure_code, RDFS.label, Literal(code)))

            # Link the work order activity to this failure mode code.
            g.add((wo, MWO.hasFailureModeCode, failure_code))

        # ---------------------------------------------------------------------
        # Actual cost datum
        # ---------------------------------------------------------------------

        # If ActualCost is present, create a datum individual for the cost.
        if not pd.isna(row.get("ActualCost")):
            cost = INST[f"ActualCostDatum_{wo_id}"]

            # Type and label the cost datum.
            g.add((cost, RDF.type, MWO.ActualCostDatum))
            g.add((cost, RDFS.label, Literal(f"actual cost for {row['MaintenanceWorkOrderActivity']}")))

            # Store the numeric cost value as an xsd:decimal literal.
            g.add((cost, LIS.datumValue, Literal(row["ActualCost"], datatype=XSD.decimal)))

            # Link the work order to its cost datum.
            g.add((wo, MWO.hasActualCost, cost))

        # ---------------------------------------------------------------------
        # Work hours datum
        # ---------------------------------------------------------------------

        # If WorkHours is present, create a datum individual for the hours.
        if not pd.isna(row.get("WorkHours")):
            hours = INST[f"WorkHoursDatum_{wo_id}"]

            # Type and label the work-hours datum.
            g.add((hours, RDF.type, MWO.WorkHoursDatum))
            g.add((hours, RDFS.label, Literal(f"work hours for {row['MaintenanceWorkOrderActivity']}")))

            # Store the numeric hours value as an xsd:decimal literal.
            g.add((hours, LIS.datumValue, Literal(row["WorkHours"], datatype=XSD.decimal)))

            # Link the work order to its work-hours datum.
            g.add((wo, MWO.hasWorkHours, hours))

    # Write all triples in the graph to the output Turtle file.
    g.serialize(destination=OUT_PATH, format="turtle")

    # Print a short message so the user knows the script finished.
    print(f"Wrote {OUT_PATH} with {len(g)} triples")


# This standard Python pattern means:
# run main() only when this file is executed directly.
# If another script imports this file, main() will not run automatically.
if __name__ == "__main__":
    main()
