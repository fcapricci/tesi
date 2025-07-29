import pandas as pd
import os
import xml.etree.ElementTree as ET
from collections import defaultdict

# === Percorsi file ===
JACOCO_DIR = "jacoco_reports"
REFACTORED_METHODS = "refactored_methods.txt"
REFACTORING_CSV = "metodo_refactoring.csv"
OUTPUT_TESTS = "test_involved.txt"
OUTPUT_TABLE = "tabella_metodo_refactoring_test.csv"

# === Skip se output già presente ===
if os.path.exists(OUTPUT_TESTS):
    print(f"✅ {OUTPUT_TESTS} già presente, skip generazione.")
    exit(0)

# === Carica metodi refactorati e deduci le classi ===
refactored_classes = set()
with open(REFACTORED_METHODS) as f:
    for line in f:
        method = line.strip()
        if method:
            class_name = ".".join(method.split(".")[:-1])
            refactored_classes.add(class_name)

# === Estrai coperture JaCoCo: RefactoredClass -> TestClass ===
coverage_map = defaultdict(set)

for root, _, files in os.walk(JACOCO_DIR):
    for file in files:
        if file.endswith(".xml"):
            path = os.path.join(root, file)
            try:
                tree = ET.parse(path)
                root_element = tree.getroot()
                for class_elem in root_element.findall(".//class"):
                    raw_name = class_elem.get("name")
                    if raw_name:
                        covered_class = raw_name.replace("/", ".")
                        for ref_class in refactored_classes:
                            if covered_class.startswith(ref_class):
                                test_class = os.path.basename(file).replace(".xml", "")
                                coverage_map[ref_class].add(test_class)
            except ET.ParseError:
                continue

# === Converti in DataFrame RefactoredClass -> TestClass ===
df_coverage = pd.DataFrame([
    (ref_class, test_class)
    for ref_class, test_classes in coverage_map.items()
    for test_class in test_classes
], columns=["RefactoredClass", "TestClass"])

# === Carica metodo_refactoring.csv ===
df_metodo = pd.read_csv(REFACTORING_CSV)
df_metodo["ClasseClean"] = df_metodo["Classe"].str.replace(r"^.*?org", "org", regex=True)

# === Merge per aggiungere TestClass alle righe del CSV ===
df_merged = pd.merge(
    df_metodo,
    df_coverage,
    left_on="ClasseClean",
    right_on="RefactoredClass",
    how="left"
)

# === Compatta per (Metodo, Refactoring, Classe) ===
df_final = df_merged.groupby(
    ["Metodo", "Refactoring", "Classe"]
)["TestClass"].apply(lambda x: ", ".join(sorted(set(x.dropna())))).reset_index()

# === Salva TestClass uniche in un file .txt ===
unique_tests = sorted(set(df_merged["TestClass"].dropna()))
with open(OUTPUT_TESTS, "w") as f:
    for test in unique_tests:
        f.write(test + "\n")

# === Salva tabella compatta in CSV (opzionale) ===
df_final.to_csv(OUTPUT_TABLE, index=False)

print(f"✅ Generati {len(unique_tests)} test coinvolti in {OUTPUT_TESTS}")
