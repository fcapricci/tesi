import json
import csv

# === INPUT ===
refactoring_file = 'filtered_refactorings.json'
tests_file = 'tests_involved.txt'

# === OUTPUT ===
summary_csv = 'refactoring_quantificati.csv'
mapping_csv = 'refactoring_test_mapping.csv'

# === Carica lista test coinvolti ===
with open(tests_file, 'r') as f:
    test_classes = {line.strip() for line in f if line.strip()}

# === Carica refactoring ===
with open(refactoring_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1️⃣ Quantifica refactoring per tipo
quantita = {}
# 2️⃣ Mapping: test_class → [list of refactoring types touching metodi coperti]
mapping = {}

for commit in data.get('commits', []):
    for ref in commit.get('refactorings', []):
        tipo = ref.get('type', 'N/D')
        quantita[tipo] = quantita.get(tipo, 0) + 1

        for loc in ref.get('rightSideLocations', []):
            class_path = loc.get('filePath', '')
            class_name = class_path.replace('/', '.').replace('.java', '')

            for test in test_classes:
                if class_name.split('.')[-1] in test:  # usa solo nome semplice (es. DijkstraShortestPath)
                    mapping.setdefault(test, []).append(tipo)

# === Scrivi quantificazione ===
with open(summary_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Tipo Refactoring', 'Occorrenze'])
    for tipo, count in quantita.items():
        writer.writerow([tipo, count])

# === Scrivi mapping ===
with open(mapping_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['TestClass', 'Tipi di Refactoring associati'])
    for test, tipi in mapping.items():
        writer.writerow([test, ';'.join(sorted(set(tipi)))])

print(f"✅ Creati:\n • {summary_csv}\n • {mapping_csv}")
