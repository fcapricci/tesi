#!/bin/bash

tag="$1"
repo_path="$2"

if [ -z "$tag" ] || [ -z "$repo_path" ]; then
  echo "❌ Uso: $0 <tag_release> <repo_path>"
  exit 1
fi

if [ ! -d "$repo_path" ]; then
  echo "❌ Errore: la directory della repository '$repo_path' non esiste."
  exit 1
fi

cd "$repo_path" || exit 1

# === CONFIG ===
numero_esecuzioni=2
intervallo=100
tempo_attesa=0
tests_file="/home/federico/JGraphT_Test/project/test_involved.txt"

if [ ! -f "$tests_file" ]; then
  echo "❌ File $tests_file mancante"
  exit 1
fi

# === Output ===
mkdir -p ../grafici
csv_output="../grafici/risultati_${tag}_refactoring_specifici_summary.csv"
echo "ClasseDiTest,Esecuzione,Energia media CPU (J)" > "$csv_output"

# === Estrai classi di test ===
mapfile -t classi < <(sed 's/^jacoco_//' "$tests_file" | sed 's/_/./g')


for class in "${classi[@]}"; do
  for ((i = 1; i <= numero_esecuzioni; i++)); do
    echo "▶️ Classe: $class | Esecuzione $i di $numero_esecuzioni"

    # Misura energia con perf
    perf_output=$(sudo perf stat -x, -I $intervallo -e power/energy-pkg/ \
      env JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64" \
      PATH="/usr/lib/jvm/java-11-openjdk-amd64/bin:$PATH" \
      mvn -Dtest="$class" -DfailIfNoTests=false test 2>&1)

    energia_cpu=$(echo "$perf_output" | grep 'energy-pkg' | awk -F',' '{sum += $1} END {if (NR > 0) print sum/NR; else print 0}')

    echo "$class,$i,$energia_cpu" >> "$csv_output"

    if [ $i -lt $numero_esecuzioni ]; then
      sleep $tempo_attesa
    fi
  done
done

echo -e "\n✅ Misurazione completata per $tag — solo energia CPU salvata in $csv_output"
