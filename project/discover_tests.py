import os

repo_path = "repo"  # cartella della repo locale
output_file = os.path.join(repo_path, "all_test_classes.txt")

# Se il file esiste, non rigenerarlo
if os.path.exists(output_file):
    print(f"✅ Classi di test già individuate: {output_file}")
    exit(0)

test_classes = []

# Cerca ricorsivamente tutte le cartelle src/test/java
for root, dirs, files in os.walk(repo_path):
    if os.path.basename(root) == "java" and "src/test" in root.replace("\\", "/"):
        for dirpath, _, filenames in os.walk(root):
            for file in filenames:
                if file.endswith("Test.java"):
                    full_path = os.path.join(dirpath, file)
                    relative_path = os.path.relpath(full_path, root)
                    class_name = relative_path.replace("/", ".").replace("\\", ".").replace(".java", "")
                    if ".perf" not in class_name:
                        test_classes.append(class_name)

# Salva su file
with open(output_file, "w") as out:
    for cls in sorted(test_classes):
        out.write(cls + "\n")

print(f"✅ Trovate {len(test_classes)} classi di test (escluse .perf). Salvate in {output_file}")
