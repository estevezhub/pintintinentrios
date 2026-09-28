#!/bin/bash
# Campaña de estrategias: tribunal → búsqueda evolutiva → imitación del Sabio
cd "$(dirname "$0")/../.."
D=analisis/datos
rm -f $D/.campana_fin
python3 motor/campana.py tribunal --rondas 18000 > $D/campana_tribunal.log 2>&1
python3 motor/campana.py cem --gen 14 --pob 16 --rondas 4000 > $D/campana_cem.log 2>&1
python3 motor/campana.py imitar --rondas 1200 --muestras 96 > $D/campana_imitar.log 2>&1
echo FIN > $D/.campana_fin
