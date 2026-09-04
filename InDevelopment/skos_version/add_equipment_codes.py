import re

# Adjust these paths if your files are located elsewhere
APPENDIX_A_FILE = "../i14224_appendixA.ttl"
SKOS_FILE = "iso14224_skos_ApA.ttl"
OUTPUT_FILE = "iso14224_skos_ApA_with_codes.ttl"

# Matches each old-style block in i14224_appendixA.ttl, e.g.:
# ###  https://iso14224.org/ontology/i14224/rdl/CombustionEngine
# i14224:CombustionEngine
#     rdf:type owl:Class ;
#     ...
#     i14224:hasEquipmentCode i14224:CE ;
#     ...
#     cmnsav:directSource "ISO 14224:2023 Appendix A"@en .
APPENDIX_BLOCK_RE = re.compile(
    r"###\s+https://iso14224\.org/ontology/i14224/rdl/(\w+)\s*\n"
    r"i14224:\w+\s*\n"
    r"(?P<body>(?:.*?\n)*?)"
    r"\s*cmnsav:directSource \"[^\"]*\"@en \.\n?",
    re.MULTILINE,
)

# Matches each compact block in iso14224_skos_ApA.ttl, e.g.:
# ### https://iso14224.org/skos/CombustionEngine
# i14224skos:CombustionEngine
#     a skos:Concept ;
#     skos:prefLabel "Combustion engine"@en ;
#     i14224skos:mapsToTerm i14224skos:EquipmentClass ;
#     i14224skos:taxonomicLevelNumber "Level 6" ;
#     i14224skos:taxonomicClassificationLevel i14224skos:EquipmentUnit .
SKOS_BLOCK_RE = re.compile(
    r"(### https://iso14224\.org/skos/(\w+)\s*\n"
    r"i14224skos:\w+\s*\n"
    r"(?:.*?\n)*?"
    r"\s*i14224skos:taxonomicClassificationLevel\s+i14224skos:\w+\s*)"
    r"(\.\s*\n?)",
    re.MULTILINE,
)


def extract_equipment_code(body):
    """Extract equipment code local name from i14224:hasEquipmentCode i14224:XX ;"""
    m = re.search(r"i14224:hasEquipmentCode\s+i14224:(\w+)\s*;", body)
    return m.group(1) if m else None


def build_name_to_code_map(appendix_a_content):
    """Parse i14224_appendixA.ttl and build a dict: {EntityName: EquipmentCode}."""
    mapping = {}
    for match in APPENDIX_BLOCK_RE.finditer(appendix_a_content):
        name = match.group(1)
        body = match.group("body")
        code = extract_equipment_code(body)
        if code:
            mapping[name] = code
    return mapping


def add_codes_to_skos_blocks(skos_content, name_to_code):
    """Find each i14224skos:Name block and insert
    i14224skos:hasEquipmentCode i14224skos:XX . before the closing '.'
    Includes NoEquipmentCodeSpecified entries so they can be reviewed.
    """
    used_codes = set()
    matched_names = set()
    no_code_names = []   # entities mapped to NoEquipmentCodeSpecified
    unmapped_names = []  # entities with no entry at all in appendixA

    def repl(match):
        block_body = match.group(1)
        name = match.group(2)
        end = match.group(3)

        matched_names.add(name)
        code = name_to_code.get(name)

        if code is None:
            unmapped_names.append(name)
            return block_body + end

        used_codes.add(code)
        if code == "NoEquipmentCodeSpecified":
            no_code_names.append(name)

        new_block = block_body.rstrip() + " ;\n"
        new_block += f"    i14224skos:hasEquipmentCode i14224skos:{code} .\n"
        return new_block

    new_content = SKOS_BLOCK_RE.sub(repl, skos_content)
    return new_content, used_codes, matched_names, no_code_names, unmapped_names


def build_equipment_code_collection(used_codes):
    """Build skos:Concept declarations + skos:Collection for all equipment codes."""
    sorted_codes = sorted(used_codes)
    lines = []
    lines.append("#################################################################")
    lines.append("#    Equipment codes")
    lines.append("#################################################################\n")

    for code in sorted_codes:
        lines.append(f"i14224skos:{code}")
        lines.append("    a skos:Concept ;")
        lines.append(f'    skos:prefLabel "{code}"@en .\n')

    lines.append("i14224skos:Equipment a skos:Collection ;")
    lines.append("    skos:member")
    member_lines = [f"        i14224skos:{code}" for code in sorted_codes]
    lines.append(",\n".join(member_lines) + " .")

    return "\n".join(lines) + "\n"


def main():
    with open(APPENDIX_A_FILE, "r", encoding="utf-8") as f:
        appendix_a_content = f.read()

    with open(SKOS_FILE, "r", encoding="utf-8") as f:
        skos_content = f.read()

    name_to_code = build_name_to_code_map(appendix_a_content)
    print(f"[appendixA] Parsed {len(name_to_code)} name->code mappings.")

    total_skos_blocks = len(re.findall(r"### https://iso14224\.org/skos/\w+", skos_content))
    print(f"[skos file] Found {total_skos_blocks} '### https://iso14224.org/skos/...' headers.")

    (
        new_skos_content,
        used_codes,
        matched_names,
        no_code_names,
        unmapped_names,
    ) = add_codes_to_skos_blocks(skos_content, name_to_code)

    print(f"[skos file] Successfully matched & processed {len(matched_names)} blocks.")
    if len(matched_names) < total_skos_blocks:
        print(
            f"WARNING: {total_skos_blocks - len(matched_names)} block(s) were NOT matched "
            "by SKOS_BLOCK_RE."
        )

    if unmapped_names:
        print(
            f"WARNING: {len(unmapped_names)} SKOS entities had no matching entry in "
            f"{APPENDIX_A_FILE} (no code added): {sorted(unmapped_names)}"
        )

    print(f"[codes] {len(used_codes)} distinct equipment codes used (including NoEquipmentCodeSpecified).")

    if no_code_names:
        print(
            f"\n*** {len(no_code_names)} entities mapped to NoEquipmentCodeSpecified — "
            "PLEASE REVIEW: ***"
        )
        for n in sorted(no_code_names):
            print(f"    - {n}")

    collection_block = build_equipment_code_collection(used_codes)
    final_content = new_skos_content.rstrip() + "\n\n" + collection_block

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"\nOutput written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()