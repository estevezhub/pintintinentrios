#!/bin/bash
# Experimentos de la auditoría. Cada bloque escribe su propio archivo.
cd "$(dirname "$0")/../.."
D=analisis/datos
python3 motor/laboratorio.py bench \
  "lin:ahogo=40,amenaza=-1,pts=0.3,doble=1,cerco=0.5,cebo=0.3,cob=0.05" \
  "lin:ahogo=40,amenaza=-1,pts=0.3,doble=2,cerco=0.5,cebo=0.3,cob=0.05" \
  "lin:ahogo=40,amenaza=-1,pts=0.3,doble=4,cerco=0.5,cebo=0.3,cob=0.05" \
  "lin:ahogo=40,amenaza=-1,pierde=-3,pts=0.3,cerco=0.5,cebo=0.3,cob=0.05" \
  "lin:ahogo=40,amenaza=-1,pierde=-3,pts=0.6,cerco=0.5,cebo=0.3,cob=0.05" \
  --rival maestro --rondas 12000 > $D/pesos_dobles.txt 2>&1
PINTINTIN_PASE_EN_TRANCA=0 python3 motor/laboratorio.py bench novato jugador fogueado "lex:ahogo,-amenaza,pts" \
  --rival maestro --rondas 12000 > $D/tranca_sin_pase.txt 2>&1
python3 motor/laboratorio.py bench sabio96 --rival jugador --rondas 1500 > $D/sabio96_vs_jugador.txt 2>&1
python3 motor/laboratorio.py bench sabio192 --rival maestro --rondas 3000 > $D/sabio192_vs_maestro.txt 2>&1
echo FIN > $D/.fin
