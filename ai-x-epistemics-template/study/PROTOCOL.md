# Protocol

## Track

Pista abierta. El conteo usa la encuesta de traslado matutino que el equipo ya levantó. No llama a un modelo.

## Question

Entre quienes aceptaron la encuesta de traslado matutino al campus de la Universidad Politécnica de Yucatán, ¿qué proporción dice que usaría un punto de encuentro para compartir el traslado, y cuántos de esos casos tienen auto propio?

## Metric

`share_willing_yes`: respuestas «Sí» a la pregunta del punto de encuentro, sobre la muestra que aceptó. El runner la escribe en `results/commute.json` con `python -m epistemics run commute`.

Campos de la misma corrida, no métricas aparte: `n_willing_driver`, `n_willing_not_own_car`, `share_own_car`, `share_bus`, `share_late_any_day`, `share_usual_after_0700`, `share_outside_z06`, `n_z06`, `n_outside_z06`, `n_placed`, `n_willing_driver_z06`, `n_willing_not_own_z06`, `n_board_prepa_10`, `n_board_humanitas`, `n_name_americas`, `n_name_americas_yes`. Los asientos vacíos no se cuentan.

## Baseline

`mayoria`, umbral 0.5. Una premisa de «la mayoría» queda por encima de ese umbral solo si la tasa de esta corrida lo supera. No hay una segunda encuesta.

## N

La muestra es cada fila con «Sí, acepto» cuyo cuatrimestre no dice que la encuesta no es para esa persona. El archivo de origen trae 262 filas. La corrida fija n.

## Falsifier

Si `share_willing_yes` no supera 0.5, en esta muestra no es cierto que la mayoría usaría un punto de encuentro. Si `n_willing_driver` no alcanza a `n_willing_not_own_car`, los autos propios que dijeron que sí no cubren, uno a uno, a quienes dijeron que sí y no tienen auto propio. Si `share_outside_z06` no supera 0.5, en la muestra completa no es cierto que la mayoría quede fuera de Z06. Multiplicar `n_willing_driver` por 4 asientos vacíos es un supuesto: la encuesta no pregunta cuántos lugares van libres. Z06 es la zona «Caucel y poniente exterior». Z99 no cuenta como fuera. Una colonia marcada «revisar» no asigna zona. El PDF de tiempos mide un punto por zona, solo Z01 a Z05, y no se copia a las personas.

## Preexisting

El runner, los cuatro ejemplos, los fixtures y el esqueleto del informe vienen con la plantilla. La encuesta es trabajo previo del equipo: la primera respuesta es del 6 de noviembre de 2026 y el sprint empieza el 13. Las macrozonas y el PDF de tiempos son del Proyecto Integrador I, Equipo 5 (mapa del 6 de octubre de 2026; capturas de Maps del 13 de octubre de 2026), también previos al sprint. El trabajo de este fin de semana es el cruce en `epistemics/studies/commute.py`. La tasa 0.67 de `results/fliprate.json` sigue siendo el demo, no un dato de estudiantes.

## Not this weekend

Si el canal de implementación es una aplicación o un grupo de WhatsApp. El estudio de capitulación sobre ítems de viaje compartido, que era la pregunta anterior de este archivo.
