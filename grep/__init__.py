import os
import re
from typing import Union

from lazyme.string import color_str


class Context(object):

    def __init__(self, context=None, before=None, after=None):
        if (before or after) and context:
            raise ValueError(
                "Context can't be supplied if either 'before' or 'after' are supplied"
            )

        if before is not None and not isinstance(before, int):
            raise TypeError("'before' argument must be an integer")

        if after is not None and not isinstance(after, int):
            raise TypeError("'after' argument must be an integer")

        if context is not None and not isinstance(context, int):
            raise TypeError("'context' argument must be an integer")

        if context:
            self.before = context
            self.after = context

        else:
            self.before = before or 0
            self.after = after or 0


class Pattern(object):

    def __init__(
        self,
        needle,
        invert_match: bool = False,
        ignore_case: bool = False,
        words_only: bool = False,
    ):
        self.needle = needle
        self.invert_match = invert_match
        self.ignore_case = ignore_case
        self.words_only = words_only

    def _flags(self):
        if self.ignore_case:
            return "(?i)"

        return ""

    def __str__(self):
        pattern = f"{self.needle}{self._flags()}"
        if self.words_only:
            pattern = f"(?:\W|^){pattern}(?:\W|$)"

        if self.invert_match:
            pattern = f"^((?!(?:{pattern})).)*$"

        return pattern


class Matches(object):

    def __init__(
        self,
        text: str,
        context: Context,
        pattern: Union[Pattern, str],
        only_matched=False,
        highlight: bool = False,
        number_lines: bool = False,
        zero_based: bool = False,
    ):
        self.text = text
        self.pattern = pattern
        self.context = context
        self.only_matched = only_matched
        self.highlight = highlight
        self.number_lines = number_lines
        self.zero_based = zero_based

    def __iter__(self):
        matching_line_indices = set(self.matching_lines())
        for index, line in enumerate(self.text.splitlines()):
            if index in matching_line_indices:
                yield Match(
                    line,
                    index,
                    number_lines=self.number_lines,
                    zero_based=self.zero_based,
                )

    def matching_lines(self):
        for line_number, line in enumerate(self.text.splitlines()):
            if re.search(str(self.pattern), line):
                yield line_number
                yield from (
                    line_number - i
                    for i in range(1, self.context.before + 1)
                    if line_number - i >= 0
                )
                yield from (
                    line_number + i
                    for i in range(1, self.context.after + 1)
                    if line_number + i < len(self.text)
                )


class Match(object):

    def __init__(self, text, index: int, number_lines: bool, zero_based=False):
        self.text = text
        self.index = index
        self.number_lines = number_lines
        self.zero_based = zero_based

    def __str__(self):
        if not self.zero_based:
            self.index += 1

        if self.number_lines:
            return "%d: %s" % (self.index, self.text)

        return self.text

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return str(self) == other


class grep(object):

    def __init__(
        self,
        pattern,
        *,
        after=None,
        before=None,
        context=None,
        ignore_case=False,
        invert_match=False,
        highlight=True,
        words_only=False,
        number_lines=False,
        separate_matches=False,
        only_matched=False,
        zero_based=False
    ):
        self.context = Context(after=after, before=before, context=context)
        self.pattern = Pattern(pattern, invert_match, ignore_case, words_only)
        self.highlight = highlight
        self.number_lines = number_lines
        self.separate_matches = separate_matches
        self.only_matched = only_matched
        self.zero_based = zero_based

    def __ror__(self, haystack: str):
        matches = Matches(
            haystack,
            self.context,
            self.pattern,
            self.only_matched,
            self.highlight,
            self.number_lines,
            self.zero_based,
        )
        for match in matches:
            return str(match)
