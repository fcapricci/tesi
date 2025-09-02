# Progetto di Analisi e Confronto Refactoring

Questo progetto automatizza l'analisi e il confronto di refactoring e il loro impatto sul consumo energetico e sui test associati. Utilizza strumenti come JaCoCo per l'analisi della copertura del codice e RefactoringMiner per identificare i refactoring tra diverse versioni di un progetto.

---

## Struttura del Progetto

### Principali Script Python

- **[`automazione.py`](automazione.py)**  
  Script principale che coordina l'intero processo di analisi. Include:
  - Misurazione del consumo energetico.
  - Analisi dei refactoring tra release consecutive.
  - Generazione di report di copertura del codice.
  - Confronto dei risultati pre e post-refactoring.

- **[`filtro_refactoring_per_tipologia.py`](filtro_refactoring_per_tipologia.py)**  
  Filtra i refactoring di un determinato tipo da un file JSON e salva i risultati in un nuovo file JSON.

- **[`conteggio_refactoring.py`](conteggio_refactoring.py)**  
  Conta i refactoring per tipo da un file JSON filtrato e genera un file CSV con il conteggio.

- **[`refactoring_effettuati.py`](refactoring_effettuati.py)**  
  Estrae informazioni sui refactoring da un file JSON e le salva in un file CSV.

- **[`filter_tests.py`](filter_tests.py)**  
  Analizza i report di JaCoCo per mappare le classi refactorate ai test che le coprono.

- **[`pre_post_refactoring.py`](pre_post_refactoring.py)**  
  Confronta il consumo energetico tra due release consecutive e genera un file CSV con i risultati.

- **[`lu.py`](lu.py)**  
  Estrae i metodi refactorati di tipo "Extract Method" e li salva in un file compatibile con JaCoCo.

---

## Flusso di Lavoro

1. **Preparazione dei Dati**  
   - Utilizzare RefactoringMiner per generare un file JSON con i refactoring tra due release.
   - Filtrare i refactoring di interesse con [`filtro_refactoring_per_tipologia.py`](filtro_refactoring_per_tipologia.py).

2. **Analisi dei Refactoring**  
   - Utilizzare [`refactoring_effettuati.py`](refactoring_effettuati.py) per estrarre i dettagli dei refactoring in formato CSV.
   - Contare i refactoring per tipo con [`conteggio_refactoring.py`](conteggio_refactoring.py).

3. **Analisi dei Test**  
   - Generare i report di copertura del codice con JaCoCo.
   - Mappare i test alle classi refactorate con [`filter_tests.py`](filter_tests.py).

4. **Confronto Pre/Post Refactoring**  
   - Misurare il consumo energetico con script esterni.
   - Confrontare i risultati pre e post-refactoring con [`pre_post_refactoring.py`](pre_post_refactoring.py).

5. **Automazione Completa**  
   - Eseguire l'intero processo con [`automazione.py`](automazione.py).

---

## Requisiti

- **Python 3.12**
- Librerie Python:
  - `pandas`
  - `xml.etree.ElementTree`
  - `json`
  - `csv`
  - `subprocess`
  - `shutil`
  - `re`
- Strumenti esterni:
  - **RefactoringMiner**
  - **JaCoCo**

---

## Output generati
1. **File JSON**  
   

2. **File csv**  

3. **Grafici**  
   - Nella cartella grafici sono riportati tutti i confronti e le misurazioni

---

 ## Note
 Assicurarsi che i percorsi dei file e delle directory siano configurati correttamente negli script.
 I report di JaCoCo devono essere generati prima di eseguire l'analisi dei test.
