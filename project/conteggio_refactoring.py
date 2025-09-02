import json
import csv
import os

# === INPUT ===
refactoring_file = 'filtered_refactorings.json'

# === OUTPUT ===
summary_csv = 'refactoring_quantificati.csv'


if os.path.exists(summary_csv):
    print(f"✅ Output già presente: {summary_csv}")
    exit(0)

# === Carica refactoring ===
with open(refactoring_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# === Quantifica refactoring per tipo ===
quantita = {}
for commit in data.get('commits', []):
    for ref in commit.get('refactorings', []):
        tipo = ref.get('type', 'N/D')
        quantita[tipo] = quantita.get(tipo, 0) + 1

# === Scrivi file CSV con il conteggio ===
with open(summary_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Tipo Refactoring', 'Occorrenze'])
    for tipo, count in sorted(quantita.items()):
        writer.writerow([tipo, count])

print(f"✅ Creato file: {summary_csv}")
