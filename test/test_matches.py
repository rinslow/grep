from grep import Matches, Context


def test_sanity():
    matches = Matches(
        """A
B
C
D
A
B
C
D""",
        Context(),
        "A",
    )

    assert tuple(matches) == ("A", "A")


def test_line_numbering():
    matches = Matches(
        """A
B
C
D
A
B
C
D""",
        Context(),
        "A",
        number_lines=True,
    )

    assert tuple(matches) == ("1: A", "5: A")


def test_before():
    matches = Matches(
        """A
B
C
D
A
B
C
D""",
        Context(before=1),
        "A",
        number_lines=True,
    )

    assert set(matches.matching_lines()) == {0, 4, 3}


def test_after():
    matches = Matches(
        """A
B
C
D
A
B
C
D""",
        Context(after=1),
        "A",
        number_lines=True,
    )

    assert set(matches.matching_lines()) == {0, 1, 4, 5}


def test_context():
    matches = Matches(
        """A
    B
    C
    D
    A
    B
    C
    D""",
        Context(context=2),
        "A",
        number_lines=True,
    )

    assert set(matches.matching_lines()) == {0, 1, 2, 3, 4, 5, 6}
