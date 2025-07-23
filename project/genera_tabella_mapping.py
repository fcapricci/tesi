import os
import xml.etree.ElementTree as ET
import json
import csv

# === CONFIG ===
JACOCO_DIR = "jacoco_reports"
REFACTORINGS_JSON = "filtered_refactorings.json"
TESTS_INVOLVED = "tests_involved.txt"
OUTPUT_CSV = "metodo_refactoring_test.csv"

# === 1. Carica classi di test coinvolte ===
with open(TESTS_INVOLVED, "r") as f:
    test_classes = set(line.strip() for line in f if line.strip())

# === 2. Estrai metodi refactorati ===
refactored_methods = dict()  # key: (class_name, method_name) -> set(refactoring_type)

def extract_class_from_path(path):
    return path.replace("jgrapht-core/src/main/java/", "").replace(".java", "").replace("/", ".")

with open(REFACTORINGS_JSON, "r") as f:
    data = json.load(f)
    for commit in data.get("commits", []):
        for ref in commit.get("refactorings", []):
            ref_type = ref.get("type")
            for location in ref.get("rightSideLocations", []):
                if location.get("codeElementType") != "METHOD_DECLARATION":
                    continue
                method_signature = location["codeElement"]
                method_name = method_signature.split()[1].split("(")[0]  # es: getMaximumFlowValue
                class_name = extract_class_from_path(location["filePath"])
                key = (class_name, method_name)
                refactored_methods.setdefault(key, set()).add(ref_type)

# === 3. Scansiona i report JaCoCo ===
result_rows = []

for test_class in test_classes:
    report_name = f"jacoco_{test_class.replace('.', '_')}.xml"
    report_path = os.path.join(JACOCO_DIR, report_name)
    if not os.path.exists(report_path):
        continue

    tree = ET.parse(report_path)
    root = tree.getroot()

    for package in root.findall(".//package"):
        package_name = package.get("name").replace("/", ".")
        for class_ in package.findall("class"):
            class_name = class_.get("name").replace("/", ".")
            full_class = f"{package_name}.{class_name}"
            for method in class_.findall("method"):
                method_name = method.get("name")
                key = (full_class, method_name)
                if key in refactored_methods:
                    for ref_type in refactored_methods[key]:
                        result_rows.append([f"{full_class}.{method_name}", ref_type, test_class])

# === 4. Scrivi il CSV ===
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Metodo", "Refactoring", "ClasseDiTest"])
    writer.writerows(result_rows)

print(f"✅ CSV generato: {OUTPUT_CSV} ({len(result_rows)} righe)")
