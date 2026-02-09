#!/usr/bin/env python3
"""
Convert OWL classes in vocab14224_basic.ttl to SKOS concepts in vocab14224_skos_basic.ttl.

What it does
------------
1) OWL/RDFS classes -> SKOS Concepts (in https://iso14224.org/skos/ with prefix iso14224:)
   - rdfs:subClassOf      -> skos:broader   (only when superclass is also a converted class)
   - rdfs:label           -> skos:prefLabel
   - skos:prefLabel       -> skos:prefLabel (carried over)
   - skos:altLabel        -> skos:altLabel  (carried over)
   - skos:definition      -> skos:definition (carried over)
   - skos:scopeNote       -> skos:scopeNote (carried over)
   - skos:example         -> skos:example   (carried over)
   - rdfs:comment         -> skos:definition (only if skos:definition not already present)

2) OWL Named Individuals -> skos:narrower relationships
   If an individual is typed as a class C that is converted to a concept, create:
        iso14224:<individualLocalName> skos:narrower iso14224:<classLocalName>

   Example input:
        voc:active_maintenance_time rdf:type owl:NamedIndividual, voc:TypeReliabilityMeasure .
   Output:
        iso14224:active_maintenance_time skos:narrower iso14224:TypeReliabilityMeasure .

   Also (for SKOS tooling consistency), the script types the mapped individual node as skos:Concept,
   adds skos:inScheme, and carries over SKOS annotations (pref/alt/definition/scopeNote/example) where present.

Requirements
------------
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

# SKOS annotation properties to carry over verbatim
SKOS_ANNOT_PROPS = (
    SKOS.prefLabel,
    SKOS.altLabel,
    SKOS.definition,
    SKOS.scopeNote,
    SKOS.example,
)


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


def add_literal_or_string(g: Graph, s: URIRef, p: URIRef, o) -> None:
    """Add object as-is if Literal, otherwise string-literal fallback."""
    if isinstance(o, Literal):
        g.add((s, p, o))
    else:
        g.add((s, p, Literal(str(o), lang="en")))


def carry_over_skos_annotations(g_in: Graph, g_out: Graph, src: URIRef, tgt: URIRef) -> None:
    """Copy selected SKOS annotation properties from src -> tgt."""
    for prop in SKOS_ANNOT_PROPS:
        for val in g_in.objects(src, prop):
            add_literal_or_string(g_out, tgt, prop, val)


def carry_over_pref_label_from_rdfs_label(g_in: Graph, g_out: Graph, src: URIRef, tgt: URIRef) -> None:
    """Copy rdfs:label -> skos:prefLabel (used when no skos:prefLabel exists)."""
    for lab in g_in.objects(src, RDFS.label):
        add_literal_or_string(g_out, tgt, SKOS.prefLabel, lab)


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

    # --------- Collect OWL/RDFS classes (URIs only; ignore blank-node class expressions) ---------
    classes = set(g_in.subjects(RDF.type, OWL.Class)) | set(g_in.subjects(RDF.type, RDFS.Class))
    classes = {c for c in classes if is_uriref(c)}

    # Map OWL class URI -> SKOS concept URI
    class_to_concept: dict[URIRef, URIRef] = {c: ISO14224[local_name(c)] for c in classes}

    # --------- Create concepts for classes ---------
    for c, concept in sorted(class_to_concept.items(), key=lambda kv: str(kv[0])):
        g_out.add((concept, RDF.type, SKOS.Concept))
        g_out.add((concept, SKOS.inScheme, SCHEME_URI))
        g_out.add((concept, DCTERMS.source, c))  # traceability

        # Carry over SKOS annotations first (pref/alt/definition/scopeNote/example)
        carry_over_skos_annotations(g_in, g_out, c, concept)

        # Ensure prefLabel exists (fallback to rdfs:label)
        if not any(g_out.objects(concept, SKOS.prefLabel)):
            carry_over_pref_label_from_rdfs_label(g_in, g_out, c, concept)

        # If no skos:definition already, optionally derive one from rdfs:comment
        if not any(g_out.objects(concept, SKOS.definition)):
            for com in g_in.objects(c, RDFS.comment):
                add_literal_or_string(g_out, concept, SKOS.definition, com)

    # --------- Map subclass hierarchy -> broader ---------
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
    # Named Individuals -> skos:narrower relationships + carry-over annotations
    # =====================================================================
    individuals = {s for s in g_in.subjects(RDF.type, OWL.NamedIndividual) if is_uriref(s)}

    for ind in sorted(individuals, key=lambda x: str(x)):
        ind_skos_uri = ISO14224[local_name(ind)]

        # Look at rdf:type assertions (excluding owl:NamedIndividual)
        for t in g_in.objects(ind, RDF.type):
            if t == OWL.NamedIndividual:
                continue
            if not is_uriref(t):
                continue

            if t in class_to_concept:
                # The requested mapping direction:
                g_out.add((ind_skos_uri, SKOS.narrower, class_to_concept[t]))

                # Make the individual-mapped resource a SKOS concept (helps tools/validators)
                g_out.add((ind_skos_uri, RDF.type, SKOS.Concept))
                g_out.add((ind_skos_uri, SKOS.inScheme, SCHEME_URI))
                g_out.add((ind_skos_uri, DCTERMS.source, ind))  # traceability

                # Carry over SKOS annotations from the individual if present
                carry_over_skos_annotations(g_in, g_out, ind, ind_skos_uri)

                # Ensure prefLabel exists for the individual concept
                if not any(g_out.objects(ind_skos_uri, SKOS.prefLabel)):
                    # fallback to rdfs:label
                    carry_over_pref_label_from_rdfs_label(g_in, g_out, ind, ind_skos_uri)

                # last-resort prefLabel fallback: local name
                if not any(g_out.objects(ind_skos_uri, SKOS.prefLabel)):
                    g_out.add((ind_skos_uri, SKOS.prefLabel, Literal(local_name(ind), lang="en")))

    # Write output
    OUT_FILE.write_text(g_out.serialize(format="turtle"), encoding="utf-8")
    print(f"Wrote: {OUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
