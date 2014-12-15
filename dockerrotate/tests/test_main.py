from nose.tools import eq_

from dockerrotate.main import normalize_tag_name


def test_normalize_tag_name():
    CASES = [
        ("some.domain.com/organization/image:tag", "organization/image"),
        ("organization/image:tag", "organization/image"),
        ("image:tag", "image"),
    ]
    for tag, expected in CASES:
        yield eq_, expected, normalize_tag_name(tag)
