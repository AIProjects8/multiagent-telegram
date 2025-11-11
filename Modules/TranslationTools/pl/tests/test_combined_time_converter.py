#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from ..converter import convert

class TestCombinedTimeConverter:
    @pytest.mark.parametrize("input_text,expected", [
        (
            "Spotkanie od godziny 09:00 do 17:30. Przerwa o 12:00. Spotkamy się o 15:45.",
            "Spotkanie od godziny dziewiątej do siedemnastej trzydzieści. Przerwa o dwunastej. Spotkamy się o piętnastej czterdzieści pięć."
        ),
        (
            "Początek o 00:00, koniec o 23:59",
            "Początek o północy, koniec o dwudziestej trzeciej pięćdziesiąt dziewięć"
        ),
        (
            "Harmonogram: 08:00 śniadanie, od godziny 09:00 praca, 12:00 obiad, 17:00 koniec",
            "Harmonogram: ósma śniadanie, od godziny dziewiątej praca, dwunasta obiad, siedemnasta koniec"
        )
    ])
    def test_combined_time_conversions(self, input_text, expected):
        actual = convert(input_text)
        assert actual == expected, f"Expected '{expected}' for input '{input_text}', but got '{actual}'"

    def test_complex_mixed_text(self):
        complex_text = "Dzisiaj od godziny 00:00 do 23:59. Spotkanie o 15:30. Przerwa o 12:00. Koniec o 18:45."
        expected = "Dzisiaj od północy do dwudziestej trzeciej pięćdziesiąt dziewięć. Spotkanie o piętnastej trzydzieści. Przerwa o dwunastej. Koniec o osiemnastej czterdzieści pięć."
        result = convert(complex_text)
        assert result == expected

    def test_no_time_patterns(self):
        text_without_time = "To jest zwykły tekst bez formatów czasowych."
        result = convert(text_without_time)
        assert result == text_without_time

    @pytest.mark.parametrize("input_text,expected", [
        ("", ""),
        ("   ", "   "),
        ("00:00", "północ"),
        ("od godziny 00:00", "od północy")
    ])
    def test_edge_cases(self, input_text, expected):
        actual = convert(input_text)
        assert actual == expected, f"Expected '{expected}' for input '{input_text}', but got '{actual}'"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
