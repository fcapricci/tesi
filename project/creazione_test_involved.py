import pandas as pd

# === Config ===
CSV_INPUT = "metodi_coperti_da_test_extractAndMoveMethod.csv"  # il file di partenza
OUTPUT_FILE = "test_involved_extractAndMoveMethod.txt"  # file di output

# Carica il CSV
df = pd.read_csv(CSV_INPUT)

# Prende solo la colonna "TestIdentifier", rimuove duplicati e valori vuoti
test_list = df["TestIdentifier"].dropna().drop_duplicates()

# Salva in un file di testo, una riga per test
test_list.to_csv(OUTPUT_FILE, index=False, header=False)

print(f"✅ Creato {OUTPUT_FILE} con {len(test_list)} test")
