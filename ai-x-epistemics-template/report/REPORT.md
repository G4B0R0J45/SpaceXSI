# Would UPY students use a morning meeting point?

## Authors

Gabriel Rojas, Universidad Politécnica de Yucatán.

## Abstract

This open-track study asks whether students who accepted a morning-commute survey at the Universidad Politécnica de Yucatán would use a nearby meeting point to share that ride, and whether yes answers from students who drive their own car cover, one for one, yes answers from students who do not. The respondents are students in cuatrimestre 0 or the third cuatrimestre, not the whole university. The count reads the saved survey and does not call a model. In the consenting sample, n was 260. The share who said they would use a meeting point was 0.62. The lower end of the 95% Wilson interval for that share was 0.55. That is above the majority threshold of 0.5. The share who answered maybe was 0.28. The count with their own car who said yes was 15. The count without their own car who said yes was 145. So 15 does not reach 145. The same run joins rows to a preexisting macrozone. The share placed outside Z06, over the full consenting sample, was 0.42. If every row without a zone were outside Z06, the share outside Z06 would be 0.70. A claim that most respondents live outside Z06 is therefore undetermined on this sample. This result does not show that a meeting point would operate or that a car has empty seats. The survey and the zone tables are preexisting; the sprint work is the join.

## Question

Among students who accepted the morning-commute survey for the Universidad Politécnica de Yucatán campus, what share say they would use a meeting point to share the ride, and how many of those yes answers come from students who drive their own car?

The protocol also tests two falsifiers on the same run. A majority claim is true only if the share is above the saved baseline of 0.5. Own-car yes answers cover other yes answers, one for one, only if the own-car yes count reaches the yes count from every other mode. The protocol wrote a third test, on whether most of the sample is outside zone Z06, as one threshold on the full consenting sample. This version reports that test as a range, because a row without a zone stays in the denominator and cannot be counted on either side. Z06 is Caucel and the outer west. Z99 is another municipality and is not counted as outside. Empty seats are not a column in the survey.

## Related Work

The sprint reading list already names the prior art this study does not replace. MASK, DarkBench, SycEval, and ELEPHANT measure lies, manipulation, and answer-flipping under pressure. ForecastBench measures calibration on resolvable questions. Community Notes is a public notes system. The Habermas Machine drafts agreement text. Forethought's design sketches are the menu the sprint tracks come from. This study does not rerun those benchmarks and does not call a model. The local sources are the files under `evidence/`. `evidence/encuesta-traslado-upy.md` saves the survey questions this count uses. `evidence/macrozonas-upy.md` saves the zone table and the one-day travel-time note. No other paper is cited, because no other paper is saved in this repository.

## Method

The command is `python -m epistemics run commute`. The runner reads `study/sources/encuesta_traslado_upy.csv`. A row stays in the sample when the acceptance cell is exactly "Sí, acepto" and the term cell does not say the survey is not for that person. The written prompt in the result file is the rule list. A yes is the meeting-point answer "Sí". A maybe is "Tal vez" and a no is "No". Own car is the mode "Auto propio". Bus or combi is a mode that starts with "Camión". Driven by someone else is a mode that starts with "Me llevan en auto". A day after 07:00 last week is an integer of at least 1. A usual arrival after 07:00 is a clock time strictly later than 07:00. Rates use the template ratio helper and two-decimal rounding. The interval for the willing share is a Wilson 95% interval, rounded the same way.

Zone assignment uses the first rule that fires. A normalized neighborhood that matches one high-certainty zone is that zone, unless the postal code is also high-certainty, at least 0.95 in a different zone, in which case the row is a conflict and gets no zone. Otherwise a high-certainty postal code at or above 0.95 assigns its zone. Otherwise Umán is Z11, Kanasín is Z12, and another municipality is Z99. Anything else is unassigned. A neighborhood marked for review does not assign a zone. The PDF times are not copied onto rows. The runner writes `results/commute.json` with provider `survey`, model `commute-counter`, n, and the metrics. It does not multiply drivers by an assumed seat count.

One rule changed after the first submitted version. The neighborhood catalog labels some rows "alta (punto OSM)". The first run read only the exact label "alta" as high certainty, so those neighborhoods, Las Américas among them, got no zone. This version reads any label that starts with "alta" as high certainty. The first result file is kept as `results/commute_first_submission.json`. In the first submitted version, the share placed outside Z06 was 0.39. In that version, the share outside Z06 among placed rows was 0.56. No other rule changed. The unit tests for the join are in `tests/test_commute.py` and use synthetic rows.

## Results

These figures are the commute count in `results/commute.json`. They are not fixture output and they are not a measurement of a deployed model.

Sample.

- In the consenting sample, n was 260.
- The count in cuatrimestre 0 was 124.
- The count in the third cuatrimestre was 136.
- The first saved response timestamp was 2026-11-06T09:00.
- The last saved response timestamp was 2026-11-13T16:30.

Meeting point.

- The saved survey asks: Si hubiera un punto de encuentro cerca de donde sales para compartir el traslado con otros estudiantes de la UPY, ¿lo usarías?
- The share who said they would use a meeting point was 0.62.
- The count who said yes was 160.
- The lower end of the 95% Wilson interval for that share was 0.55.
- The upper end of that interval was 0.67.
- The baseline threshold for a majority claim was 0.5.
- The share who answered maybe was 0.28.
- The count who answered maybe was 73.
- The share who answered no was 0.10.
- The count who answered no was 27.

Cars and modes.

- The count with their own car who said yes was 15.
- The count without their own car who said yes was 145.
- The count who usually take a bus or combi and said yes was 86.
- The count who are usually driven by someone else and said yes was 38.
- The share who usually drive their own car was 0.11.
- The share who usually take a bus or combi was 0.48.

Arrival.

- The share who arrived after 07:00 on at least one day last week was 0.75.
- The share whose usual arrival is after 07:00 was 0.33.

Zones.

- The count placed in Z06 was 78.
- The share placed in Z06 was 0.30.
- The count placed outside Z06 was 109.
- The share placed outside Z06, over the full consenting sample, was 0.42.
- The count placed in a zone from Z01 to Z12 was 187.
- Among placed rows, the share outside Z06 was 0.58.
- The count with no zone from Z01 to Z12 was 73.
- The share with no zone from Z01 to Z12 was 0.28.
- The count who chose another municipality was 28.
- The count with no usable neighborhood or postal code was 42.
- If every row without a zone were outside Z06, the share outside Z06 would be 0.70.
- The count of rows not placed in Z06 that mention Caucel or its postal code was 11.
- The count in Z06 with their own car who said yes was 6.
- The count in Z06 without their own car who said yes was 40.
- The saved zone note says: Es una muestra de un solo día, un punto por zona y horarios programados por Maps (no tiempo real).

On this sample, 0.62 is above 0.5, and so is the lower end of the interval, 0.55, so a majority of consenting respondents said they would use a meeting point. A further 0.28 answered maybe, and this report does not count them as yes. The count 15 does not reach 145, so own-car yes answers do not cover the other yes answers one for one. Most of those 145 already have a way to get to campus: 86 usually take a bus or combi and 38 are usually driven by someone else. The zone test does not settle. The share outside Z06 is at least 0.42 and at most 0.70, and 0.5 sits inside that range, so this sample cannot say whether most respondents are outside Z06. Z06 is the largest single zone, with 78 rows, and its placed share, 0.30, is not a majority. The Z06 pair is 6 and 40, so the same coverage gap appears inside that zone. Each sentence in the lists above is copied into `report/claims.json`.

## Limitations

The respondents are real students who accepted the survey, not fixtures and not a live model. They are students in cuatrimestre 0 or the third cuatrimestre. The last term option on the form reads: 6.º cuatrimestre u otro (la encuesta no es para ti; gracias). The sample is whoever answered, so the shares describe respondents and not enrollment. The metric is what they said they would do, not a trip that happened. The survey never asks how many seats are free, so multiplying drivers by four seats would be an assumption this run does not make. The survey asks on how many days a student arrived after 07:00. It does not ask whether the first class that day was at 07:00, or why the arrival was after 07:00, so 0.75 is not a rate of lateness caused by transport. Rows with no zone stay in the full-sample denominator, which is why the outside-Z06 share is a range and not one number. Neighborhood matching misses spellings, and the Caucel count in the Results section is the visible part of that. A respondent who chose another municipality and then wrote Caucel stays in Z99. A postal code is optional. The zone rule changed once after the first submission, as the Method section says. The saved zone note says: Es una muestra de un solo día, un punto por zona y horarios programados por Maps (no tiempo real). Those times are not assigned to people. Collection started before the sprint and ended on its first day.

## Dual-Use

This result does not show that a meeting point would run, that students would keep showing up, or that any model should tell them to. A share of 0.62 can be quoted to make a proposal sound more settled than a stated intention on one campus survey. The count 15 against 145 can be quoted to argue that drivers are too few, or the reverse, without the denominator. The report keeps both numbers and the baseline of 0.5 in the same section so a short quote is harder to lift alone. The zone range can be quoted from either end, so the report prints both ends together. The zone note is one day and one point per zone. Lifting a travel time as if it were a student's morning would overstate the file. This study does not include steps for pressuring a student, organizing a group, or hiding a source. The survey asked for acceptance before the other questions. The saved file records neighborhood, an optional postal code, and an optional sex field. The published metrics do not list a person, a neighborhood, or that sex field. The raw CSV was in the public repository until 15 November 2026. It is now kept by the team, and only aggregate counts are published.

## Preexisting Work

The runner, the four examples, the fixtures, the fictional evidence pages, the synthetic notes CSV, and the Cursor skills shipped with the template are preexisting scaffolding. `results/fliprate.json` remains that template demo and is not a student measurement. The survey is prior team work: the first saved response is dated 6 November 2026, and the sprint starts on 13 November 2026. The macrozones, the map, and the travel-time PDF are from Proyecto Integrador I, Equipo 5, also before this sprint. The sprint work is the join in `epistemics/studies/commute.py`, its tests in `tests/test_commute.py`, and this report.
