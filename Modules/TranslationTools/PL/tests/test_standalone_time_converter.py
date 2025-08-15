#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from ..standalone_time_converter import convert_standalone_time

class TestStandaloneTimeConverter:
    @pytest.mark.parametrize("input_text,expected", [
        ("00:00", "północ"),
        ("00:15", "piętnaście po północy"),
        ("01:12", "pierwsza dwanaście"),
        ("23:59", "dwudziesta trzecia pięćdziesiąt dziewięć"),
        ("16:11", "szesnasta jedenaście"),
        ("20:05", "dwudziesta zero pięć"),
        ("00:09", "zero dziewięć po północy"),
        ("00:32", "trzydzieści dwa po północy"),
        ("00:56", "pięćdziesiąt sześć po północy"),
        ("12:09", "dwunasta zero dziewięć"),
        ("01:00", "pierwsza"),
        ("12:00", "dwunasta"),
        ("24:00", "24")
    ])
    def test_standalone_time_conversions(self, input_text, expected):
        actual = convert_standalone_time(input_text)
        assert actual == expected, f"Expected '{expected}' for input '{input_text}', but got '{actual}'"

    @pytest.mark.parametrize("input_text,expected", [
        ("00:01", "zero jeden po północy"),
        ("00:10", "dziesięć po północy"),
        ("00:30", "trzydzieści po północy"),
        ("00:45", "czterdzieści pięć po północy")
    ])
    def test_midnight_cases(self, input_text, expected):
        actual = convert_standalone_time(input_text)
        assert actual == expected, f"Expected '{expected}' for input '{input_text}', but got '{actual}'"

    @pytest.mark.parametrize("input_text,expected", [
        ("01:01", "pierwsza zero jeden"),
        ("02:02", "druga zero dwa"),
        ("10:05", "dziesiąta zero pięć"),
        ("23:09", "dwudziesta trzecia zero dziewięć")
    ])
    def test_leading_zero_minutes(self, input_text, expected):
        actual = convert_standalone_time(input_text)
        assert actual == expected, f"Expected '{expected}' for input '{input_text}', but got '{actual}'"

    def test_no_time_patterns(self):
        text_without_time = "To jest zwykły tekst bez formatów czasowych."
        result = convert_standalone_time(text_without_time)
        assert result == text_without_time

    def test_mixed_text(self):
        mixed_text = "Spotkanie o 15:30 i 16:45, przerwa o 12:00."
        expected = "Spotkanie o piętnasta trzydzieści i szesnasta czterdzieści pięć, przerwa o dwunasta."
        result = convert_standalone_time(mixed_text)
        assert result == expected

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
