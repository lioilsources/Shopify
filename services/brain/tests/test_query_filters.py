from brain.query_filters import extract

SCHEMAS = [
    ("hodi_se_na", "Hodí se na", ["Hrnek", "Obal na mobil", "Plakát", "Tričko", "Podložka pod myš"]),
    ("orientace", "Orientace", ["na výšku", "na šířku", "čtverec"]),
    ("styl", "Styl", ["watercolor", "anime"]),
    ("pomer_stran", "Poměr stran", ["3:4", "16:9"]),
]


def test_use_case_style_and_rest():
    ext = extract("liška akvarel na hrnek", SCHEMAS)
    assert ext.filters == {"styl": ["watercolor"], "hodi_se_na": ["Hrnek"]}
    assert ext.rest == "liska na"
    assert [m.label for m in ext.matches] == ["Styl", "Hodí se na"]


def test_inflected_and_accentless():
    assert extract("chci plakaty s dinosaury", SCHEMAS).filters == {"hodi_se_na": ["Plakát"]}
    assert extract("něco na hrnky", SCHEMAS).filters == {"hodi_se_na": ["Hrnek"]}


def test_orientation_phrases_do_not_mix():
    assert extract("krajina na výšku", SCHEMAS).filters == {"orientace": ["na výšku"]}
    assert extract("nalezato", SCHEMAS).filters == {"orientace": ["na šířku"]}


def test_synonyms_need_the_value_in_schema():
    assert extract("kryt na mobil", SCHEMAS).filters == {"hodi_se_na": ["Obal na mobil"]}
    assert extract("triko s kočkou", SCHEMAS).filters == {"hodi_se_na": ["Tričko"]}
    # "kresba" has no value in this catalogue: stays as text.
    ext = extract("kresba", SCHEMAS)
    assert ext.filters == {} and ext.rest == "kresba"


def test_ratio_matches_exactly():
    assert extract("formát 3:4", SCHEMAS).filters == {"pomer_stran": ["3:4"]}
    assert extract("3 4", SCHEMAS).filters == {}


def test_short_words_alone_never_match():
    assert extract("pes na zahradě", SCHEMAS).filters == {}


def test_multiword_value_beats_partial():
    ext = extract("podložka pod myš s liškou", SCHEMAS)
    assert ext.filters == {"hodi_se_na": ["Podložka pod myš"]}


def test_category_word_scopes_search():
    cats = [("krajiny", "Krajiny a příroda"), ("plysaci", "Plyšáci a hračky")]
    ext = extract("krajina na plakát", SCHEMAS, cats)
    assert ext.category == "krajiny" and ext.filters == {"hodi_se_na": ["Plakát"]}
    assert ext.rest == "na"
    assert extract("plyšáka", SCHEMAS, cats).category == "plysaci"
    assert extract("příroda", SCHEMAS, cats).category is None
