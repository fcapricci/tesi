import os
import xml.etree.ElementTree as ET
import csv

# === Percorsi ===
JACOCO_DIR = "jacoco_reports"  # Cartella con i report .xml
REFACTORED_METHODS = "refactored_methods.txt"
REFACTORINGS_JSON = "filtered_refactorings.json"
OUTPUT_CSV = "mapping_metodo_refactoring_test.csv"

# === STEP 1: carica metodi refactorati (formato completo class.method)
refactored_methods = set()
with open(REFACTORED_METHODS) as f:
    for line in f:
        method = line.strip()
        if method:
            refactored_methods.add(method)

# === STEP 2: crea mappa metodo -> tipo di refactoring
refactoring_map = {}  # class.method -> tipo
with open(REFACTORINGS_JSON) as f:
    for line in f:
        line = line.strip().strip('",')
        if "::" in line and "#" in line:
            left, tipo = line.rsplit("#", 1)
            class_name, method_name = left.split("::")
            full = f"{class_name}.{method_name}"
            refactoring_map[full] = tipo

# === STEP 3: scorri tutti i file JaCoCo
mappatura = []

for root_dir, _, files in os.walk(JACOCO_DIR):
    for file in files:
        if not file.endswith(".xml"):
            continue

        test_class = file.replace("jacoco_", "").replace(".xml", "").replace("_", ".")
        path = os.path.join(root_dir, file)

        try:
            root = ET.parse(path).getroot()
        except Exception:
            continue

        for package in root.findall(".//package"):
            for cls in package.findall("class"):
                class_name = cls.get("name").replace("/", ".")
                for method in cls.findall("method"):
                    method_name = method.get("name")
                    full = f"{class_name}.{method_name}"

                    if full in refactored_methods:
                        refactoring = refactoring_map.get(full, "UNKNOWN")
                        mappatura.append([full, refactoring, test_class])

# === STEP 4: salva CSV
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["MetodoRefactorato", "Refactoring", "ClasseDiTest"])
    writer.writerows(mappatura)

print(f"✅ Mappatura creata: {OUTPUT_CSV} ({len(mappatura)} righe)")
