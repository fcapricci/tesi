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
# Leggi i test coinvolti, rimuovi righe vuote, uniscili con virgole
test_classes=$(grep -v '^$' "/home/federico/JGraphT_Test/project/tests_involved.txt" | paste -sd, -)

if [ -z "$test_classes" ]; then
  echo "❌ Nessun test trovato in tests_involved.txt"
  exit 1
fi

comando="mvn -Dtest=${test_classes} -DfailIfNoTests=false test"
tempo_attesa=0

mkdir -p ../grafici
timestamp=$(date '+%Y-%m-%d_%H-%M-%S')
file_output="../grafici/risultati_${tag}_refactoring.txt"

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

# === Esecuzioni ===
for ((i = 1; i <= numero_esecuzioni; i++)); do
  echo "Inizio esecuzione $i di $numero_esecuzioni..."
  echo -e "\n\n===== ESECUZIONE $i DI $numero_esecuzioni =====" >> "$file_output"
  echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')" >> "$file_output"
  echo "Comando: $comando" >> "$file_output"

  monitor_hwmon & PID_HWMON=$!
  monitor_gpu_power & PID_GPU=$!

  echo -e "\n--- OUTPUT COMANDO + PERF ---" >> "$file_output"
  sudo perf stat -I $intervallo -e power/energy-pkg/ \
    env JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64" \
    PATH="/usr/lib/jvm/java-11-openjdk-amd64/bin:$PATH" \
    $comando 2>> "$file_output"

  kill $PID_HWMON $PID_GPU 2>/dev/null
  wait $PID_HWMON $PID_GPU 2>/dev/null

  echo "--- FINE ESECUZIONE $i ---" >> "$file_output"

  if [ $i -lt $numero_esecuzioni ]; then
    sleep $tempo_attesa
  fi
done

# === Generazione grafici + CSV ===
cd .. || exit 1
python3 grafici.py grafici/risultati_${tag}.txt

echo -e "\n✅ Misura completata per release $tag. Output: grafici/risultati_${tag}_refactoring.txt"
