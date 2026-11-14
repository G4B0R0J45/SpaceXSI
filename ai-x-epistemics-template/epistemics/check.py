"""Submission gate: claims must point at saved results, and the report must have its sections."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from epistemics.run import find_root

REQUIRED_HEADINGS = (
    "question",
    "related work",
    "method",
    "results",
    "limitations",
    "dual-use",
)

HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
WORD = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?")


@dataclass
class CheckResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def check_submission(root: Path | None = None) -> CheckResult:
    root = root or find_root()
    result = CheckResult()
    result.notes.append(
        "Paste the report into the official Apart sprint PDF template before submitting."
    )
    result.notes.append(
        "Label this repository's scaffolding as preexisting work in the report and the README."
    )

    report_path = root / "report" / "REPORT.md"
    claims_path = root / "report" / "claims.json"
    if not report_path.is_file():
        result.errors.append(f"Missing report: {report_path.as_posix()}")
        return result
    report = report_path.read_text(encoding="utf-8")
    sections = split_sections(report)
    for heading in REQUIRED_HEADINGS:
        if not any(name.startswith(heading) for name in sections):
            result.errors.append(f"Report is missing a section heading for {heading}.")

    abstract = section_body(sections, "abstract")
    if abstract is None:
        result.warnings.append("Abstract section is missing. The sprint asks for 150 to 250 words.")
    else:
        count = len(WORD.findall(abstract))
        if count < 150 or count > 250:
            result.warnings.append(
                f"Abstract is {count} words. The sprint asks for 150 to 250 words."
            )

    if "preexisting" not in report.lower():
        result.warnings.append(
            "Report does not mention preexisting work. The sprint requires that disclosure."
        )

    if not claims_path.is_file():
        result.errors.append(f"Missing claims file: {claims_path.as_posix()}")
        return result
    try:
        claims = json.loads(claims_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.errors.append(f"claims.json is not valid JSON: {exc}")
        return result
    if not isinstance(claims, list) or not claims:
        result.errors.append("claims.json must be a non-empty list.")
        return result

    for index, claim in enumerate(claims):
        check_claim(root, report, claim, index, result)
    return result


def check_claim(root: Path, report: str, claim: object, index: int, result: CheckResult) -> None:
    label = f"claims[{index}]"
    if not isinstance(claim, dict):
        result.errors.append(f"{label} is not an object.")
        return
    claim_id = str(claim.get("id") or label)
    text = claim.get("text")
    if not isinstance(text, str) or not text.strip():
        result.errors.append(f"{claim_id}: text is missing.")
    elif text not in report:
        result.errors.append(f"{claim_id}: claim text does not appear in REPORT.md.")

    has_pointer = "source" in claim or "pointer" in claim or "value" in claim
    has_quote = "quote" in claim or "evidence" in claim
    if has_pointer:
        source = claim.get("source")
        pointer = claim.get("pointer")
        if not isinstance(source, str) or not isinstance(pointer, str) or "value" not in claim:
            result.errors.append(f"{claim_id}: source, pointer, and value are required together.")
        else:
            source_path = root / source
            if not source_path.is_file():
                result.errors.append(f"{claim_id}: source file does not exist: {source}")
            else:
                try:
                    document = json.loads(source_path.read_text(encoding="utf-8"))
                    actual = resolve_pointer(document, pointer)
                except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as exc:
                    result.errors.append(f"{claim_id}: cannot read {pointer} from {source} ({exc}).")
                else:
                    if not values_match(claim["value"], actual):
                        result.errors.append(
                            f"{claim_id}: value {claim['value']!r} does not match {source} {pointer} ({actual!r})."
                        )
    if has_quote:
        quote = claim.get("quote")
        evidence = claim.get("evidence")
        if not isinstance(quote, str) or not isinstance(evidence, str):
            result.errors.append(f"{claim_id}: quote and evidence are required together.")
        else:
            evidence_path = root / evidence
            if not evidence_path.is_file():
                result.errors.append(f"{claim_id}: evidence file does not exist: {evidence}")
            else:
                body = evidence_path.read_text(encoding="utf-8")
                if quote not in body:
                    result.errors.append(
                        f"{claim_id}: quote is not an exact substring of {evidence}."
                    )
    if not has_pointer and not has_quote:
        result.errors.append(f"{claim_id}: needs a result pointer or an evidence quote.")


def split_sections(markdown: str) -> dict[str, str]:
    matches = list(HEADING.finditer(markdown))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections[match.group(1).strip().lower()] = markdown[start:end].strip()
    return sections


def section_body(sections: dict[str, str], prefix: str) -> str | None:
    for name, body in sections.items():
        if name.startswith(prefix):
            return body
    return None


def resolve_pointer(document: object, pointer: str) -> object:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ValueError("pointer must be a JSON pointer")
    current = document
    for raw_part in pointer.split("/")[1:]:
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            if part not in current:
                raise KeyError(part)
            current = current[part]
        else:
            raise KeyError(part)
    return current


def values_match(expected: object, actual: object) -> bool:
    if isinstance(expected, bool) or isinstance(actual, bool):
        return expected == actual
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return math.isclose(float(expected), float(actual), rel_tol=0, abs_tol=1e-6)
    return expected == actual


def format_result(result: CheckResult) -> str:
    lines = ["OK" if result.ok else "FAILED"]
    if result.errors:
        lines.append("Errors:")
        lines.extend(f"- {item}" for item in result.errors)
    if result.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {item}" for item in result.warnings)
    if result.notes:
        lines.append("Notes:")
        lines.extend(f"- {item}" for item in result.notes)
    return "\n".join(lines)
