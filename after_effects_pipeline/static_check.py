from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

CODE_BLOCK_PATTERN = re.compile(r"```(?:jsx|javascript|js)?\s*(.*?)```", re.DOTALL)

FORBIDDEN_API_PATTERNS = [
    "fetch(",
    "XMLHttpRequest",
    "eval(",
    "app.quit(",
    "system.callSystem",
    "Socket(",
]


@dataclass
class StaticCheck:
    syntax_ok: bool
    ae_contract_ok: bool
    issues: list[str] = field(default_factory=list)
    signals: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.syntax_ok and self.ae_contract_ok and not self.issues


def extract_code(text: str) -> str:
    match = CODE_BLOCK_PATTERN.search(text)
    return match.group(1).strip() if match else text.strip()


def analyze_static_jsx(code: str, expected: dict[str, Any] | None = None) -> StaticCheck:
    expected = expected or {}
    issues: list[str] = []
    balance_issues = _balance_issues(code)
    issues.extend(balance_issues)
    forbidden_hits = [item for item in FORBIDDEN_API_PATTERNS if item in code]
    for hit in forbidden_hits:
        issues.append(f"forbidden API pattern: {hit}")

    signals = {
        "has_begin_undo": "app.beginUndoGroup(" in code,
        "has_end_undo": "app.endUndoGroup(" in code,
        "creates_comp": ".items.addComp(" in code or "items.addComp(" in code,
        "sets_values": ".setValue(" in code,
        "sets_keyframes": ".setValueAtTime(" in code,
        "uses_expressions": ".expression" in code,
        "has_error_handling": "try" in code and "catch" in code,
        "forbidden_hits": forbidden_hits,
    }
    comp_name = expected.get("comp_name")
    if comp_name:
        signals["mentions_expected_comp"] = comp_name in code
    contract_ok = (
        signals["has_begin_undo"]
        and signals["has_end_undo"]
        and signals["creates_comp"]
        and signals.get("mentions_expected_comp", True)
    )
    if not signals["has_begin_undo"]:
        issues.append("missing app.beginUndoGroup")
    if not signals["has_end_undo"]:
        issues.append("missing app.endUndoGroup")
    if not signals["creates_comp"]:
        issues.append("does not create a composition")
    if comp_name and comp_name not in code:
        issues.append(f"does not mention expected comp name: {comp_name}")

    return StaticCheck(
        syntax_ok=not balance_issues and not forbidden_hits,
        ae_contract_ok=contract_ok,
        issues=issues,
        signals=signals,
    )


def _balance_issues(code: str) -> list[str]:
    pairs = {"(": ")", "[": "]", "{": "}"}
    closers = {value: key for key, value in pairs.items()}
    stack: list[tuple[str, int]] = []
    state = "code"
    escape = False
    issues: list[str] = []
    for index, char in enumerate(code):
        nxt = code[index + 1] if index + 1 < len(code) else ""
        if state in {"single", "double"}:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif (state == "single" and char == "'") or (
                state == "double" and char == '"'
            ):
                state = "code"
            continue
        if state == "line_comment":
            if char == "\n":
                state = "code"
            continue
        if state == "block_comment":
            if char == "*" and nxt == "/":
                state = "code"
            continue
        if char == "'":
            state = "single"
        elif char == '"':
            state = "double"
        elif char == "/" and nxt == "/":
            state = "line_comment"
        elif char == "/" and nxt == "*":
            state = "block_comment"
        elif char in pairs:
            stack.append((char, index))
        elif char in closers:
            if not stack or stack[-1][0] != closers[char]:
                issues.append(f"unmatched closing delimiter {char} at {index}")
            else:
                stack.pop()
    for opener, index in stack[-5:]:
        issues.append(f"unclosed delimiter {opener} at {index}")
    if state in {"single", "double", "block_comment"}:
        issues.append(f"unterminated {state}")
    return issues

