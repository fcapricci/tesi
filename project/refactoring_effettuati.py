import json
import csv
import os

# === CONFIGURAZIONE ===
json_path = "/home/federico/JGraphT_Test/project/estratti_extract_and_move_method.json"
csv_output = "metodo_refactoring_extractAndMoveMethod.csv"

# === SALTA SE OUTPUT GIÀ ESISTE ===
if os.path.exists(csv_output):
    print(f"✅ Output già presente: {csv_output}")
    exit(0)

# === LETTURA JSON ===
with open(json_path, "r") as f:
    data = json.load(f)

# === ESTRAZIONE E SCRITTURA CSV ===
with open(csv_output, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Metodo", "Refactoring", "Classe"])

    for commit in data.get("commits", []):
        for ref in commit.get("refactorings", []):
            ref_type = ref.get("type", "N/A")
            for loc in ref.get("leftSideLocations", []):
                if loc.get("codeElementType") == "METHOD_DECLARATION":
                    method = loc.get("codeElement", "N/A")
                    class_path = loc.get("filePath", "")
                    class_name = class_path.replace("/", ".").replace(".java", "")
                    writer.writerow([method, ref_type, class_name])

print(f"✅ File CSV salvato come: {csv_output}")
