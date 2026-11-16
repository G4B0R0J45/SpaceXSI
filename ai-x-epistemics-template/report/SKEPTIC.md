# Skeptic note

This note is about the commute count in `results/commute.json`. It does not edit the results. Every number here is copied from that file or from `results/commute_first_submission.json`.

## What would flip the conclusion

The majority claim. The share who said yes was 0.62, and the lower end of its 95% interval was 0.55. That interval covers sampling noise only. The sample is whoever answered the form, and 124 of the 260 are in cuatrimestre 0. If the students who did not answer are less willing, the claim about UPY students fails while the claim about respondents stands. A yes on a form is also not a trip. If enough of the yes answers would not show up, the share of real users is below half.

The coverage claim. 15 does not reach 145 one for one. Nobody proposes one passenger per car. With an assumed number of free seats the comparison moves, and the survey has no column for free seats, days driven, or the route a car takes.

The zone claim. The share outside Z06 is between 0.42 and 0.70. It settles only when the 73 rows without a zone are placed.

## Weaker points

- The zone rule changed after the data was seen. Reading "alta (punto OSM)" as high certainty moved the lower bound from 0.39 to 0.42. The change is disclosed, and it was still made after looking.
- 11 rows mention Caucel or its postal code and are not placed in Z06. Z06 is undercounted by some part of that number. The run does no fuzzy matching.
- 28 rows chose another municipality. Z99 mixes municipalities at very different distances from campus, so it cannot be read as far or as near.
- The arrival question asks about arriving after 07:00. It does not ask whether class started at 07:00. The 0.75 share is not a lateness rate.
- The form collected no identifier, so the count cannot rule out one student answering twice.
- The study does not call a model. It says nothing about how a model reasons, so a judge who scores impact for AI and epistemics can fairly call it off topic.
- The raw survey was in the public repository until 15 November 2026. A row joins term, program, neighborhood, and an optional sex field. It is now kept by the team, and only aggregate counts are published.

## What still stands

160 of 260 respondents said yes, and that is a majority of respondents. The own-car yes answers are few, 15, on any reading of the zone join. Each sentence in the report's result lists points at a saved number through `report/claims.json`, and `python -m epistemics check` passes.
