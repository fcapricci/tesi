#!/bin/bash

# Parametri configurabili
read -p "Inserisci il numero di esecuzioni: " numero_esecuzioni
if ! [[ $numero_esecuzioni =~ ^[0-9]+$ ]] || [ "$numero_esecuzioni" -le 0 ]; then
    echo "Errore: il numero di esecuzioni deve essere un intero positivo."
    exit 1
fi

read -p "Inserisci intervallo per la misurazione (in ms, minimo 100): " intervallo
if ! [[ $intervallo =~ ^[0-9]+$ ]] || [ "$intervallo" -lt 100 ]; then
    echo "Errore: l'intervallo deve essere almeno 100ms."
    exit 1
fi

read -p "Inserisci il comando da eseguire: " comando
if ! command -v $comando &>/dev/null; then
    echo "Errore: comando '$comando' non trovato."
    exit 1
fi

read -p "Inserisci il tempo di attesa tra le esecuzioni (in secondi): " tempo_attesa
if ! [[ $tempo_attesa =~ ^[0-9]+$ ]] || [ "$tempo_attesa" -lt 0 ]; then
    echo "Errore: il tempo di attesa deve essere un valore non negativo."
    exit 1
fi

# Nome del file di output con timestamp
file_output="risultati_$(date '+%Y-%m-%d_%H-%M-%S').txt"

# Loop per le esecuzioni
for ((i=1; i<=numero_esecuzioni; i++))
do
    echo "Inizio esecuzione $i di $numero_esecuzioni..."
    echo "=== Esecuzione $i di $numero_esecuzioni ===" >> "$file_output"

    # Esegui il comando specificato
    echo "Eseguendo il comando: $comando"
    $comando >> "$file_output" 2>&1

    # Leggi i dati energetici da sensors (CPU e GPU)
    sensors_output=$(sensors)

    sudo perf stat -I $intervallo -e power/energy-pkg/ $comando >> "$file_output" 2>&1

    # Estrai il consumo energetico della GPU (PPT)
    gpu_power=$(echo "$sensors_output" | grep 'PPT' | awk '{print $2}')
    if [ -n "$gpu_power" ]; then
        echo "Consumo energetico GPU (W): $gpu_power" >> "$file_output"
    else
        echo "Non è stato possibile leggere il consumo energetico della GPU." >> "$file_output"
    fi

    # Analizza eventuali dati disponibili su hwmon per altre fonti energetiche
    for file in /sys/class/hwmon/hwmon*/power*_input; do
        if [ -f "$file" ]; then
            power_value=$(cat "$file")
            echo "Consumo energetico (da $file): $((power_value / 1000)) mW" >> "$file_output"
        fi
    done

    # Attendi il tempo specificato tra le esecuzioni
    if [ $i -lt $numero_esecuzioni ]; then
        echo "Attendo $tempo_attesa secondi prima della prossima esecuzione..."
        sleep $tempo_attesa
    fi
done

echo "Tutte le esecuzioni completate. I risultati sono stati salvati in $file_output."

