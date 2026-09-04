import re

INPUT_FILE = "iso14224_skos_ApA_with_codes_and_categories.ttl"
OUTPUT_FILE = "iso14224_skos_ApA_with_codes_and_categories_sorted.ttl"

# Order in which equipment categories should be sorted
CATEGORY_ORDER = [
    "RotatingEquipment",
    "MechanicalEquipment",
    "ElectricalEquipment",
    "SafetyAndControlEquipment",
    "SubseaEquipment",
    "WellCompletionEquipment",
    "DrillingEquipment",
    "WellInterventionEquipment",
    "MarineEquipment",
    "UtilitiesEquipment",
    "AuxiliariesEquipment",
]
CATEGORY_RANK = {cat: i for i, cat in enumerate(CATEGORY_ORDER)}

# Matches one Level 6 block, e.g.:
# ### https://iso14224.org/skos/CombustionEngine
# i14224skos:CombustionEngine
#     a skos:Concept ;
#     ...
#     i14224skos:taxonomicLevelNumber "Level 6" ;
#     ...
#     i14224skos:hasEquipmentCategory i14224skos:RotatingEquipment .
LEVEL6_BLOCK_RE = re.compile(
    r"### https://iso14224\.org/skos/(\w+)\s*\n"
    r"i14224skos:\w+\s*\n"
    r"(?:.*?\n)*?"
    r"\s*i14224skos:taxonomicLevelNumber\s+\"Level 6\"\s*;\s*\n"
    r"(?:.*?\n)*?"
    r"\s*i14224skos:hasEquipmentCategory\s+i14224skos:(\w+)\s*\.\s*\n?",
    re.MULTILINE,
)

# Marks the start/end of the Level 6 section so we only touch that part of the file.
SECTION_HEADER_RE = re.compile(
    r"(#################################################################\n"
    r"#\s*Equipment units - Level 6\n"
    r"#################################################################\n)"
)
NEXT_SECTION_RE = re.compile(
    r"(#################################################################\n"
    r"#\s*Equipment types - Level 7)"
)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    header_match = SECTION_HEADER_RE.search(content)
    next_match = NEXT_SECTION_RE.search(content)

    if not header_match or not next_match:
        print("ERROR: Could not locate Level 6 section boundaries.")
        return

    section_start = header_match.end()
    section_end = next_match.start()

    level6_section = content[section_start:section_end]

    blocks = []
    unmatched_text_positions = []

    last_end = 0
    for m in LEVEL6_BLOCK_RE.finditer(level6_section):
        if m.start() != last_end:
            # capture any stray text between blocks (shouldn't normally happen)
            unmatched_text_positions.append(level6_section[last_end:m.start()])
        name = m.group(1)
        category = m.group(2)
        block_text = m.group(0)
        blocks.append((name, category, block_text))
        last_end = m.end()

    trailing_text = level6_section[last_end:]

    print(f"[parse] Found {len(blocks)} Level 6 blocks.")

    unknown_categories = sorted({cat for _, cat, _ in blocks if cat not in CATEGORY_RANK})
    if unknown_categories:
        print(f"WARNING: Unrecognized categories (will sort last): {unknown_categories}")

    def sort_key(item):
        name, category, _ = item
        rank = CATEGORY_RANK.get(category, len(CATEGORY_ORDER))
        return (rank, name.lower())

    blocks.sort(key=sort_key)

    sorted_section = "".join(block_text for _, _, block_text in blocks)
    # Preserve any trailing content (e.g., blank line before next section)
    new_level6_section = sorted_section + trailing_text

    new_content = (
        content[:section_start] + new_level6_section + content[section_end:]
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()