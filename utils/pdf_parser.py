import re
from collections import Counter

def parsetext_tagged(lines, character_names):
    dialogue = []
    current_character = None
    current_lines = []
    meta = {}

    for entry in lines:
        stripped = entry["text"]
        if not stripped:
            continue

        # Match "CHARACTER:"
        match = re.match(r"^([A-Z][A-Z\s\(\)']+):(.*)", stripped)
        if match:
            raw = match.group(1).strip()
            after_colon = match.group(2).strip()  # this captures the dialogue after the colon
            clean = re.sub(r"[\(\)\s'\d]", "", raw)

            if clean in character_names:
                if current_character and current_lines:
                    dialogue.append({
                        "character": current_character,
                        "line": " ".join(current_lines),
                        "page": meta["page"],
                        "column": meta["column"]
                    })

                current_character = clean
                current_lines = [after_colon] if after_colon else []
                meta = {"page": entry["page"], "column": entry["column"]}
            continue


        # Match "CHARACTER" on its own line
        if stripped in character_names:
            if current_character and current_lines:
                dialogue.append({
                    "character": current_character,
                    "line": " ".join(current_lines),
                    "page": meta["page"],
                    "column": meta["column"]
                })
            current_character = stripped
            current_lines = []
            meta = {"page": entry["page"], "column": entry["column"]}
            continue

        if current_character:
            current_lines.append(stripped)

    if current_character and current_lines:
        dialogue.append({
            "character": current_character,
            "line": " ".join(current_lines),
            "page": meta["page"],
            "column": meta["column"]
        })

    return dialogue





def extract_character_names(pdf):

    name_counter = Counter()

    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue
        lines = text.split("\n")
        for line in lines:
            stripped = line.strip()

            # Pattern 1: HARMOND:
            match_colon = re.match(r"^([A-Z][A-Z\s\(\)'\d]+):", stripped)
            if match_colon:
                raw = match_colon.group(1)
                clean = re.sub(r"[\(\)\d'\s]", "", raw)
                name_counter[clean] += 1
                continue

            # Pattern 2: Standalone all-caps line (e.g. HARMOND)
            if stripped.isupper() and len(stripped.split()) <= 2 and len(stripped) > 2:
                name_counter[stripped] += 1

    return [name for name, count in name_counter.items() if count > 2]


      
        