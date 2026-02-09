#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
import re

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, DCTERMS

# ---------- Files ----------
IN_FILE = Path("vocab14224_basic.ttl")
OUT_FILE = Path("vocab14224_skos_basic.ttl")

# ---------- Namespaces ----------
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
ISO14224 = Namespace("https://iso14224.org/skos/")
SCHEME_URI = URIRef("https://iso14224.org/skos/scheme/vocab14224_basic")

SKOS_ANNOT_PROPS = (
    SKOS.prefLabel,
    SKOS.altLabel,
    SKOS.definition,
    SKOS.scopeNote,
    SKOS.example,
)

# -------------------------------------------------
# Utility Functions
# -------------------------------------------------

def is_uriref(x):
    return isinstance(x, URIRef)


def local_name(u: URIRef) -> str:
    s = str(u)
    if "#" in s:
        return s.rsplit("#", 1)[1]
    p = urlparse(s).path
    return p.rstrip("/").rsplit("/", 1)[-1]


def is_single_word_all_lower(name: str) -> bool:
    if "_" in name:
        return False
    if not re.fullmatch(r"[a-z0-9]+", name):
        return False
    return any("a" <= ch <= "z" for ch in name)


def to_upper_camel_from_underscore(name: str) -> str:
    parts = name.split("_")
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def transform_local(name: str) -> str:
    if "_" in name:
        return to_upper_camel_from_underscore(name)
    if is_single_word_all_lower(name):
        return name[:1].upper() + name[1:]
    return name


def replace_uri_local(u: URIRef, new_local: str) -> URIRef:
    s = str(u)
    if "#" in s:
        base = s.rsplit("#", 1)[0]
        return URIRef(f"{base}#{new_local}")
    if s.endswith("/"):
        s = s[:-1]
    base = s.rsplit("/", 1)[0]
    return URIRef(f"{base}/{new_local}")


# ---------- NEW: normalize label to start lowercase ----------

def normalize_label_literal(lit: Literal) -> Literal:
    """
    Ensure prefLabel and altLabel start with lowercase.
    Only modifies first character.
    Preserves language and datatype.
    """
    if not isinstance(lit, Literal):
        return Literal(str(lit), lang="en")

    text = str(lit)
    if not text:
        return lit

    new_text = text[0].lower() + text[1:]

    return Literal(new_text, lang=lit.language, datatype=lit.datatype)


def add_literal_or_string(g: Graph, s: URIRef, p: URIRef, o):
    if isinstance(o, Literal):
        g.add((s, p, o))
    else:
        g.add((s, p, Literal(str(o), lang="en")))


def carry_over_skos_annotations(g_in: Graph, g_out: Graph, src: URIRef, tgt: URIRef):
    for prop in SKOS_ANNOT_PROPS:
        for val in g_in.objects(src, prop):

            # Normalize prefLabel and altLabel to lowercase start
            if prop in (SKOS.prefLabel, SKOS.altLabel):
                val = normalize_label_literal(val)

            add_literal_or_string(g_out, tgt, prop, val)


def carry_over_pref_from_rdfs(g_in: Graph, g_out: Graph, src: URIRef, tgt: URIRef):
    for lab in g_in.objects(src, RDFS.label):
        lab = normalize_label_literal(lab)
        add_literal_or_string(g_out, tgt, SKOS.prefLabel, lab)


# -------------------------------------------------
# Main
# -------------------------------------------------

def main():

    if not IN_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {IN_FILE.resolve()}")

    g_in = Graph()
    g_in.parse(IN_FILE, format="turtle")

    g_out = Graph()
    g_out.bind("rdf", RDF)
    g_out.bind("rdfs", RDFS)
    g_out.bind("owl", OWL)
    g_out.bind("skos", SKOS)
    g_out.bind("dcterms", DCTERMS)
    g_out.bind("iso14224", ISO14224)

    # ConceptScheme
    g_out.add((SCHEME_URI, RDF.type, SKOS.ConceptScheme))
    g_out.add((SCHEME_URI, SKOS.prefLabel,
               Literal("iso 14224 skos concept scheme (basic)", lang="en")))
    g_out.add((SCHEME_URI, DCTERMS.source, Literal(IN_FILE.name)))

    # ---------------------------
    # OWL Classes -> Concepts
    # ---------------------------
    classes = set(g_in.subjects(RDF.type, OWL.Class)) | \
              set(g_in.subjects(RDF.type, RDFS.Class))
    classes = {c for c in classes if is_uriref(c)}

    class_to_concept = {}
    class_to_source_uri = {}

    for c in classes:
        old_ln = local_name(c)
        new_ln = transform_local(old_ln)
        class_to_concept[c] = ISO14224[new_ln]
        class_to_source_uri[c] = replace_uri_local(c, new_ln) if new_ln != old_ln else c

    for c, concept in class_to_concept.items():

        g_out.add((concept, RDF.type, SKOS.Concept))
        g_out.add((concept, SKOS.inScheme, SCHEME_URI))
        g_out.add((concept, DCTERMS.source, class_to_source_uri[c]))

        carry_over_skos_annotations(g_in, g_out, c, concept)

        if not any(g_out.objects(concept, SKOS.prefLabel)):
            carry_over_pref_from_rdfs(g_in, g_out, c, concept)

        if not any(g_out.objects(concept, SKOS.definition)):
            for com in g_in.objects(c, RDFS.comment):
                add_literal_or_string(g_out, concept, SKOS.definition, com)

    # subclass -> broader
    for sub in classes:
        for sup in g_in.objects(sub, RDFS.subClassOf):
            if is_uriref(sup) and sup in class_to_concept:
                g_out.add((class_to_concept[sub], SKOS.broader, class_to_concept[sup]))

    # Top concepts
    for c in classes:
        concept = class_to_concept[c]
        if not any(g_out.objects(concept, SKOS.broader)):
            g_out.add((SCHEME_URI, SKOS.hasTopConcept, concept))
            g_out.add((concept, SKOS.topConceptOf, SCHEME_URI))

    # ---------------------------
    # Named Individuals -> skos:narrower
    # ---------------------------
    individuals = {s for s in g_in.subjects(RDF.type, OWL.NamedIndividual)
                   if is_uriref(s)}

    for ind in individuals:

        old_ln = local_name(ind)
        new_ln = transform_local(old_ln)

        ind_concept = ISO14224[new_ln]
        ind_source = replace_uri_local(ind, new_ln) if new_ln != old_ln else ind

        linked_any = False

        for t in g_in.objects(ind, RDF.type):
            if t == OWL.NamedIndividual:
                continue
            if is_uriref(t) and t in class_to_concept:
                g_out.add((ind_concept, SKOS.narrower, class_to_concept[t]))
                linked_any = True

        if linked_any:
            g_out.add((ind_concept, RDF.type, SKOS.Concept))
            g_out.add((ind_concept, SKOS.inScheme, SCHEME_URI))
            g_out.add((ind_concept, DCTERMS.source, ind_source))

            carry_over_skos_annotations(g_in, g_out, ind, ind_concept)

            if not any(g_out.objects(ind_concept, SKOS.prefLabel)):
                carry_over_pref_from_rdfs(g_in, g_out, ind, ind_concept)

            if not any(g_out.objects(ind_concept, SKOS.prefLabel)):
                g_out.add((
                    ind_concept,
                    SKOS.prefLabel,
                    Literal(new_ln[0].lower() + new_ln[1:], lang="en")
                ))

    OUT_FILE.write_text(g_out.serialize(format="turtle"), encoding="utf-8")
    print(f"Wrote: {OUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
