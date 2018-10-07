from itertools import combinations
from ScrapingPolicy import ScrapingPolicy

root = 'http://gateway.x-plane.com'
policy = ScrapingPolicy(root)

def test_canonicalize():
    """canonicalize() should choose a single representation for equivalent URLs"""
    for pair in combinations(['/foo', '/foo/', '/foo/index.html', f"{root}/foo", f"{root}/foo/", f"{root}/foo/index.html"], 2):
        assert policy.canonicalize(pair[0]) == policy.canonicalize(pair[1])
    assert f"{root}/foo/bar.jpg" == policy.canonicalize('/foo/bar.jpg')

def test_outdir():
    assert policy.out_directory == 'gateway.x-plane.com'
