import re

APPENDIX_A_FILE = "../i14224_appendixA.ttl"
SKOS_FILE = "iso14224_skos_ApA.ttl"
OUTPUT_FILE = "iso14224_skos_ApA_level7_updated.ttl"

# Matches each block in i14224_appendixA.ttl, e.g.:
# ###  https://iso14224.org/ontology/i14224/rdl/DieselEngine
# i14224:DieselEngine
#     rdf:type owl:Class ;
#     rdfs:subClassOf i14224:CombustionEngine ;
#     ...
#     i14224:equipment_class_level "Level 7"@en ;
#     ...
#     cmnsav:directSource "ISO 14224:2023 Appendix A"@en .
APPENDIX_BLOCK_RE = re.compile(
    r"###\s+https://iso14224\.org/ontology/i14224/rdl/(\w+)\s*\n"
    r"i14224:\w+\s*\n"
    r"(?P<body>(?:.*?\n)*?)"
    r"\s*cmnsav:directSource \"[^\"]*\"@en \.\n?",
    re.MULTILINE,
)

# Matches each Level 6 or Level 7 block in iso14224_skos_ApA.ttl. Level 6 blocks end
# with hasEquipmentCategory, Level 7 blocks end with hasEquipmentCode. We capture the
# whole block up to its terminating '.' so we can inspect/modify contents.
SKOS_BLOCK_RE = re.compile(
    r"(### https://iso14224\.org/skos/(\w+)\s*\n"
    r"i14224skos:\w+\s*\n"
    r"(?:.*?\n)*?)"
    r"(\s*i14224skos:hasEquipmentCode\s+i14224skos:\S+\s*"
    r"(?:;\s*\n\s*i14224skos:hasEquipmentCategory\s+i14224skos:\S+\s*)?)"
    r"(\.\s*\n?)",
    re.MULTILINE,
)

LEVEL7_RE = re.compile(r'i14224skos:taxonomicLevelNumber\s+"Level 7"')


def extract_equipment_class_level(body):
    """Extract the equipment_class_level text value, e.g. 'Level 7'."""
    m = re.search(r'i14224:equipment_class_level\s+"([^"]+)"@en', body)
    return m.group(1) if m else None


def extract_subclass_of(body):
    """Extract the rdfs:subClassOf local name, e.g. 'CombustionEngine'."""
    m = re.search(r'rdfs:subClassOf\s+i14224:(\w+)\s*;', body)
    return m.group(1) if m else None


def build_name_to_parent_map(appendix_a_content):
    """Parse i14224_appendixA.ttl and build {EntityName: ParentLocalName}
    for entities at Level 7 that have an rdfs:subClassOf parent."""
    mapping = {}

    for match in APPENDIX_BLOCK_RE.finditer(appendix_a_content):
        name = match.group(1)
        body = match.group("body")

        level = extract_equipment_class_level(body)
        if level != "Level 7":
            continue

        parent = extract_subclass_of(body)
        if parent:
            mapping[name] = parent

    return mapping


def update_skos_blocks(skos_content, name_to_parent):
    matched_names = set()
    changed_to_equipment_type = []
    added_broader = []
    skipped_no_parent = []

    def repl(match):
        prefix = match.group(1)   # up to (not including) hasEquipmentCode line
        core = match.group(2)     # hasEquipmentCode [; hasEquipmentCategory ...]
        end = match.group(3)      # trailing '.' and newline
        name = re.search(r"### https://iso14224\.org/skos/(\w+)", prefix).group(1)

        matched_names.add(name)

        is_level7 = LEVEL7_RE.search(prefix) is not None

        new_prefix = prefix

        if is_level7:
            # Task 1: change mapsToTerm i14224skos:EquipmentClass -> EquipmentType
            if re.search(r"i14224skos:mapsToTerm\s+i14224skos:EquipmentClass\s*;", new_prefix):
                new_prefix = re.sub(
                    r"(i14224skos:mapsToTerm\s+i14224skos:)EquipmentClass(\s*;)",
                    r"\1EquipmentType\2",
                    new_prefix,
                )
                changed_to_equipment_type.append(name)

            # Task 2: add skos:broader if a parent mapping exists
            parent = name_to_parent.get(name)
            if parent:
                # Insert "skos:broader i14224skos:Parent ;" right after the
                # taxonomicClassificationLevel line (or right before hasEquipmentCode)
                new_core = core.rstrip()
                # core currently starts with the hasEquipmentCode line; we need to
                # inject skos:broader BEFORE it, replacing the trailing ';' logic.
                # Easiest: append skos:broader as an additional statement before core.
                new_prefix = new_prefix.rstrip()
                if not new_prefix.endswith(";"):
                    new_prefix += " ;"
                new_prefix += f"\n    skos:broader i14224skos:{parent} ;\n"
                added_broader.append(name)
            else:
                skipped_no_parent.append(name)

        return new_prefix + core + end

    new_content = SKOS_BLOCK_RE.sub(repl, skos_content)
    return new_content, matched_names, changed_to_equipment_type, added_broader, skipped_no_parent


def main():
    with open(APPENDIX_A_FILE, "r", encoding="utf-8") as f:
        appendix_a_content = f.read()

    with open(SKOS_FILE, "r", encoding="utf-8") as f:
        skos_content = f.read()

    name_to_parent = build_name_to_parent_map(appendix_a_content)
    print(f"[appendixA] Parsed {len(name_to_parent)} Level 7 name->parent mappings.")

    total_skos_blocks = len(re.findall(r"### https://iso14224\.org/skos/\w+", skos_content))
    print(f"[skos file] Found {total_skos_blocks} '### https://iso14224.org/skos/...' headers.")

    (
        new_skos_content,
        matched_names,
        changed_to_equipment_type,
        added_broader,
        skipped_no_parent,
    ) = update_skos_blocks(skos_content, name_to_parent)

    print(f"[skos file] Successfully matched {len(matched_names)} blocks (regex-level match).")
    if len(matched_names) < total_skos_blocks:
        print(
            f"WARNING: {total_skos_blocks - len(matched_names)} block(s) were NOT matched "
            "by SKOS_BLOCK_RE."
        )

    print(f"[task 1] Changed mapsToTerm EquipmentClass -> EquipmentType for "
          f"{len(changed_to_equipment_type)} Level 7 entities.")
    print(f"[task 2] Added skos:broader to {len(added_broader)} Level 7 entities.")

    level7_skipped = [n for n in skipped_no_parent]
    if level7_skipped:
        print(
            f"\n*** {len(level7_skipped)} Level 7 entities had NO rdfs:subClassOf parent "
            f"in {APPENDIX_A_FILE} (no skos:broader added) — for review: ***"
        )
        for n in sorted(level7_skipped):
            print(f"    - {n}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_skos_content)

    print(f"\nOutput written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()