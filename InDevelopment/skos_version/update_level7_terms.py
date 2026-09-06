import re
import sys
import os

print("=" * 60)
print("SCRIPT VERSION MARKER: update_level7_terms_v4")
print(f"Running from: {os.path.abspath(__file__)}")
print(f"Working directory: {os.getcwd()}")
print("=" * 60)
sys.stdout.flush()

APPENDIX_A_FILE = "../i14224_appendixA.ttl"
SKOS_FILE = "iso14224_skos_ApA_rebuilt.ttl"
OUTPUT_FILE = "iso14224_skos_ApA_level7_updated.ttl"

APPENDIX_BLOCK_RE = re.compile(
    r"###\s+https://iso14224\.org/ontology/i14224/rdl/(\w+)\s*\n"
    r"i14224:\w+\s*\n"
    r"(?P<body>(?:.*?\n)*?)"
    r"\s*cmnsav:directSource \"[^\"]*\"@en \.\n?",
    re.MULTILINE,
)

HEADER_RE = re.compile(r"### https://iso14224\.org/skos/(\w+)")
LEVEL7_RE = re.compile(r'i14224skos:taxonomicLevelNumber\s+"Level 7"')


def extract_equipment_class_level(body):
    m = re.search(r'i14224:equipment_class_level\s+"([^"]+)"@en', body)
    return m.group(1) if m else None


def extract_subclass_of(body):
    m = re.search(r'rdfs:subClassOf\s+i14224:(\w+)', body)
    if not m:
        return None
    parent = m.group(1)
    if parent == "EquipmentByType":
        return None
    return parent


def build_name_to_parent_map(appendix_a_content):
    mapping = {}
    all_matches = list(APPENDIX_BLOCK_RE.finditer(appendix_a_content))
    print(f"[DEBUG] APPENDIX_BLOCK_RE.finditer returned {len(all_matches)} matches.")

    level7_count = 0
    for match in all_matches:
        name = match.group(1)
        body = match.group("body")
        level = extract_equipment_class_level(body)
        if level == "Level 7":
            level7_count += 1
            parent = extract_subclass_of(body)
            if parent:
                mapping[name] = parent

    print(f"[DEBUG] Total blocks classified as Level 7: {level7_count}")
    print(f"[DEBUG] Total Level 7 mappings with parent extracted: {len(mapping)}")
    return mapping


def process_skos_file(skos_content, name_to_parent):
    """Split by '### .../skos/Name' headers, process each block individually,
    then rejoin. This avoids relying on a single fragile block-matching regex."""
    header_matches = list(HEADER_RE.finditer(skos_content))
    print(f"[DEBUG] Found {len(header_matches)} skos block headers.")

    if not header_matches:
        print("[ERROR] No headers found in SKOS file — aborting.")
        return skos_content, 0, 0

    preamble = skos_content[: header_matches[0].start()]

    pieces = [preamble]
    changed_to_equipment_type = 0
    added_broader = 0
    skipped_no_parent = []

    for i, m in enumerate(header_matches):
        name = m.group(1)
        block_start = m.start()
        block_end = header_matches[i + 1].start() if i + 1 < len(header_matches) else len(skos_content)
        block_text = skos_content[block_start:block_end]

        if LEVEL7_RE.search(block_text):
            new_block = block_text

            # Task 1: EquipmentClass -> EquipmentType
            if re.search(r"i14224skos:mapsToTerm\s+i14224skos:EquipmentClass\s*;", new_block):
                new_block = re.sub(
                    r"(i14224skos:mapsToTerm\s+i14224skos:)EquipmentClass(\s*;)",
                    r"\1EquipmentType\2",
                    new_block,
                )
                changed_to_equipment_type += 1

            # Task 2: insert skos:broader before hasEquipmentCode line
            parent = name_to_parent.get(name)
            if parent:
                new_block2 = re.sub(
                    r"([ \t]*)(i14224skos:hasEquipmentCode\s+i14224skos:\S+\s*\.\s*\n?)",
                    rf"\1skos:broader i14224skos:{parent} ;\n\1\2",
                    new_block,
                    count=1,
                )
                if new_block2 != new_block:
                    added_broader += 1
                    new_block = new_block2
                else:
                    skipped_no_parent.append(name)
            else:
                skipped_no_parent.append(name)

            block_text = new_block

        pieces.append(block_text)

    if skipped_no_parent:
        print(f"[DEBUG] {len(skipped_no_parent)} Level 7 entities had no parent / no insertion made:")
        print(f"    {sorted(skipped_no_parent)}")

    return "".join(pieces), changed_to_equipment_type, added_broader


def main():
    if not os.path.exists(APPENDIX_A_FILE):
        print(f"[FATAL] File not found: {os.path.abspath(APPENDIX_A_FILE)}")
        sys.exit(1)
    if not os.path.exists(SKOS_FILE):
        print(f"[FATAL] File not found: {os.path.abspath(SKOS_FILE)}")
        sys.exit(1)

    with open(APPENDIX_A_FILE, "r", encoding="utf-8") as f:
        appendix_a_content = f.read()
    print(f"[DEBUG] Read {len(appendix_a_content)} characters from {APPENDIX_A_FILE}")

    with open(SKOS_FILE, "r", encoding="utf-8") as f:
        skos_content = f.read()
    print(f"[DEBUG] Read {len(skos_content)} characters from {SKOS_FILE}")

    name_to_parent = build_name_to_parent_map(appendix_a_content)
    print(f"[appendixA] Parsed {len(name_to_parent)} Level 7 name->parent mappings.")

    new_skos_content, changed_to_equipment_type, added_broader = process_skos_file(
        skos_content, name_to_parent
    )

    print(f"[task 1] Changed EquipmentClass->EquipmentType for {changed_to_equipment_type} entities.")
    print(f"[task 2] Added skos:broader to {added_broader} entities.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_skos_content)

    print(f"\nOutput written to {os.path.abspath(OUTPUT_FILE)}")
    print("SCRIPT VERSION MARKER: update_level7_terms_v4 -- COMPLETED")


if __name__ == "__main__":
    main()