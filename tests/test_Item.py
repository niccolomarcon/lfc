from context import lfc


class TestItem():
    def test_base_constructor(self):
        driver = ['S']
        body = ['a', 'S', 'b']
        production = lfc.Production(driver=driver, body=body)
        marker = 0
        delta = {'$'}
        item = lfc.Item(production, marker, delta)
        assert item.prd == production
        assert item.dot == marker
        assert item.delta == delta

    def test_from_text(self):
        pass

    def test_str(self):
        pass

    def test_dot_next(self):
        pass

    def test_after_dot(self):
        pass

    def test_initial(self):
        pass

    def test_final(self):
        pass

    def test_kernel(self):
        pass

    def test_closure(self):
        pass

    def test_reduction(self):
        pass

    def test_next(self):
        pass

    def test_repr(self):
        pass

    def test_eq(self):
        pass

    def test_lt(self):
        pass

    def test_hash(self):
        pass
