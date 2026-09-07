import re

INPUT_FILE = "iso14224_skos_ApA.ttl"
OUTPUT_FILE = "iso14224_skos_ApA_fixed.ttl"

# Fixes corrupted block endings like:
#   ...
#   i14224skos:taxonomicClassificationLevel i14224skos:EquipmentUnit ;
# HydrocycloneVessel    i14224skos:hasEquipmentCode i14224skos:HY ### https://iso14224.org/skos/SlugCatcherVessel
#
# into:
#   ...
#   i14224skos:taxonomicClassificationLevel i14224skos:EquipmentUnit ;
#   i14224skos:hasEquipmentCode i14224skos:HY .
#
# ### https://iso14224.org/skos/SlugCatcherVessel
CORRUPT_RE = re.compile(
    r'\n(?P<dupname>\w+)[ \t]+i14224skos:hasEquipmentCode[ \t]+i14224skos:(?P<code>[^\s;]+)'
    r'[ \t]*;?'
    r'(?P<catpart>[ \t]*\n[ \t]*i14224skos:hasEquipmentCategory[ \t]+i14224skos:(?P<cat>[^\s.]+))?'
    r'[ \t]*(?=(###|\Z))'
)


def fix_corruption(content):
    count = 0

    def repl(m):
        nonlocal count
        count += 1
        code = m.group("code")
        cat = m.group("cat")
        if cat:
            return (
                f"\n    i14224skos:hasEquipmentCode i14224skos:{code} ;\n"
                f"    i14224skos:hasEquipmentCategory i14224skos:{cat} .\n\n"
            )
        else:
            return f"\n    i14224skos:hasEquipmentCode i14224skos:{code} .\n\n"

    new_content = CORRUPT_RE.sub(repl, content)
    return new_content, count


HEADER_RE = re.compile(r'^### https://iso14224\.org/skos/')


def ensure_blank_before_headers(text):
    lines = text.split("\n")
    out = []
    added = 0
    for line in lines:
        if HEADER_RE.match(line) and out and out[-1].strip() != "":
            out.append("")
            added += 1
        out.append(line)
    return "\n".join(out), added


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    fixed_content, n_corrupt = fix_corruption(content)
    print(f"[fix] Repaired {n_corrupt} corrupted block ending(s).")

    final_content, n_blank = ensure_blank_before_headers(fixed_content)
    print(f"[fix] Inserted {n_blank} missing blank line(s) before block headers.")

    # Sanity check: count headers vs. count of proper block terminators
    total_headers = len(re.findall(r"### https://iso14224\.org/skos/\w+", final_content))
    print(f"[check] Total '### .../skos/...' headers: {total_headers}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"\nOutput written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()