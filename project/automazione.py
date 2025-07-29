import os
import subprocess
import csv
import shutil

# === CONFIGURAZIONE ===
repo_path = '/home/federico/JGraphT_Test/project/repo'  # cartella della repository Git locale
releases = ['jgrapht-1.3.0','1.4.0','jgrapht-1.5.0']  # tag Git delle release da analizzare
energia_threshold = 0.02  # soglia in Joule per differenza media
campione_threshold = 0.3  # soglia in Joule per singolo campione
script_misura = './misura_consumo.sh'
refactoringminer_bin = './RefactoringMiner/bin/RefactoringMiner'  # path all'eseguibile CLI
script_misura2 = './misura_consumo2.sh'
script_misura3 = './misura_consumo3.sh'

# === FUNZIONI ===
def misura_release(tag):
    print(f"> Checkout {tag}...")
    subprocess.run(['git', '-C', repo_path, 'checkout', tag], stdout=subprocess.DEVNULL)
    print(f"> Misurazione consumi per {tag}...")
    subprocess.run([script_misura, tag, repo_path], check=True)

def carica_summary(csv_path):
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        energie = [float(row['Energia media CPU (J)']) for row in reader]

    return energie

def confronta_medie(file1, file2):
    e1 = carica_summary(file1)
    e2 = carica_summary(file2)
    delta = sum(e2) / len(e2) - sum(e1) / len(e1)
    return delta

def analizza_refactoring(tag_old, tag_new):
    out_json = f"refactoring_{tag_old}_to_{tag_new}.json"
    if os.path.exists(out_json):
        print(f" Refactoring già analizzato: {out_json}")
        return
    subprocess.run([
        refactoringminer_bin,
        "-bt", repo_path, tag_old, tag_new,
        "-json", out_json
    ])
    print(f"✅ Refactoring analizzati: {out_json}")

# === CICLO PRINCIPALE ===
for i in range(len(releases) - 1):
    tag1, tag2 = releases[i], releases[i + 1]
    print(f"\n🔍 Analisi da {tag1} → {tag2}")

    # Misurazione se non già presente
    for tag in [tag1, tag2]:
        summary_path = f"grafici/risultati_{tag}_summary.csv"
        if not os.path.exists(summary_path):
            misura_release(tag)

    # Confronto energia media
    file1 = f"grafici/risultati_{tag1}_summary.csv"
    file2 = f"grafici/risultati_{tag2}_summary.csv"
    delta = confronta_medie(file1, file2)
    print(f"⚡ Δ energia media: {delta:.2f} Joule")

    if abs(delta) >= energia_threshold:
        print("⚠️ Differenza significativa trovata!")
        # Prepara file per confronto dettagliato
        shutil.copyfile(f"grafici/risultati_{tag1}.txt", "risultati_release1.txt")
        shutil.copyfile(f"grafici/risultati_{tag2}.txt", "risultati_release2.txt")

        # Confronto campione per campione
        subprocess.run(['python3', 'confronto_campionamenti.py'])

        # Analisi refactoring
        analizza_refactoring(tag1, tag2)

        # Misura energetica solo sui test coinvolti nei refactoring
        print("⚡ Avvio misura mirata sui test coinvolti nei refactoring...")
        subprocess.run([script_misura2, tag1, repo_path], check=True)
        subprocess.run([script_misura2, tag2, repo_path], check=True)



print("\n✅ Analisi completata per tutte le release.")