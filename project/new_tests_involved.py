import os
import xml.etree.ElementTree as ET

# === CONFIG ===
JACOCO_DIR = "jacoco_reports"  # directory contenente i file jacoco_*.xml
REFACTORED_METHODS_FILE = "refactored_methods.txt"
OUTPUT = "tests_involved_methods.txt"

# === Carica metodi refactorati ===
with open(REFACTORED_METHODS_FILE) as f:
    refactored = set(tuple(line.strip().rsplit(".", 1)) for line in f if line.strip())

result = set()

for file in os.listdir(JACOCO_DIR):
    if not file.endswith(".xml"):
        continue

    # es: jacoco_org_jgrapht_graph_MyTest.xml → org.jgrapht.graph.MyTest
    test_class = file.replace("jacoco_", "").replace(".xml", "").replace("_", ".")

    path = os.path.join(JACOCO_DIR, file)

    try:
        root = ET.parse(path).getroot()
    except Exception:
        continue

    # Crea lista dei metodi di test presenti nel report
    test_methods = []
    for method in root.findall(".//method"):
        name = method.get("name")
        if name and not name.startswith("lambda$") and name != "<init>":
            test_methods.append(name)

    # Cerca se questo report copre un metodo refactorato
    matched = False
    for package in root.findall(".//package"):
        for cls in package.findall("class"):
            class_name = cls.get("name").replace("/", ".")
            for method in cls.findall("method"):
                method_name = method.get("name")
                if (class_name, method_name) in refactored:
                    matched = True
                    break
            if matched:
                break
        if matched:
            break

    if matched:
        for method in test_methods:
            result.add(f"{test_class}#{method}")

# === Scrivi risultato ===
with open(OUTPUT, "w") as f:
    for r in sorted(result):
        f.write(r + "\n")

print(f"✅ Generato '{OUTPUT}' con {len(result)} metodi di test che coprono metodi refactorati.")
