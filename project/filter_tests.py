import os
import xml.etree.ElementTree as ET

# === CONFIG ===
JACOCO_REPORTS_DIR = "jacoco_reports"  # cartella con file jacoco_*.xml
REFACTORED_METHODS_FILE = "refactored_methods.txt"
OUTPUT_TESTS_FILE = "tests_involved.txt"

# === Carica metodi refactorati (classe.metodo)
with open(REFACTORED_METHODS_FILE, "r") as f:
    methods = set(tuple(line.strip().rsplit(".", 1)) for line in f if line.strip())

involved_tests = set()

for filename in os.listdir(JACOCO_REPORTS_DIR):
    if not filename.endswith(".xml"):
        continue

    filepath = os.path.join(JACOCO_REPORTS_DIR, filename)
    test_class = filename.replace("jacoco_", "").replace(".xml", "").replace("_", ".")

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        print(f"⚠️ Errore parsing {filename}: {e}")
        continue

    for package in root.findall(".//package"):
        pkg = package.get("name").replace("/", ".")
        for cls in package.findall("class"):
            cls_name = cls.get("name").replace("/", ".")
            full_class = f"{pkg}.{cls_name}"
            for method in cls.findall("method"):
                method_name = method.get("name")
                if (full_class, method_name) in methods:
                    involved_tests.add(test_class)
                    break  # una corrispondenza basta per includere il test

# === Salva risultato ===
with open(OUTPUT_TESTS_FILE, "w") as f:
    for t in sorted(involved_tests):
        f.write(t + "\n")

print(f"✅ Trovati {len(involved_tests)} test coinvolti. Salvati in {OUTPUT_TESTS_FILE}")
