import os

test_classes = []

# Cerca ricorsivamente tutte le cartelle src/test/java
for root, dirs, files in os.walk("."):
    if os.path.basename(root) == "java" and "src/test" in root.replace("\\", "/"):
        for dirpath, _, filenames in os.walk(root):
            for file in filenames:
                if file.endswith("Test.java"):
                    full_path = os.path.join(dirpath, file)
                    relative_path = os.path.relpath(full_path, root)
                    class_name = relative_path.replace("/", ".").replace("\\", ".").replace(".java", "")
                    test_classes.append(class_name)

# Salva su file
with open("all_test_classes.txt", "w") as out:
    for cls in sorted(test_classes):
        out.write(cls + "\n")

print(f"✅ Trovate {len(test_classes)} classi di test in più moduli. Salvate in all_test_classes.txt")
