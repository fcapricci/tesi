import os
import xml.etree.ElementTree as ET
import csv

# === Percorsi ===
JACOCO_DIR = "jacoco_reports"
REFACTORED_METHODS_FILE = "refactored_methods_addParameter.txt"
OUTPUT_CSV = "testclass_to_refactored_methods_addParameter.csv"
OUTPUT_TEST_CLASSES = "test_classes_involved_addParameter.txt"

# === Carica metodi refactorati e normalizza ===
refactored_methods = set()
with open(REFACTORED_METHODS_FILE) as f:
    for line in f:
        method = line.strip()

        # Rimuovi il prefisso jgrapht-core.src.main.
        for prefix in ["jgrapht-core.src.main.", "src.main."]:
            if method.startswith(prefix):
                method = method.replace(prefix, "")

        # Se è un costruttore tipo ClassName.ClassName → converti in ClassName.<init>
        parts = method.split(".")
        if len(parts) >= 2 and parts[-1] == parts[-2]:
            parts[-1] = "<init>"
            method = ".".join(parts)

        # Se finisce con .this → è un costruttore
        if method.endswith(".this"):
            parts = method.split(".")
            parts[-1] = "<init>"
            method = ".".join(parts)

        refactored_methods.add(method)

# === Mappa: test_class → metodi refactorati coperti ===
coverage_map = {}

# === Parsing JaCoCo ===
for filename in os.listdir(JACOCO_DIR):
    if not filename.endswith(".xml"):
        continue

    filepath = os.path.join(JACOCO_DIR, filename)
    test_class = filename.replace(".xml", "")

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError:
        print(f"❌ Errore nel parsing: {filepath}")
        continue

    for clazz in root.findall(".//class"):
        class_name = clazz.get("name", "").replace("/", ".")  # questo ha già il package
        simple_class_name = class_name.split(".")[-1]

        for method in clazz.findall("method"):
            method_name = method.get("name", "")
            if method_name == "<init>":
                full_method = f"{class_name}.<init>"
            else:
                full_method = f"{class_name}.{method_name}"

            if full_method in refactored_methods:
                if test_class not in coverage_map:
                    coverage_map[test_class] = set()
                coverage_map[test_class].add(full_method)

# === Scrittura CSV con mapping completo ===
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["TestClass", "RefactoredMethod"])
    for test_class, methods in coverage_map.items():
        for method in methods:
            writer.writerow([test_class, method])

# === Scrittura TXT con classi di test uniche ===
with open(OUTPUT_TEST_CLASSES, "w") as f:
    for test_class in sorted(coverage_map.keys()):
        f.write(test_class + "\n")

print(f"✅ CSV salvato in: {OUTPUT_CSV}")
print(f"✅ Lista classi di test salvata in: {OUTPUT_TEST_CLASSES}")
