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
