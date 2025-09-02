import json

# === Input/Output ===
INPUT_JSON = "estratti_extract_and_move_method.json"
OUTPUT_TXT = "refactored_methods_extractAndMoveMethod.txt"

# === Estrai metodi refactorati nel formato compatibile con JaCoCo ===
metodi = set()

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

for commit in data.get("commits", []):
    for refactoring in commit.get("refactorings", []):
        if refactoring.get("type") != "Extract Method":
            continue

        for location in refactoring.get("rightSideLocations", []):
            file_path = location.get("filePath", "").replace("/", ".").replace(".java", "")
            code_element = location.get("codeElement")

            if not code_element:
                continue  # salta se manca il nome del metodo

            method_name = code_element.split("(")[0].strip().split()[-1]
            full_method = f"{file_path}.{method_name}"
            metodi.add(full_method)

# === Scrittura file di output ===
with open(OUTPUT_TXT, "w") as f:
    for m in sorted(metodi):
        f.write(m + "\n")

print(f"✅ File generato: {OUTPUT_TXT} ({len(metodi)} metodi validi)")
