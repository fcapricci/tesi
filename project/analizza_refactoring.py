import json
import sys
import os

if len(sys.argv) != 3:
    sys.exit(1)

tag_old, tag_new = sys.argv[1], sys.argv[2]
input_path = f"refactoring_{tag_old}_to_{tag_new}.json"
output_path = "filtered_refactorings.json"

if not os.path.exists(input_path):
    sys.exit(1)

if os.path.exists(output_path):
    print(f"✅ Refactoring già filtrato: {output_path}")
    sys.exit(0)

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

commits = data.get("commits", [])
filtered_commits = []

method_refactoring_keywords = [
    "Method", "Rename Method", "Extract Method", "Inline Method",
    "Move Method", "Pull Up Method", "Push Down Method", "Change Return Type",
    "Change Parameter", "Remove Parameter", "Add Parameter"
]

for commit in commits:
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

    filtered_commits.append({
        "repository": commit.get("repository", ""),
        "sha1": commit.get("sha1", ""),
        "url": commit.get("url", ""),
        "refactorings": filtered_refactorings
    })

with open(output_path, "w", encoding="utf-8") as out_file:
    json.dump({"commits": filtered_commits}, out_file, indent=2)

print(f"✅ Refactoring filtrato e salvato: {output_path}")
