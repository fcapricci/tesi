#!/bin/bash

echo "▶️ Avvio esecuzione test con report aggregato per modulo..."

mkdir -p jacoco_reports

# Trova tutti i moduli che contengono test
modules=$(find . -type f -path "*/src/test/java/*.java" | sed 's|/src/test/java/.*||' | sort -u)

for module_dir in $modules; do
  echo "📦 Modulo: $module_dir"

  cd "$module_dir" || continue

  # Pulisce eventuali dati precedenti
  rm -f target/jacoco.exec target/site/jacoco/jacoco.xml

  # Esegue tutti i test del modulo con JaCoCo
  mvn -fn clean \
    -Djacoco.append=false \
    jacoco:prepare-agent test jacoco:report

  # Salva il report aggregato
  if [ -f target/site/jacoco/jacoco.xml ]; then
    module_name=$(basename "$module_dir")
    cp target/site/jacoco/jacoco.xml "../../jacoco_reports/jacoco_${module_name}.xml"
    echo "  ✅ Report salvato per modulo $module_name"
  else
    echo "  ⚠️ Report mancante per $module_dir"
  fi

  cd - > /dev/null || exit
done

echo "✅ Fine. Report aggregati in ./jacoco_reports"
