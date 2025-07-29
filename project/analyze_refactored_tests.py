import json
import os

# === CONFIG ===
REFACTORINGS_JSON = "filtered_refactorings.json"
OUTPUT_METHODS = "refactored_methods.txt"

# Se l'output esiste, non rigenerare
if os.path.exists(OUTPUT_METHODS):
    print(f"✅ Output già presente: {OUTPUT_METHODS}")
    exit(0)

def extract_class_from_path(path):
    return path.replace("jgrapht-core/src/main/java/", "").replace(".java", "").replace("/", ".")

# === Estrazione (Classe, Metodo) ===
methods_set = set()

with open(REFACTORINGS_JSON, "r") as f:
    data = json.load(f)
    for commit in data.get("commits", []):
        for ref in commit.get("refactorings", []):
            for location in ref.get("rightSideLocations", []):
                if location.get("codeElementType") != "METHOD_DECLARATION":
                    continue
                method_sig = location.get("codeElement", "")
                try:
                    method_name = method_sig.split()[1].split("(")[0]
                except IndexError:
                    continue
                class_name = extract_class_from_path(location["filePath"])
                methods_set.add(f"{class_name}.{method_name}")

# === Scrivi su file ===
with open(OUTPUT_METHODS, "w") as out:
    for line in sorted(methods_set):
        out.write(line + "\n")

print(f"✅ Generati {len(methods_set)} metodi in {OUTPUT_METHODS}")
