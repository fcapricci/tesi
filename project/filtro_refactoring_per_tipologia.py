import json
import sys

def filtra_refactoring(json_path, tipo_desiderato, output_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Lista dei commit che contengono refactoring del tipo desiderato
    refactorings_filtrati = []

    # Lista piatta di tutti i singoli refactoring (per conteggio e salvataggio alternativo)
    refactorings_singoli = []

    for commit in data.get('commits', []):
        matching = [r for r in commit.get('refactorings', []) if r.get('type') == tipo_desiderato]
        if matching:
            refactorings_filtrati.append({
                "repository": commit.get("repository"),
                "sha1": commit.get("sha1"),
                "refactorings": matching
            })
            refactorings_singoli.extend(matching)

    # Salva i commit filtrati in output
    with open(output_path, 'w', encoding='utf-8') as out:
        json.dump({"commits": refactorings_filtrati}, out, indent=2, ensure_ascii=False)

    # Stampa conteggio
    print(f"✅ Salvato file con {len(refactorings_filtrati)} commit che contengono '{tipo_desiderato}'")
    print(f"🔢 Totale refactoring '{tipo_desiderato}' trovati: {len(refactorings_singoli)}")



# === ESEMPIO DI USO DA TERMINALE ===
# python filtra_refactoring.py refactorings.json "Extract Method" estratti_extract_method.json

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python filtra_refactoring.py <input_json> <tipo_refactoring> <output_json>")
        sys.exit(1)

    input_json = sys.argv[1]
    tipo_refactoring = sys.argv[2]
    output_json = sys.argv[3]

    filtra_refactoring(input_json, tipo_refactoring, output_json)
