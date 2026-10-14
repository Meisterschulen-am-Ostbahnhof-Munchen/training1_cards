"""
Normalizes a Markdown file so python-markdown renders it the way GitHub/CommonMark
would, before handing it to render_html.py. Fixes three mismatches between
python-markdown's stricter list/paragraph rules and how these docs are actually
written:

1. A bullet list directly under a lead-in sentence (no blank line between them)
   gets swallowed into that paragraph as literal "- " text instead of becoming
   a list, because python-markdown (unlike GitHub) won't let a list interrupt
   an immediately preceding paragraph without a blank line first.

2. A multi-line bullet of the form "- **Label:** text\\n  more text\\n  ```code```"
   (common in review-style docs: "- **Problem:** ...", "- **Fix:** ..." under a
   finding) often fails to render its fenced code block as a real <pre> at all -
   python-markdown's list-continuation handling is inconsistent about it,
   especially for numbered sub-items nested inside the bullet. Flattening each
   such bullet into a plain "**Label:**" paragraph (dedenting its continuation
   lines) sidesteps the problem entirely and reads just as well in print.

3. Any fenced code block left at a non-zero indentation afterward (e.g. still
   nested under a numbered sub-step) gets normalized to its own fence-marker's
   indentation baseline and wrapped in blank lines, so it always ends up as a
   standalone block instead of leaking into surrounding text as inline code.

Usage: python preprocess_md.py <input.md> <output.md>
"""
import re
import sys

from pathlib import Path
from typing import Union, Optional, Tuple


def _check_fence(line: str, current_fence: Optional[Tuple[str, int]]) -> Optional[Tuple[str, int]]:
    """Tracks opening and closing of fenced code blocks (backticks or tildes).

    - Opening fence: 0-3 leading spaces, 3+ backticks or tildes. If backticks, no backticks in info.
    - Closing fence: 0-3 leading spaces, same character, at least opening length, trailing whitespace only.
    """
    indent = len(line) - len(line.lstrip(" "))
    if indent > 3:
        return current_fence

    stripped = line.strip()
    if current_fence is None:
        m = re.match(r"^(`{3,}|~{3,})", stripped)
        if m:
            marker = m.group(1)
            char = marker[0]
            length = len(marker)
            info = stripped[length:]
            if char == "`" and "`" in info:
                return None
            return (char, length)
        return None
    else:
        char, length = current_fence
        pattern = rf"^{re.escape(char * length)}{re.escape(char)}*\s*$"
        if re.match(pattern, stripped):
            return None
        return current_fence


def preprocess_markdown(src_path: Union[str, Path], out_path: Union[str, Path]) -> None:
    """Normalizes Markdown for python-markdown."""
    with open(src_path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    # --- Fix 1: blank line before a list that directly follows a paragraph ---
    list_item_re = re.compile(r"^(?:-|\d+\.)\s")
    fixed = []
    prev_was_list_item = False
    fence = None
    for line in lines:
        prev_fence = fence
        fence = _check_fence(line, fence)
        if prev_fence is not None or fence is not None:
            fixed.append(line)
            prev_was_list_item = False
            continue
        is_list_item = bool(list_item_re.match(line))
        if is_list_item and not prev_was_list_item and fixed and fixed[-1].strip() != "":
            fixed.append("")
        fixed.append(line)
        if line.strip() != "":
            prev_was_list_item = is_list_item
    lines = fixed

    # --- Fix 2: flatten multi-line "- **Label:** ..." bullets into paragraphs ---
    label_re = re.compile(r"^- \*\*(.+?)\*\*:?\s*(.*)$")

    out = []
    i = 0
    n = len(lines)
    fence = None
    while i < n:
        line = lines[i]
        prev_fence = fence
        fence = _check_fence(line, fence)
        if prev_fence is not None or fence is not None:
            out.append(line)
            i += 1
            continue
        m = label_re.match(line)
        has_continuation = m is not None and (i + 1) < n and lines[i + 1].startswith("  ")
        if m and has_continuation:
            label, rest = m.group(1).rstrip(":"), m.group(2)
            if out and out[-1].strip() != "":
                out.append("")
            out.append(f"**{label}:** {rest}".rstrip())
            out.append("")
            i += 1
            while i < n and (lines[i].startswith("  ") or lines[i].strip() == ""):
                if lines[i].strip() == "":
                    out.append("")
                else:
                    out.append(lines[i][2:])
                i += 1
            continue
        out.append(line)
        i += 1

    text = "\n".join(out)

    # --- Fix 3: normalize any fenced code block still left indented ---
    lines2 = text.split("\n")
    out2 = []
    fence = None
    fence_indent = 0
    for idx, line in enumerate(lines2):
        prev_fence = fence
        fence = _check_fence(line, fence)
        if prev_fence is None and fence is not None:
            # Opening fence
            fence_indent = len(line) - len(line.lstrip(" "))
            if out2 and out2[-1].strip() != "":
                out2.append("")
            out2.append(line[fence_indent:])
        elif prev_fence is not None and fence is None:
            # Closing fence
            out2.append(line[fence_indent:] if line.startswith(" " * fence_indent) else line.lstrip())
            nxt = lines2[idx + 1] if idx + 1 < len(lines2) else ""
            if nxt.strip() != "":
                out2.append("")
        elif fence is not None:
            # Inside fence
            out2.append(line[fence_indent:] if line.startswith(" " * fence_indent) else line)
        else:
            out2.append(line)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out2))
    print("wrote", out_path)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        preprocess_markdown(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python preprocess_md.py <input.md> <output.md>")
        sys.exit(1)
