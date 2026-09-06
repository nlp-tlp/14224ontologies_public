import re

INPUT_FILE = "iso14224_skos_ApA.ttl"
OUTPUT_FILE = "iso14224_skos_ApA_rebuilt.ttl"

HEADER_RE = re.compile(r"### https://iso14224\.org/skos/(\w+)")
CODES_SECTION_MARKER = "#    Equipment codes"

# Tolerant field extractors — work regardless of surrounding whitespace/newlines,
# and stop capturing at whitespace, ';', '.', or '#' (to avoid swallowing
# corruption artifacts like a stray "###" glued onto the value).
PREFLABEL_RE = re.compile(r'skos:prefLabel\s+"([^"]*)"@en')
MAPSTOTERM_RE = re.compile(r'i14224skos:mapsToTerm\s+i14224skos:([^\s;.#]+)')
LEVELNUM_RE = re.compile(r'i14224skos:taxonomicLevelNumber\s+"([^"]+)"')
CLASSLEVEL_RE = re.compile(r'i14224skos:taxonomicClassificationLevel\s+i14224skos:([^\s;.#]+)')
HASCODE_RE = re.compile(r'i14224skos:hasEquipmentCode\s+i14224skos:([^\s;.#]+)')
HASCATEGORY_RE = re.compile(r'i14224skos:hasEquipmentCategory\s+i14224skos:([^\s;.#]+)')


def rebuild_block(name, body):
    """Rebuild one concept block from extracted fields, in canonical order."""
    pref_label = PREFLABEL_RE.search(body)
    maps_to = MAPSTOTERM_RE.search(body)
    level_num = LEVELNUM_RE.search(body)
    class_level = CLASSLEVEL_RE.search(body)
    has_code = HASCODE_RE.search(body)
    has_category = HASCATEGORY_RE.search(body)

    missing = []
    if not pref_label:
        missing.append("prefLabel")
    if not maps_to:
        missing.append("mapsToTerm")
    if not level_num:
        missing.append("taxonomicLevelNumber")
    if not class_level:
        missing.append("taxonomicClassificationLevel")
    if not has_code:
        missing.append("hasEquipmentCode")

    if missing:
        print(f"[WARN] {name}: missing field(s) {missing} — leaving original text unmodified.")
        return None

    lines = [
        f"### https://iso14224.org/skos/{name}",
        f"i14224skos:{name}",
        "    a skos:Concept ;",
        f'    skos:prefLabel "{pref_label.group(1)}"@en ;',
        f"    i14224skos:mapsToTerm i14224skos:{maps_to.group(1)} ;",
        f'    i14224skos:taxonomicLevelNumber "{level_num.group(1)}" ;',
        f"    i14224skos:taxonomicClassificationLevel i14224skos:{class_level.group(1)} ;",
    ]

    if has_category:
        lines.append(f"    i14224skos:hasEquipmentCode i14224skos:{has_code.group(1)} ;")
        lines.append(f"    i14224skos:hasEquipmentCategory i14224skos:{has_category.group(1)} .")
    else:
        lines.append(f"    i14224skos:hasEquipmentCode i14224skos:{has_code.group(1)} .")

    return "\n".join(lines) + "\n"


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    codes_idx = content.find(CODES_SECTION_MARKER)
    if codes_idx == -1:
        print("[WARN] Could not find Equipment codes section marker; processing entire file.")
        body_content = content
        footer = ""
        codes_search_start = len(content)
    else:
        # Back up to the start of the '###...' separator line preceding the marker
        sep_start = content.rfind("#################", 0, codes_idx)
        codes_search_start = sep_start if sep_start != -1 else codes_idx
        body_content = content[:codes_search_start]
        footer = content[codes_search_start:]

    header_matches = list(HEADER_RE.finditer(body_content))
    print(f"[info] Found {len(header_matches)} '### .../skos/Name' headers to process.")

    if not header_matches:
        print("[ERROR] No headers found — aborting.")
        return

    preamble = body_content[: header_matches[0].start()]

    rebuilt_blocks = []
    n_rebuilt = 0
    n_failed = 0

    for i, m in enumerate(header_matches):
        name = m.group(1)
        block_start = m.start()
        block_end = header_matches[i + 1].start() if i + 1 < len(header_matches) else len(body_content)
        block_text = body_content[block_start:block_end]

        new_block = rebuild_block(name, block_text)
        if new_block is not None:
            rebuilt_blocks.append(new_block)
            n_rebuilt += 1
        else:
            # Fall back to original text (already includes its own header)
            rebuilt_blocks.append(block_text.rstrip("\n") + "\n")
            n_failed += 1

    print(f"[result] Successfully rebuilt {n_rebuilt} blocks; {n_failed} left unmodified (see warnings above).")

    final_content = preamble + "\n".join(rebuilt_blocks) + "\n" + footer

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"\nOutput written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()