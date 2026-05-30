from solv_scraper.club_match import is_olgsga


def test_olgsga_variants():
    assert is_olgsga("OLG St. Gallen/App.")
    assert is_olgsga("OLG St.Gallen/Appenzell")
    assert is_olgsga("OLG Basel/OLG St. Gallen/App.")
    assert is_olgsga("thurgorienta/OLG St.Gallen/App")
    assert is_olgsga("thurgorienta/OLG St.Gallen-Appenzell")


def test_non_olgsga():
    assert not is_olgsga("OLG Stäfa")
    assert not is_olgsga("OLG Pfäffikon")
    assert not is_olgsga("")
