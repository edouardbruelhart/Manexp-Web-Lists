"""Tests for taxa/color_generator/text_to_color.py"""

from manexp_web_lists.taxa.color_generator.text_to_color import text_to_color


def test_text_to_color():
    color = text_to_color("test")

    assert color == "#59cc32"
