from cultadapt.eval_metrics import content_similarity, lexical_shift, stereotype_risk, target_culture_signal


def test_content_similarity_bounds():
    s = content_similarity("hello world", "hello")
    assert 0.0 <= s <= 1.0


def test_lexical_shift_bounds():
    s = lexical_shift("A B C", "A B D")
    assert 0.0 <= s <= 1.0


def test_stereotype_risk_detects_pattern():
    r = stereotype_risk("All people from X are backward")
    assert r > 0


def test_target_signal_non_negative():
    source = {"foods": ["paratha"], "names": ["Rohan"], "festivals": ["Diwali"], "places": ["Delhi"]}
    target = {"foods": ["idli"], "names": ["Arun"], "festivals": ["Pongal"], "places": ["Chennai"]}
    t = target_culture_signal("Arun eats idli in Chennai during Pongal.", source, target)
    assert 0.0 <= t <= 1.0
