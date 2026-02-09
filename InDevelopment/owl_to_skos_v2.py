#!/usr/bin/env python3
"""
Convert OWL classes in vocab14224_basic.ttl to SKOS concepts in vocab14224_skos_basic.ttl.

Adds mapping for OWL named individuals:
If an individual has rdf:type someClass, and someClass is an OWL/RDFS class that we
converted to a SKOS concept, then create:

    iso14224:<individualLocalName> skos:narrower iso14224:<classLocalName>

Example input:
    voc:active_maintenance_time rdf:type owl:NamedIndividual , voc:TypeReliabilityMeasure .

Example output:
    iso14224:active_maintenance_time skos:narrower iso14224:TypeReliabilityMeasure .

Notes:
- We still create SKOS Concepts from OWL/RDFS classes:
    * rdfs:label -> skos:prefLabel
    * rdfs:comment -> skos:definition (change to skos:note if you prefer)
    * rdfs:subClassOf -> skos:broader
- For named individuals we DO NOT create concepts by default (unless you enable it);
  we just add skos:narrower relationships from the individual's mapped URI.
- Individuals are mapped into the same SKOS namespace https://iso14224.org/skos/
  using their local name.

Requirements:
    pip install rdflib
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, DCTERMS

# ---------- Files ----------
IN_FILE = Path("vocab14224_basic.ttl")
OUT_FILE = Path("vocab14224_skos_basic.ttl")

# ---------- Namespaces ----------
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
ISO14224 = Namespace("https://iso14224.org/skos/")  # requested new prefix/namespace

SCHEME_URI = URIRef("https://iso14224.org/skos/scheme/vocab14224_basic")


def local_name(u: URIRef) -> str:
    """Extract a local name from a URI (after #, else last path segment)."""
    s = str(u)
    if "#" in s:
        return s.rsplit("#", 1)[1]
    p = urlparse(s).path
    if p and p != "/":
        return p.rstrip("/").rsplit("/", 1)[-1]
    # Fallback: whole URI sanitized
    return s.replace("://", "_").replace("/", "_").replace("#", "_")


def is_uriref(x) -> bool:
    return isinstance(x, URIRef)


def main() -> None:
    if not IN_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {IN_FILE.resolve()}\n"
            "Put vocab14224_basic.ttl in the same folder as this script (or edit IN_FILE)."
        )

    g_in = Graph()
    g_in.parse(IN_FILE, format="turtle")

    g_out = Graph()
    g_out.bind("rdf", RDF)
    g_out.bind("rdfs", RDFS)
    g_out.bind("owl", OWL)
    g_out.bind("skos", SKOS)
    g_out.bind("dcterms", DCTERMS)
    g_out.bind("iso14224", ISO14224)  # requested prefix

    # Create the scheme
    g_out.add((SCHEME_URI, RDF.type, SKOS.ConceptScheme))
    g_out.add((SCHEME_URI, SKOS.prefLabel, Literal("ISO 14224 SKOS concept scheme (basic)", lang="en")))
    g_out.add((SCHEME_URI, DCTERMS.source, Literal(str(IN_FILE.name))))

    # --------- Collect OWL/RDFS classes (as URIs; ignore blank-node class expressions) ---------
    classes = set(g_in.subjects(RDF.type, OWL.Class)) | set(g_in.subjects(RDF.type, RDFS.Class))
    classes = {c for c in classes if is_uriref(c)}

    # Map OWL class URI -> SKOS concept URI
    class_to_concept: dict[URIRef, URIRef] = {}
    for c in sorted(classes, key=lambda x: str(x)):
        class_to_concept[c] = ISO14224[local_name(c)]

    # --------- Create concepts for classes ---------
    for c, concept in class_to_concept.items():
        g_out.add((concept, RDF.type, SKOS.Concept))
        g_out.add((concept, SKOS.inScheme, SCHEME_URI))

        # Copy labels: rdfs:label and/or existing skos:prefLabel
        labels = set(g_in.objects(c, RDFS.label)) | set(g_in.objects(c, SKOS.prefLabel))
        for lab in labels:
            if isinstance(lab, Literal):
                g_out.add((concept, SKOS.prefLabel, lab))
            else:
                g_out.add((concept, SKOS.prefLabel, Literal(str(lab), lang="en")))

        # Copy comments as definition
        for com in g_in.objects(c, RDFS.comment):
            if isinstance(com, Literal):
                g_out.add((concept, SKOS.definition, com))
            else:
                g_out.add((concept, SKOS.definition, Literal(str(com), lang="en")))

        # Preserve original class IRI for traceability
        g_out.add((concept, DCTERMS.source, c))

    # --------- Map subclass hierarchy -> broader ---------
    # Only map when superclass is also in our class set
    for sub in classes:
        sub_concept = class_to_concept[sub]
        for sup in g_in.objects(sub, RDFS.subClassOf):
            if not is_uriref(sup):
                continue
            if sup in class_to_concept:
                g_out.add((sub_concept, SKOS.broader, class_to_concept[sup]))

    # --------- Add top concepts (those with no broader) ---------
    for c in classes:
        concept = class_to_concept[c]
        if not any(g_out.objects(concept, SKOS.broader)):
            g_out.add((SCHEME_URI, SKOS.hasTopConcept, concept))
            g_out.add((concept, SKOS.topConceptOf, SCHEME_URI))

    # =====================================================================
    # NEW: Map OWL named individuals -> skos:narrower relations
    # =====================================================================
    # Find individuals typed as owl:NamedIndividual (URI only)
    individuals = {s for s in g_in.subjects(RDF.type, OWL.NamedIndividual) if is_uriref(s)}

    # For each individual, look at its rdf:type triples (excluding owl:NamedIndividual),
    # and if the type is one of the classes we converted, assert:
    #   iso14224:<individual> skos:narrower iso14224:<classConcept>
    for ind in sorted(individuals, key=lambda x: str(x)):
        ind_skos_uri = ISO14224[local_name(ind)]

        for t in g_in.objects(ind, RDF.type):
            if t == OWL.NamedIndividual:
                continue
            if not is_uriref(t):
                continue

            # Only map types that are classes we converted
            if t in class_to_concept:
                g_out.add((ind_skos_uri, SKOS.narrower, class_to_concept[t]))

                # (Optional but helpful) type the individual-mapped node as a SKOS Concept too,
                # so validators and SKOS tools treat it consistently.
                g_out.add((ind_skos_uri, RDF.type, SKOS.Concept))
                g_out.add((ind_skos_uri, SKOS.inScheme, SCHEME_URI))
                g_out.add((ind_skos_uri, DCTERMS.source, ind))

                # Copy a label if the individual has one; otherwise, fall back to local name.
                ind_labels = set(g_in.objects(ind, RDFS.label)) | set(g_in.objects(ind, SKOS.prefLabel))
                if ind_labels:
                    for lab in ind_labels:
                        if isinstance(lab, Literal):
                            g_out.add((ind_skos_uri, SKOS.prefLabel, lab))
                        else:
                            g_out.add((ind_skos_uri, SKOS.prefLabel, Literal(str(lab), lang="en")))
                else:
                    g_out.add((ind_skos_uri, SKOS.prefLabel, Literal(local_name(ind), lang="en")))

    # Write output
    OUT_FILE.write_text(g_out.serialize(format="turtle"), encoding="utf-8")
    print(f"Wrote: {OUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
