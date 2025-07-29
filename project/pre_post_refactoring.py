import csv
import re
import sys
import os

# === Leggi argomenti ===
if len(sys.argv) != 3:
    print("Uso: python3 confronta_consumo_cpu.py <tag_old> <tag_new>")
    sys.exit(1)

tag_old, tag_new = sys.argv[1], sys.argv[2]
file_pre = os.path.join("grafici", f"risultati_{tag_old}_refactoring.txt")
file_post = os.path.join("grafici", f"risultati_{tag_new}_refactoring.txt")
output_csv = "confronto_consumo_cpu.csv"

# === Salta se il file CSV esiste già ===
if os.path.exists(output_csv):
    print(f"✅ Output già presente: {output_csv}")
    sys.exit(0)

# === Estrai energia CPU totale da un file ===
def estrai_energia_cpu(file_path):
    energia_totale = 0.0
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(r'(\d+,\d+)\s+Joules power/energy-pkg/', line)
            if match:
                valore = float(match.group(1).replace(',', '.'))
                energia_totale += valore
    return energia_totale

# === Verifica esistenza file input ===
if not os.path.exists(file_pre) or not os.path.exists(file_post):
    print(f"❌ File non trovato: {file_pre} o {file_post}")
    sys.exit(1)

# === Calcolo ===
energia_pre = estrai_energia_cpu(file_pre)
energia_post = estrai_energia_cpu(file_post)
differenza = energia_post - energia_pre
percentuale = (differenza / energia_pre) * 100 if energia_pre != 0 else 0.0

# === Scrivi il CSV ===
with open(output_csv, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Release Pre", "Release Post", "Energia Pre (J)", "Energia Post (J)", "Differenza (J)", "Differenza (%)"])
    writer.writerow([tag_old, tag_new, f"{energia_pre:.2f}", f"{energia_post:.2f}", f"{differenza:.2f}", f"{percentuale:.2f}"])

print(f"✅ CSV creato: {output_csv}")
