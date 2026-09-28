# Datos crudos de la auditoría (28-sep-2026)

Salida directa de cada experimento. Las cifras de los documentos salen de aquí.
Cómo regenerarlas: `../pintintin-metodologia.md` §7.

| Archivo | Experimento | Sección |
|---|---|---|
| `pesos_dobles.txt`, `tranca_sin_pase.txt` | Variantes de pesos; la escalera con la regla "tranca sin pase" | auditoría §4.1, §6 |
| `sabio96_vs_jugador.txt`, `sabio192_vs_maestro.txt` | El Sabio contra Jugadores y Maestros | §4.2 |
| `perfil_maestros.txt`, `perfil_mixta.txt` | Puntos por mano y situaciones de riesgo | §4.6–4.7 |
| `complice*.txt` | La estrategia del cómplice; dura vs suave | §4.8 |
| `remontada_*.txt` | El reloj, planes alternativos, umbrales, Sabio yendo abajo | §4.9 |
| `tacticas_*.txt` | Farol de la pinza; repite, mata y tranca; qué pasa al repetir | §4.10 |
| `campana_tribunal.txt` | 44 afirmaciones juzgadas | §4.11a |
| `campana_cem.log`, `cem_historia.json` | Búsqueda evolutiva (pesos por generación) | §4.11b |
| `campana_imitar.log`, `imitar_sabio.json` | Imitación del Sabio (logit condicional) | §4.11c |
| `candidatos.json`, `campana_validar*.log`, `campana_ablacion.log` | Validación con control en mismas semillas; ablación | §4.11d |
| `campana_liga.txt`, `liga_pool.json` | Liga de 21 estrategias con Elo | §4.11e |
| `correr_cola.sh`, `correr_campana.sh` | Scripts que generaron las corridas largas | — |

Las primeras corridas de la auditoría (benchmark contra Maestros, Omnisciente,
Sabio 24/96, órdenes lexicográficos, estudio de la salida, diferencias
Sabio–Maestro, verificación) se perdieron de una carpeta temporal por una
interrupción. Sus cifras están transcritas en la auditoría y se regeneran con
los comandos de la metodología.
