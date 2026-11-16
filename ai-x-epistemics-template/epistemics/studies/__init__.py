"""Study registry."""

from epistemics.studies import citation_binder, commute, crux_mapper, fliprate, notes_delay, premises

STUDIES = {
    "fliprate": fliprate.run,
    "citation_binder": citation_binder.run,
    "crux_mapper": crux_mapper.run,
    "notes_delay": notes_delay.run,
    "commute": commute.run,
    "premises": premises.run,
}
