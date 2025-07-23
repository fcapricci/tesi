import re
import os
import csv
import sys
import matplotlib.pyplot as plt

# --- USO ---
if len(sys.argv) != 2:
    print("Uso: python grafici.py <file_output.txt>")
    sys.exit(1)

file_path = sys.argv[1]
output_dir = 'grafici'
os.makedirs(output_dir, exist_ok=True)

base_filename = os.path.splitext(os.path.basename(file_path))[0]

perf_data = {}
hwmon_data = {}
gpu_data = {}
current_run = 0

# --- Parsing file ---
with open(file_path, 'r') as file:
    for line in file:
        if "===== ESECUZIONE" in line:
            current_run += 1
            perf_data[current_run] = []
            hwmon_data[current_run] = []
            gpu_data[current_run] = []

        perf_match = re.search(r'^\s*\d+\.\d+\s+([\d,]+)\s+Joules', line)
        if perf_match:
            joules = float(perf_match.group(1).replace(',', '.'))
            perf_data[current_run].append(joules)

        hwmon_match = re.search(r'\[.*?\] \[HWMON\] .*? = (\d+) mW', line)
        if hwmon_match:
            mwatts = int(hwmon_match.group(1))
            hwmon_data[current_run].append(mwatts / 1000)

        gpu_match = re.search(r'\[.*?\] \[GPU\] PPT = ([\d.]+) W', line)
        if gpu_match:
            gpu_data[current_run].append(float(gpu_match.group(1)))

# --- Funzione per grafici ---
def plot_domain(data, title, ylabel, filename):
    plt.figure(figsize=(10, 6))
    for run, values in data.items():
        plt.plot(range(len(values)), values, label=f'Esecuzione {run}')
    plt.title(f"{title}\nFile dati: {base_filename}")
    plt.xlabel('Campionamento')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()

# --- Disegna i grafici ---
plot_domain(perf_data, 'Energia CPU (perf)', 'Joule', f'{base_filename}_energia_cpu_perf.png')
plot_domain(hwmon_data, 'Potenza HWMON', 'Watt', f'{base_filename}_potenza_hwmon.png')
plot_domain(gpu_data, 'Potenza GPU (PPT)', 'Watt', f'{base_filename}_potenza_gpu_ppt.png')

# --- CSV Riassuntivo ---
csv_path = os.path.join(output_dir, f'{base_filename}_summary.csv')
with open(csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Esecuzione', 'Energia media CPU (J)', 'Max HWMON (W)', 'Max GPU PPT (W)'])
    for run in sorted(perf_data.keys()):
        avg_perf = round(sum(perf_data[run]) / len(perf_data[run]), 2) if perf_data[run] else 0
        max_hwmon = round(max(hwmon_data[run]), 2) if hwmon_data[run] else 0
        max_gpu = round(max(gpu_data[run]), 2) if gpu_data[run] else 0
        writer.writerow([run, avg_perf, max_hwmon, max_gpu])

print(f"Tutti i grafici sono stati salvati nella cartella '{output_dir}' ✅")
print(f"Riepilogo esportato in CSV: {csv_path} ✅")