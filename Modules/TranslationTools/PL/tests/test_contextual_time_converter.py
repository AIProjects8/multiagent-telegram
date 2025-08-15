#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from ..contextual_time_converter import convert_contextual_time

class TestContextualTimeConverter:
    @pytest.mark.parametrize("input_text,expected", [
        ("od godziny 12:00", "od godziny dwunastej"),
        ("od 15:30", "od piętnastej trzydzieści"),
        ("do godziny 23:45", "do godziny dwudziestej trzeciej czterdzieści pięć"),
        ("o godzinie 00:00", "o północy"),
        ("o 08:15", "o ósmej piętnaście"),
        ("od 00:00", "od północy"),
        ("do 00:00", "do północy"),
        ("o 00:00", "o północy"),
        ("od godziny 01:00", "od godziny pierwszej"),
        ("do godziny 24:00", "do godziny 24")
    ])
    def test_contextual_time_conversions(self, input_text, expected):
        actual = convert_contextual_time(input_text)
        assert actual == expected, f"Expected '{expected}' for input '{input_text}', but got '{actual}'"

    def test_no_time_patterns(self):
        text_without_time = "To jest zwykły tekst bez formatów czasowych."
        result = convert_contextual_time(text_without_time)
        assert result == text_without_time

    def test_mixed_text(self):
        mixed_text = "Spotkanie od godziny 09:00 do 17:30. Przerwa o 12:00."
        expected = "Spotkanie od godziny dziewiątej do siedemnastej trzydzieści. Przerwa o dwunastej."
        result = convert_contextual_time(mixed_text)
        assert result == expected

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
