#!/usr/bin/env python

from pandocfilters import toJSONFilter, RawBlock
from pygments import highlight
from pygments.lexers import Lean4Lexer
from pygments.formatters import HtmlFormatter
import subprocess


def pygments(key, value, format, meta):
    if key == "CodeBlock":
        [[ident, classes, keyvals], code] = value
        if any("lean4" in s for s in classes):
            lexer = Lean4Lexer()
            formatter = HtmlFormatter(
                style="default",
                noclasses=True,
                wrapcode=True,
            )
            return RawBlock("html", highlight(code, lexer, formatter))


if __name__ == "__main__":
    toJSONFilter(pygments)
