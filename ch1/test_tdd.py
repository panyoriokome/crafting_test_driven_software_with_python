class TestAddition():
    def test_main(self):
        result = addition(3, 2)
        assert result == 5

    def test_threeargs(self):
        result = addition(3, 2, 1)
        assert result == 6

    def test_noargs(self):
        result = addition()
        assert result == 0

def addition(*args):
    a1, a2 = args
    return a1 + a2
