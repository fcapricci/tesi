import json

# === Percorsi file ===
input_path = "refactoring_jgrapht-1.3.0_to_1.4.0.json"
output_path = "filtered_refactorings.json"

# === Caricamento JSON ===
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

commits = data.get("commits", [])
filtered_commits = []

# === Parole chiave per refactoring di metodi ===
method_refactoring_keywords = [
    "Method", "Rename Method", "Extract Method", "Inline Method",
    "Move Method", "Pull Up Method", "Push Down Method", "Change Return Type",
    "Change Parameter", "Remove Parameter", "Add Parameter"
]

total_commits_with_refactoring = 0
total_refactorings = 0

# === Analisi dei commit ===
for commit_index, commit in enumerate(commits, start=1):
    refactorings = commit.get("refactorings", [])
    filtered_refactorings = []

    for ref in refactorings:
        ref_type = ref.get("type", "")
        if not any(keyword in ref_type for keyword in method_refactoring_keywords):
            continue

        locations = ref.get("leftSideLocations", []) + ref.get("rightSideLocations", [])
        if any("src/test" in loc.get("filePath", "").lower() or "test" in loc.get("filePath", "").lower()
               for loc in locations):
            continue

        filtered_refactorings.append(ref)

    if not filtered_refactorings:
        continue

    total_commits_with_refactoring += 1
    total_refactorings += len(filtered_refactorings)

    print(f"\n📦 Commit {commit_index}")
    print(f"🔗 Repository: {commit.get('repository', 'N/D')}")
    print(f"🔐 SHA1     : {commit.get('sha1', 'N/D')}")
    print(f"🔗 URL      : {commit.get('url', 'N/D')}")

    for idx, ref in enumerate(filtered_refactorings, start=1):
        print(f"\n  🔧 Refactoring {idx}")
        print(f"  Tipo        : {ref.get('type')}")
        print(f"  Descrizione : {ref.get('description')}")
        left_locations = ref.get("leftSideLocations", [])
        if left_locations:
            print("  File coinvolti:")
            for loc in left_locations:
                print(f"    - {loc['filePath']} (linee {loc['startLine']} - {loc['endLine']})")
        else:
            print("    Nessun file segnalato.")

    # Aggiungi al JSON filtrato
    filtered_commits.append({
        "repository": commit.get("repository", ""),
        "sha1": commit.get("sha1", ""),
        "url": commit.get("url", ""),
        "refactorings": filtered_refactorings
    })

# === Salvataggio su file JSON ===
with open(output_path, "w", encoding="utf-8") as out_file:
    json.dump({"commits": filtered_commits}, out_file, indent=2)

print(f"\n✅ Totale commit con refactoring di metodi (esclusi i test): {total_commits_with_refactoring}")
print(f"✅ Totale refactoring di metodi trovati                    : {total_refactorings}")
print(f"📁 Output salvato in: {output_path}")
