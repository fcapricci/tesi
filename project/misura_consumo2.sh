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

# === CONFIGURAZIONE ===
numero_esecuzioni=2
intervallo=100
tempo_attesa=0
tests_file="/home/federico/JGraphT_Test/project/test_involved_extractAndMoveMethod.txt"

if [ ! -f "$tests_file" ]; then
  echo "❌ File $tests_file mancante"
  exit 1
fi

# === Output ===
mkdir -p ../grafici
timestamp=$(date '+%Y-%m-%d_%H-%M-%S')
file_output="../grafici/risultati_${tag}_refactoring_extractAndMoveMethod.txt"

# === Monitoraggio HWMON ===
monitor_hwmon() {
  while true; do
    for file in /sys/class/hwmon/hwmon*/power*_input; do
      if [ -f "$file" ]; then
        ts=$(date +%s%3N)
        val=$(cat "$file")
        echo "[$ts] [HWMON] $file = $((val / 1000)) mW" >> "$file_output"
      fi
    done
    sleep $(awk "BEGIN {print $intervallo / 1000}")
  done
}

# === Monitoraggio GPU ===
monitor_gpu_power() {
  while true; do
    ts=$(date +%s%3N)
    sensors_output=$(sensors)
    gpu_power=$(echo "$sensors_output" | grep 'PPT' | awk '{print $2}')
    if [ -n "$gpu_power" ]; then
      echo "[$ts] [GPU] PPT = $gpu_power W" >> "$file_output"
    fi
    sleep $(awk "BEGIN {print $intervallo / 1000}")
  done
}

# === Leggi tutte le classi di test in una riga, separate da virgola ===
test_classes=$(
  awk '{
    s=$0
    sub(/^jacoco_/,"",s)     # togli prefisso jacoco_
    sub(/\.xml$/,"",s)       # togli eventuale .xml
    gsub(/_/,".",s)          # _ -> .
    print s
  }' "$tests_file" | paste -sd, -
)

if [ -z "$test_classes" ]; then
  echo "❌ Nessuna classe di test valida trovata nel file."
  exit 1
fi

# === Esecuzioni ===
for ((i = 1; i <= numero_esecuzioni; i++)); do
  echo -e "\n\n===== ESECUZIONE $i DI $numero_esecuzioni =====" >> "$file_output"
  echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')" >> "$file_output"
  echo "▶️ Eseguo tutte le classi: $test_classes" >> "$file_output"

  monitor_hwmon & PID_HWMON=$!
  monitor_gpu_power & PID_GPU=$!

  sudo perf stat -I $intervallo -e power/energy-pkg/ \
    env JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64" \
    PATH="/usr/lib/jvm/java-11-openjdk-amd64/bin:$PATH" \
    mvn -Dtest="$test_classes" -Dsurefire.failIfNoSpecifiedTests=false -DfailIfNoTests=false test \
    2>> "$file_output"

  kill $PID_HWMON $PID_GPU 2>/dev/null
  wait $PID_HWMON $PID_GPU 2>/dev/null

  echo "--- FINE ESECUZIONE $i ---" >> "$file_output"

  if [ $i -lt $numero_esecuzioni ]; then
    sleep $tempo_attesa
  fi
done

# === Generazione grafici (opzionale) ===
cd .. || exit 1
python3 grafici.py "grafici/risultati_${tag}_refactoring_extractAndMoveMethod.txt"

echo -e "\n✅ Misura completata per release $tag (esecuzione unica per tutti i test)."
