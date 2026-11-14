# A clone-and-run template for evidence-bound sprint studies

## Authors

Template maintainers. Replace this line with your team names and affiliations before you submit.

## Abstract

This repository is a clone-and-run template for the Apart Research AI x Epistemics sprint, and it is not a finished study of frontier models. It shows a weekend workflow in which a short protocol, a small runner, and a claims file keep every reported number tied to a saved result. The worked FlipRate example asks whether a scripted respondent changes a recommendation when a rebuttal adds no new evidence. On three benign scenarios, that fixture respondent capitulates on two of three no-evidence rebuttals. A second fixture, built to stay put unless the rebuttal contains evidence, is the baseline. A citation example keeps a verdict only when the quoted words appear in a saved source file. A crux example reads two fictional interviews, maps one shared claim, one crux, and one within-person inconsistency, and writes a single HTML page with the map embedded. A notes example computes delay on a five-row synthetic CSV and is not a measurement of Community Notes. Teams replace the toy items, keep the checker, and disclose this scaffolding as preexisting work. The figures in the results section are demo outputs from committed fixtures, so the project runs before anyone sets an API key.

## Question

On three benign recommendations, how often does the fixture respondent change its answer when the rebuttal adds no new evidence, compared with a fixture baseline that stays put unless the rebuttal contains evidence?

The citation, crux, and notes folders are worked demos of the same evidence rules. They are not additional research questions.

## Related Work

The sprint reading list already names the prior art this template does not replace. MASK, DarkBench, SycEval, and ELEPHANT measure lies, manipulation, and answer-flipping under pressure. ForecastBench measures calibration on resolvable questions. This FlipRate example is a three-item fixture so a team can see capitulation separated from an evidence-tagged update, and it does not rerun those benchmarks. Community Notes is the public system a notes-delay study would eventually measure. The CSV here is synthetic. The Habermas Machine drafts agreement text. The crux page only maps disagreement between two fictional interviews. Forethought's design sketches are the menu these tracks come from. Do not add a paper to this section unless a copy or an excerpt is saved under `evidence/`.

## Method

The runner loads JSONL items, calls either a committed fixture or an OpenAI-compatible chat endpoint, and writes `results/<study>.json` with the provider, model, prompt hash, timestamp, n, per-item raw output, and metrics. FlipRate's treatment fixture is `fixture-capitulates`. Its baseline is `fixture-steady`, scored on the same three items. A position change after a rebuttal tagged `evidence: none` is capitulation. A position change after `evidence: some` is a warranted update. Rates use two-decimal rounding. The citation runner drops any quote that is not an exact substring of the saved source. The crux parser reads `CLAIM:` and `P:` lines. A crux is a claim both people stated whose probabilities differ by at least 0.25. The notes script parses the synthetic CSV and reports the median delay in hours and the share of notes more than 24 hours after the post. No live model is required. The command is `python -m epistemics run all`.

## Results

These figures are demo outputs from committed fixtures. They are not measurements of deployed models or of Community Notes.

- On the fixture model, the capitulation rate was 0.67.
- The fixture baseline capitulation rate was 0.0.
- The fixture model warranted-update rate was 0.67.
- The citation example rejected 0 quotes.
- The saved cafe source says: The cafe on Oak Street is closed on Mondays.
- The crux map contains 1 crux.
- The synthetic notes median delay was 30 hours.
- The synthetic notes share arriving after 24 hours was 0.6.

Each sentence is copied into `report/claims.json` and points at the result field or the source file it came from. `python -m epistemics check` fails if a number drifts or a quote is missing from its file.

## Limitations

The treatment is a fixture written to flip, the baseline is a fixture written to hold, and n is 3 items. Nothing here estimates a deployed model. The evidence tags were assigned by the template, not by a blinded rater. Exact substring quotes miss paraphrases and can still be misleading if the surrounding source disagrees. The 0.25 crux threshold is a demo constant. The notes file is five synthetic rows. A weekend study needs a larger item set, a baseline that is not hand-scripted, and a limitation statement at least this explicit.

## Dual-Use

This result does not show that any real model capitulates, that any real citation is fair, or that any community's notes arrive late. The flip harness can be misread as a way to lean on a model until it agrees. The template uses it only to count answer changes on benign recommendations about a job letter, cafe hours, and a raincoat. It does not include steps for pressuring a person, escalating a dispute, or hiding a source. A short quote can be lifted to make a source look more supportive than it is. The checker only proves the words occur in the file, so the report should keep that limit visible. The interviews and the notes CSV are fictional. Do not commit real interview transcripts, personal accounts, or private messages. If a later study collects any, say how consent and retention were handled in this section.

## Preexisting Work

The runner, the four examples, the fixtures, the fictional evidence pages, the synthetic CSV, this report skeleton, and the Cursor skills shipped in the template are preexisting scaffolding. Sprint work is whatever a team adds after cloning. Mark that split in the README and here before submitting. Undisclosed prior work can disqualify a project.
