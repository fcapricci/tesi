import os
import csv
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd

# === CONFIG ===
CSV_INPUT = "tabella_metodo_refactoring_test_extractAndMoveMethod.csv"
JACOCO_DIR = "jacoco_reports"
CSV_OUTPUT = "metodi_coperti_da_test_extractAndMoveMethod.csv"

# Heuristic: estrae la FQN di classe di produzione dalla colonna "Classe"
# Esempio input: "jgrapht-core.src.main.org.jgrapht.traverse.CrossComponentIterator"
# -> "org.jgrapht.traverse.CrossComponentIterator"
def normalize_target_class(classe_value: str) -> str:
    if not isinstance(classe_value, str):
        return ""
    # prova a tagliare dopo ".src.main."
    m = re.search(r"\.src\.main\.(.+)$", classe_value)
    if m:
        return m.group(1)
    # fallback: prendi dalla prima occorrenza di 'org.'
    m2 = re.search(r"(org\.[A-Za-z0-9_$.]+)$", classe_value)
    if m2:
        return m2.group(1)
    return classe_value

# Estrae il simple-name del metodo dalla colonna "Metodo"
# Esempi:
# "public calculateMaximumFlow(source V, sink V) : double" -> "calculateMaximumFlow"
# "public ClosestFirstIterator(g Graph<V,E>, ... ) : void" (costruttore) -> simple name della classe (gestito più avanti)
def extract_method_simple_name(metodo_value: str) -> str:
    if not isinstance(metodo_value, str):
        return ""
    # prendi il token immediatamente prima della prima parentesi tonda
    # ignorando visibilità/return type
    # cattura l'ultima parola prima di "("
    m = re.search(r"([A-Za-z_$][A-Za-z0-9_$]*)\s*\(", metodo_value)
    return m.group(1) if m else ""

# Dal nome file "jacoco_..." prova a estrarre classe di test e (se presente) metodo di test.
# Supporta:  #  ::  __  come separatori classe/metodo
# Esempi:
# jacoco_org_jgrapht_alg_MyTest.xml -> org.jgrapht.alg.MyTest
# jacoco_org_jgrapht_alg_MyTest#testFoo.xml -> org.jgrapht.alg.MyTest#testFoo
def parse_test_identifier_from_filename(path: str) -> str:
    name = os.path.splitext(os.path.basename(path))[0]
    if not name.startswith("jacoco_"):
        core = name
    else:
        core = name[len("jacoco_"):]
    # Separa eventuale metodo di test
    test_method = None
    test_class_part = core
    for sep in ("#", "::", "__"):
        if sep in core:
            test_class_part, test_method = core.split(sep, 1)
            break
    # Underscore -> dots per la parte di classe
    test_class = test_class_part.replace("_", ".")
    return f"{test_class}#{test_method}" if test_method else test_class

# Verifica se un metodo (per FQN classe + simple-name) risulta coperto nel report JaCoCo
# - Gestisce i costruttori: in JaCoCo sono riportati come "<init>"
def is_method_covered_in_report(report_path: str, target_class_fqn: str, target_method_simple: str) -> bool:
    try:
        tree = ET.parse(report_path)
        root = tree.getroot()
    except Exception:
        return False

    # Converte FQN "org.jgrapht.alg.Foo" in "org/jgrapht/alg"
    pkg = ".".join(target_class_fqn.split(".")[:-1])
    cls_simple = target_class_fqn.split(".")[-1]
    jacoco_pkg = pkg.replace(".", "/")
    # JaCoCo usa class name completo con package: "org/jgrapht/alg/Foo" o a volte "org/jgrapht/alg/Foo$Inner"
    target_class_name = f"{pkg}.{cls_simple}"

    # Trova <package name="org/jgrapht/alg">
    for pkg_el in root.findall("package"):
        if pkg_el.get("name") != jacoco_pkg:
            continue
        # dentro il package, cerca la/e classi
        for cls_el in pkg_el.findall("class"):
            # Attributo "name" può essere "org/jgrapht/alg/Foo" o "org/jgrapht/alg/Foo$Inner"
            cls_name_attr = cls_el.get("name", "")
            # Converte in FQN puntata per confronto
            cls_fqn_from_attr = cls_name_attr.replace("/", ".")
            # match anche eventuali inner classes della target class
            if not (cls_fqn_from_attr == target_class_name or cls_fqn_from_attr.startswith(target_class_name + "$")):
                continue

            # Determina il nome metodo come lo esprime JaCoCo:
            # se è costruttore, in JaCoCo è "<init>"
            jacoco_method_name = "<init>" if target_method_simple == cls_simple else target_method_simple

            for m_el in cls_el.findall("method"):
                if m_el.get("name") != jacoco_method_name:
                    continue
                # Se c'è qualche coverage > 0 consideriamo coperto
                covered = False
                for c in m_el.findall("counter"):
                    cov = int(c.get("covered", "0"))
                    if cov > 0:
                        covered = True
                        break
                if covered:
                    return True
    return False

def main():
    if not os.path.exists(CSV_INPUT):
        raise SystemExit(f"CSV non trovato: {CSV_INPUT}")
    if not os.path.isdir(JACOCO_DIR):
        raise SystemExit(f"Cartella report JaCoCo non trovata: {JACOCO_DIR}")

    df = pd.read_csv(CSV_INPUT)

    # Colonne attese: Metodo, Refactoring, Classe, TestClass
    required_cols = {"Metodo", "Refactoring", "Classe", "TestClass"}
    missing = required_cols - set(df.columns)
    if missing:
        raise SystemExit(f"Mancano colonne nel CSV: {missing}")

    results = []
    seen = set()  # per deduplicare (targetClass, targetMethod, refactoring, testId)

    for _, row in df.iterrows():
        metodo_raw = row["Metodo"]
        refactoring = row["Refactoring"]
        classe_raw = row["Classe"]
        testclass_raw = row["TestClass"]

        target_class_fqn = normalize_target_class(str(classe_raw))
        target_method_simple = extract_method_simple_name(str(metodo_raw))

        if not target_class_fqn or not target_method_simple:
            continue

        # Lista di potenziali report da controllare (da colonna TestClass, separati da virgola)
        report_candidates = []
        if isinstance(testclass_raw, str) and testclass_raw.strip():
            for item in str(testclass_raw).split(","):
                item = item.strip()
                if not item:
                    continue
                # aggiungi ".xml" se manca e risolvi path
                fname = item if item.endswith(".xml") else f"{item}.xml"
                path = os.path.join(JACOCO_DIR, fname)
                if os.path.exists(path):
                    report_candidates.append(path)

        # Se la colonna non aiuta o i file non esistono, fallback: scorri tutti i report
        if not report_candidates:
            for fn in os.listdir(JACOCO_DIR):
                if fn.endswith(".xml"):
                    report_candidates.append(os.path.join(JACOCO_DIR, fn))

        for report_path in report_candidates:
            if is_method_covered_in_report(report_path, target_class_fqn, target_method_simple):
                test_identifier = parse_test_identifier_from_filename(report_path)
                key = (target_class_fqn, target_method_simple, refactoring, test_identifier)
                if key not in seen:
                    seen.add(key)
                    results.append({
                        "TargetClass": target_class_fqn,
                        "TargetMethod": target_method_simple,
                        "Refactoring": refactoring,
                        "TestIdentifier": test_identifier
                    })

    # Salva CSV
    os.makedirs(os.path.dirname(CSV_OUTPUT) or ".", exist_ok=True)
    with open(CSV_OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["TargetClass","TargetMethod","Refactoring","TestIdentifier"])
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Creato: {CSV_OUTPUT} ({len(results)} righe)")

if __name__ == "__main__":
    main()
