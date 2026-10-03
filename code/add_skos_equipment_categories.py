import re

APPENDIX_A_FILE = "../i14224_appendixA.ttl"
SKOS_FILE = "iso14224_skos_ApA_with_codes.ttl"
OUTPUT_FILE = "iso14224_skos_ApA_with_codes_and_categories.ttl"

# Matches each block in i14224_appendixA.ttl, e.g.:
# ###  https://iso14224.org/ontology/i14224/rdl/CombustionEngine
# i14224:CombustionEngine
#     rdf:type owl:Class ;
#     ...
#     i14224:equipment_category "rotating equipment"@en ;
#     ...
#     cmnsav:directSource "ISO 14224:2023 Appendix A"@en .
APPENDIX_BLOCK_RE = re.compile(
    r"###\s+https://iso14224\.org/ontology/i14224/rdl/(\w+)\s*\n"
    r"i14224:\w+\s*\n"
    r"(?P<body>(?:.*?\n)*?)"
    r"\s*cmnsav:directSource \"[^\"]*\"@en \.\n?",
    re.MULTILINE,
)

# Matches each block in iso14224_skos_ApA_with_codes.ttl, e.g.:
# ### https://iso14224.org/skos/CombustionEngine
# i14224skos:CombustionEngine
#     a skos:Concept ;
#     ...
#     i14224skos:hasEquipmentCode i14224skos:CE .
SKOS_BLOCK_RE = re.compile(
    r"(### https://iso14224\.org/skos/(\w+)\s*\n"
    r"i14224skos:\w+\s*\n"
    r"(?:.*?\n)*?"
    r"\s*i14224skos:hasEquipmentCode\s+i14224skos:\w+)"
    r"(\s*\.\s*\n?)",
    re.MULTILINE,
)

LEVEL6_RE = re.compile(r'i14224skos:taxonomicLevelNumber\s+"Level 6"')

# Map free-text equipment_category values (lowercased) found in i14224_appendixA.ttl
# to the SKOS category concept local names already defined in the SKOS file's
# "Equipment category" section (i14224skos:RotatingEquipment, etc.)
CATEGORY_LABEL_TO_CONCEPT = {
    "rotating equipment": "RotatingEquipment",
    "mechanical equipment": "MechanicalEquipment",
    "electrical equipment": "ElectricalEquipment",
    "safety and control equipment": "SafetyAndControlEquipment",
    "subsea production equipment": "SubseaEquipment",
    "well completion equipment": "WellCompletionEquipment",
    "drilling equipment": "DrillingEquipment",
    "well intervention equipment": "WellInterventionEquipment",
    "marine equipment": "MarineEquipment",
    "utilities equipment": "UtilitiesEquipment",
    "auxiliaries equipment": "AuxiliariesEquipment",
}


def extract_equipment_category(body):
    """Extract the equipment_category text value, e.g. 'rotating equipment'."""
    m = re.search(r'i14224:equipment_category\s+"([^"]+)"@en', body)
    return m.group(1) if m else None


def build_name_to_category_map(appendix_a_content):
    """Parse i14224_appendixA.ttl and build {EntityName: CategoryConceptLocalName}."""
    mapping = {}
    unmapped_labels = set()

    for match in APPENDIX_BLOCK_RE.finditer(appendix_a_content):
        name = match.group(1)
        body = match.group("body")
        label = extract_equipment_category(body)
        if not label:
            continue

        concept = CATEGORY_LABEL_TO_CONCEPT.get(label.strip().lower())
        if concept:
            mapping[name] = concept
        else:
            unmapped_labels.add(label)

    return mapping, unmapped_labels


def add_categories_to_skos_blocks(skos_content, name_to_category):
    matched_names = set()
    updated_names = []
    skipped_not_level6 = []
    unmapped_names = []

    def repl(match):
        block_body = match.group(1)
        name = match.group(2)
        end = match.group(3)

        matched_names.add(name)

        if not LEVEL6_RE.search(block_body):
            skipped_not_level6.append(name)
            return block_body + end

        category = name_to_category.get(name)
        if category is None:
            unmapped_names.append(name)
            return block_body + end

        updated_names.append(name)
        new_block = block_body.rstrip() + " ;\n"
        new_block += f"    i14224skos:hasEquipmentCategory i14224skos:{category} ."
        return new_block + "\n"

    new_content = SKOS_BLOCK_RE.sub(repl, skos_content)
    return new_content, matched_names, updated_names, skipped_not_level6, unmapped_names


def main():
    with open(APPENDIX_A_FILE, "r", encoding="utf-8") as f:
        appendix_a_content = f.read()

    with open(SKOS_FILE, "r", encoding="utf-8") as f:
        skos_content = f.read()

    name_to_category, unmapped_labels = build_name_to_category_map(appendix_a_content)
    print(f"[appendixA] Parsed {len(name_to_category)} name->category mappings.")
    if unmapped_labels:
        print(
            f"WARNING: {len(unmapped_labels)} distinct equipment_category label(s) "
            f"had no matching SKOS concept: {sorted(unmapped_labels)}"
        )

    total_skos_blocks = len(re.findall(r"### https://iso14224\.org/skos/\w+", skos_content))
    print(f"[skos file] Found {total_skos_blocks} '### https://iso14224.org/skos/...' headers.")

    (
        new_skos_content,
        matched_names,
        updated_names,
        skipped_not_level6,
        unmapped_names,
    ) = add_categories_to_skos_blocks(skos_content, name_to_category)

    print(f"[skos file] Successfully matched {len(matched_names)} blocks (regex-level match).")
    if len(matched_names) < total_skos_blocks:
        print(
            f"WARNING: {total_skos_blocks - len(matched_names)} block(s) were NOT matched "
            "by SKOS_BLOCK_RE (check they already have hasEquipmentCode)."
        )

    print(f"[categories] Added hasEquipmentCategory to {len(updated_names)} Level 6 entities.")
    print(f"[categories] Skipped {len(skipped_not_level6)} entities (not Level 6).")

    if unmapped_names:
        print(
            f"\n*** {len(unmapped_names)} Level 6 entities had NO category mapping in "
            f"{APPENDIX_A_FILE} — PLEASE REVIEW: ***"
        )
        for n in sorted(unmapped_names):
            print(f"    - {n}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_skos_content)

    print(f"\nOutput written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()