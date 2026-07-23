"""Repair malformed JSON emitted by small local models.

Two failure modes observed repeatedly on live idril runs, in
otherwise-good model output:

1. Multi-line string values with literal, unescaped control characters
   (newlines, tabs) instead of ``\\n``/``\\t`` - invalid JSON, but the
   content itself is fine once the escaping is fixed.
2. Extra text before/after the JSON object: markdown code fences, a
   sentence of preamble, or a stray trailing brace.

Both are fixed by a single character scan: find the first ``{``,
track brace depth outside of string literals to find its matching
``}`` (discarding anything before or after), and escape raw control
characters found inside string literals along the way.
"""


def repair_and_extract_json(text: str) -> str:
    """Extract and repair the first top-level JSON object in text.

    Args:
        text: Raw model output that should contain a JSON object,
            possibly with surrounding prose/markdown or unescaped
            control characters inside string values.

    Returns:
        A string containing just the repaired JSON object.

    Raises:
        ValueError: No ``{`` found, or the object is never closed.
    """
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in text")

    depth = 0
    in_string = False
    escape = False
    end = None
    out: list[str] = []

    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                out.append(ch)
                escape = False
            elif ch == "\\":
                out.append(ch)
                escape = True
            elif ch == '"':
                in_string = False
                out.append(ch)
            elif ch == "\n":
                out.append("\\n")
            elif ch == "\r":
                out.append("\\r")
            elif ch == "\t":
                out.append("\\t")
            else:
                out.append(ch)
            continue

        out.append(ch)
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    if end is None:
        raise ValueError("Unterminated JSON object in text")
    return "".join(out)
