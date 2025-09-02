README
Progetto di tesi " analisi dell'impatto dei refactoring sul consumo di energia nei progetti open source "
Questo progetto automatizza l'analisi e il confronto di refactoring e il loro impatto sul consumo energetico e sui test associati. Utilizza strumenti come JaCoCo per l'analisi della copertura del codice e RefactoringMiner per identificare i refactoring tra diverse versioni di un progetto.

Struttura del Progetto
Principali Script Python
automazione.py
Script principale che coordina l'intero processo di analisi. Include:

Misurazione del consumo energetico.
Analisi dei refactoring tra release consecutive.
Generazione di report di copertura del codice.
Confronto dei risultati pre e post-refactoring.
filtro_refactoring_per_tipologia.py
Filtra i refactoring di un determinato tipo da un file JSON e salva i risultati in un nuovo file JSON.

conteggio_refactoring.py
Conta i refactoring per tipo da un file JSON filtrato e genera un file CSV con il conteggio.

refactoring_effettuati.py
Estrae informazioni sui refactoring da un file JSON e le salva in un file CSV.

filter_tests.py
Analizza i report di JaCoCo per mappare le classi refactorate ai test che le coprono.

pre_post_refactoring.py
Confronta il consumo energetico tra due release consecutive e genera un file CSV con i risultati.

lu.py
Estrae i metodi refactorati di tipo "Extract Method" e li salva in un file compatibile con JaCoCo.

Flusso di Lavoro
Preparazione dei Dati

Utilizzare RefactoringMiner per generare un file JSON con i refactoring tra due release.
Filtrare i refactoring di interesse con filtro_refactoring_per_tipologia.py.
Analisi dei Refactoring

Utilizzare refactoring_effettuati.py per estrarre i dettagli dei refactoring in formato CSV.
Contare i refactoring per tipo con conteggio_refactoring.py.
Analisi dei Test

Generare i report di copertura del codice con JaCoCo.
Mappare i test alle classi refactorate con filter_tests.py.
Confronto Pre/Post Refactoring

Misurare il consumo energetico con script esterni.
Confrontare i risultati pre e post-refactoring con pre_post_refactoring.py.
Automazione Completa

Eseguire l'intero processo con automazione.py.
Requisiti
Python 3.12
Librerie Python:
pandas
xml.etree.ElementTree
json
csv
subprocess
shutil
re
Strumenti esterni:
RefactoringMiner
JaCoCo
Esempi di Utilizzo
Filtrare Refactoring
Contare Refactoring
Analisi Automatica
Output Generati
File JSON

Refactoring filtrati: estratti_<tipo_refactoring>.json
File CSV

Dettagli refactoring: metodo_refactoring_<tipo>.csv
Conteggio refactoring: refactoring_quantificati.csv
Confronto consumo CPU: confronto_consumo_cpu.csv
File di Test

Test coinvolti: test_involved_<tipo>.txt
Note
Assicurarsi che i percorsi dei file e delle directory siano configurati correttamente negli script.
I report di JaCoCo devono essere generati prima di eseguire l'analisi dei test.
Contatti
Per ulteriori informazioni, contattare l'autore del progetto.
