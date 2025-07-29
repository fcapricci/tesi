import csv
import re

# === Percorsi dei file ===
file_pre = "/home/federico/JGraphT_Test/project/grafici/risultati_1.4.0_refactoring.txt"
file_post = "/home/federico/JGraphT_Test/project/grafici/risultati_jgrapht-1.3.0_refactoring.txt"
output_csv = "confronto_consumo_cpu.csv"

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

# === Calcolo ===
energia_pre = estrai_energia_cpu(file_pre)
energia_post = estrai_energia_cpu(file_post)
differenza = energia_post - energia_pre
percentuale = (differenza / energia_pre) * 100

# === Scrivi il CSV ===
with open(output_csv, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Release Pre", "Release Post", "Energia Pre (J)", "Energia Post (J)", "Differenza (J)", "Differenza (%)"])
    writer.writerow(["1.3.0", "1.4.0", f"{energia_pre:.2f}", f"{energia_post:.2f}", f"{differenza:.2f}", f"{percentuale:.2f}"])

print(f"✅ CSV creato: {output_csv}")
