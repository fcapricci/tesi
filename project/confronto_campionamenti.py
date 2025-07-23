import re
import os
import matplotlib.pyplot as plt
import numpy as np

# === CONFIGURAZIONE ===
file_r1 = 'risultati_release1.txt'
file_r2 = 'risultati_release2.txt'
threshold = 1  # Δ Joule per considerare un picco
output_dir = 'grafici'
os.makedirs(output_dir, exist_ok=True)

# === FUNZIONI ===

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

# === ESTRAZIONE ===

esecuzioni_r1 = estrai_energie_per_esecuzioni(file_r1)
esecuzioni_r2 = estrai_energie_per_esecuzioni(file_r2)

media_r1 = calcola_media_allineata(esecuzioni_r1)
media_r2 = calcola_media_allineata(esecuzioni_r2)

min_len = min(len(media_r1), len(media_r2))
differenze = [media_r2[i] - media_r1[i] for i in range(min_len)]
picchi = [(i, d) for i, d in enumerate(differenze) if abs(d) > threshold]

# === RISULTATI ===
print(f"Esecuzioni trovate - Release 1: {len(esecuzioni_r1)}, Release 2: {len(esecuzioni_r2)}")
print(f"Campioni medi analizzati: {min_len}")
print(f"Picchi rilevati (Δ > {threshold} Joule):")
for i, d in picchi:
    print(f" - Campione {i}: Δ = {d:.2f} J {'↑' if d > 0 else '↓'}")

# === GRAFICO ===
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
plt.savefig(os.path.join(output_dir, 'differenza_campionamenti_base.png'))
print("Grafico salvato in: grafici/differenza_campionamenti.png ✅")
