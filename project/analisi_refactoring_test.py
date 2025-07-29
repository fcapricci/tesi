import os
import xml.etree.ElementTree as ET

# === CONFIG ===
JACOCO_DIR = "jacoco_reports"  # cartella con jacoco_<test>.xml
METHODS_FILE = "refactored_methods.txt"
OUTPUT = "tests_involved.txt"

# === Carica metodi refactorati ===
with open(METHODS_FILE) as f:
    methods = set(tuple(line.strip().rsplit(".", 1)) for line in f if line.strip())

involved = set()

for file in os.listdir(JACOCO_DIR):
    if not file.endswith(".xml"):
        continue

    path = os.path.join(JACOCO_DIR, file)
    test_class = file.replace("jacoco_", "").replace(".xml", "").replace("_", ".")

    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception:
        continue

    for package in root.findall(".//package"):
        pkg = package.get("name").replace("/", ".")
        for cls in package.findall("class"):
            class_name = cls.get("name").replace("/", ".")
            full_class = class_name
            for method in cls.findall("method"):
                method_name = method.get("name")
                if (full_class, method_name) in methods:
                    involved.add(test_class)
                    break  # basta una corrispondenza

# === Scrivi il file ===
with open(OUTPUT, "w") as f:
    for t in sorted(involved):
        f.write(t + "\n")

print(f"✅ Salvati {len(involved)} test in {OUTPUT}")
