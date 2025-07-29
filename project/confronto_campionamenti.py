import re
import os
import matplotlib.pyplot as plt
import numpy as np
import sys

if len(sys.argv) != 3:
    print("Uso: python confronto_campionamenti.py <file_release1> <file_release2>")
    sys.exit(1)

file_r1 = sys.argv[1]
file_r2 = sys.argv[2]

threshold = 0.7  # Δ Joule per considerare un picco
output_dir = 'grafici'
os.makedirs(output_dir, exist_ok=True)

# Nome file output dinamico
nome_output = os.path.join(
    output_dir,
    f'differenza_campionamenti_{os.path.basename(file_r1)}_vs_{os.path.basename(file_r2)}.png'
)

# Se il grafico esiste, non rigenerarlo
if os.path.exists(nome_output):
    print(f"✅ Grafico già presente: {nome_output}.")
    sys.exit(0)

def estrai_energie_per_esecuzioni(filepath):
    esecuzioni = []
    energia_corrente = []
    dentro_esecuzione = False
    with open(filepath, 'r') as f:
        for line in f:
            if "===== ESECUZIONE" in line:
                if energia_corrente:
                    esecuzioni.append(energia_corrente)
                    energia_corrente = []
                dentro_esecuzione = True
            elif dentro_esecuzione:
                match = re.search(r'^\s*\d+\.\d+\s+([\d,]+)\s+Joules', line)
                if match:
                    joule = float(match.group(1).replace(',', '.'))
                    energia_corrente.append(joule)
        if energia_corrente:
            esecuzioni.append(energia_corrente)
    return esecuzioni

def calcola_media_allineata(esecuzioni):
    min_len = min(len(e) for e in esecuzioni)
    trimmed = [e[:min_len] for e in esecuzioni]
    return np.mean(trimmed, axis=0)

esecuzioni_r1 = estrai_energie_per_esecuzioni(file_r1)
esecuzioni_r2 = estrai_energie_per_esecuzioni(file_r2)

media_r1 = calcola_media_allineata(esecuzioni_r1)
media_r2 = calcola_media_allineata(esecuzioni_r2)

min_len = min(len(media_r1), len(media_r2))
differenze = [media_r2[i] - media_r1[i] for i in range(min_len)]
picchi = [(i, d) for i, d in enumerate(differenze) if abs(d) > threshold]


plt.figure(figsize=(12, 6))
plt.plot(range(min_len), media_r1[:min_len], label='Media Release 1')
plt.plot(range(min_len), media_r2[:min_len], label='Media Release 2')
for i, d in picchi:
    plt.axvline(i, color='red', linestyle='--', alpha=0.5)
plt.title("Confronto Energia Media per Campione (CPU)")
plt.xlabel("Campione (100ms ciascuno)")
plt.ylabel("Energia media (Joule)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(nome_output)
print(f"Grafico salvato in: {nome_output} ✅")
