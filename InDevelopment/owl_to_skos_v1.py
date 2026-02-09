#!/usr/bin/env python3
"""
Convert OWL classes in vocab14224_basic.ttl to SKOS concepts in vocab14224_skos_basic.ttl.

- Reads:  vocab14224_basic.ttl
- Writes: vocab14224_skos_basic.ttl
- Creates SKOS concepts in namespace: https://iso14224.org/skos/  (prefix iso14224:)
- For each owl:Class (and rdfs:Class) found:
    * Create iso14224:<localName> a skos:Concept
    * Copy rdfs:label -> skos:prefLabel
    * Copy skos:prefLabel if already present
    * Copy rdfs:comment -> skos:note (feel free to change to skos:note)
    * Map rdfs:subClassOf (when superclass is also a class) -> skos:broader
- Creates a ConceptScheme: https://iso14224.org/skos/scheme/vocab14224_basic
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, OWL, DCTERMS

# ---------- Files ----------
IN_FILE = Path("vocab14224_basic.ttl")
OUT_FILE = Path("vocab14224_skos_basic.ttl")

# ---------- Namespaces ----------
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
ISO14224 = Namespace("https://iso14224.org/skos/")  # requested new prefix/namespace

SCHEME_URI = URIRef("https://iso14224.org/skos/scheme/vocab14224_basic")


def local_name(u: URIRef) -> str:
    """
    Extract a local name from a URI (after #, else last path segment).
    """
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

    # Collect classes
    classes = set(g_in.subjects(RDF.type, OWL.Class)) | set(g_in.subjects(RDF.type, RDFS.Class))
    # Keep only URI classes (ignore blank nodes)
    classes = {c for c in classes if is_uriref(c)}

    # Map OWL class URI -> SKOS concept URI
    class_to_concept: dict[URIRef, URIRef] = {}
    for c in sorted(classes, key=lambda x: str(x)):
        ln = local_name(c)
        class_to_concept[c] = ISO14224[ln]

    # Create concepts and copy labels/notes
    for c, concept in class_to_concept.items():
        g_out.add((concept, RDF.type, SKOS.Concept))
        g_out.add((concept, SKOS.inScheme, SCHEME_URI))

        # Copy labels:
        # - rdfs:label -> skos:prefLabel
        # - skos:prefLabel -> skos:prefLabel (if your source already had it)
        labels = set(g_in.objects(c, RDFS.label)) | set(g_in.objects(c, SKOS.prefLabel))
        for lab in labels:
            if isinstance(lab, Literal):
                g_out.add((concept, SKOS.prefLabel, lab))
            else:
                g_out.add((concept, SKOS.prefLabel, Literal(str(lab), lang="en")))

        # Copy comments as definition (common choice)
        for com in g_in.objects(c, RDFS.comment):
            if isinstance(com, Literal):
                g_out.add((concept, SKOS.definition, com))
            else:
                g_out.add((concept, SKOS.definition, Literal(str(com), lang="en")))

        # Preserve original class IRI for traceability (optional but useful)
        g_out.add((concept, DCTERMS.source, c))

    # Map subclass hierarchy -> broader
    # Only map when superclass is also in our class set (i.e., in class_to_concept)
    for sub in classes:
        sub_concept = class_to_concept[sub]
        for sup in g_in.objects(sub, RDFS.subClassOf):
            if not is_uriref(sup):
                continue
            if sup in class_to_concept:
                sup_concept = class_to_concept[sup]
                g_out.add((sub_concept, SKOS.broader, sup_concept))

    # Add top concepts (those with no broader)
    for c in classes:
        concept = class_to_concept[c]
        has_broader = any(g_out.objects(concept, SKOS.broader))
        if not has_broader:
            g_out.add((SCHEME_URI, SKOS.hasTopConcept, concept))
            g_out.add((concept, SKOS.topConceptOf, SCHEME_URI))

    # Write output
    ttl = g_out.serialize(format="turtle")
    OUT_FILE.write_text(ttl, encoding="utf-8")
    print(f"Wrote: {OUT_FILE.resolve()}")


if __name__ == "__main__":
    main()


