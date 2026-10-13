from utils.helpers import matches_query


def test_matches_query_true_when_all_words_present():
    assert matches_query("MXR M267 Octavio Fuzz 2020", "mxr octavio") is True


def test_matches_query_false_when_a_word_is_missing():
    assert matches_query("MXR Phase 90", "mxr octavio") is False


def test_matches_query_is_case_insensitive():
    assert matches_query("MXR OCTAVIO", "mxr octavio") is True
