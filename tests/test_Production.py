from context import lfc


class TestProduction():
    def test_base_constructor(self):
        driver = ['S']
        body = ['a', 'S', 'b']
        production = lfc.Production(driver=driver, body=body)
        assert driver == production.driver
        assert body == production.body
        assert driver is not production.driver
        assert body is not production.body

    def test_from_text(self):
        text = 'S->aSb'
        production = lfc.Production.from_text(text)
        assert production.driver == ['S']
        assert production.body == ['a', 'S', 'b']

        text = 'Ab->'
        production = lfc.Production.from_text(text)
        assert production.driver == ['A', 'b']
        assert not production.body

    def test_str(self):
        text = 'S->aSb'
        production = lfc.Production.from_text(text)
        assert text == production.__str__()

        text = 'Ab->'
        production = lfc.Production.from_text(text)
        assert text + '𝜀' == production.__str__()