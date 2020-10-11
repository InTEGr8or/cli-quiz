import click
import cliqz

def test_always_true():
    assert True

def test_search():
    search_results = cliqz.search
    print("search_results: " ,search_results)
    assert(cliqz.search)

def test_look_up():
    assert(cliqz.look_up)

def test_other():
    assert(cliqz.take)
