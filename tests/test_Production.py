from context import lfc
import pytest


class TestProduction:
    # __init__ tests
    def test_init_valid(self):
        driver = ['S']
        body = ['a', 'S', 'b']
        production = lfc.Production(driver=driver, body=body)
        assert driver == production.driver
        assert body == production.body

    def test_init_driver_not_passed(self):
        with pytest.raises(TypeError) as excinfo:
            body = ['a', 'S', 'b']
            production = lfc.Production(body=body)
        assert '__init__() missing 1 required positional argument: \'driver\'' in str(excinfo.value)

    def test_init_body_not_passed(self):
        with pytest.raises(TypeError) as excinfo:
            driver = ['a', 'S', 'b']
            production = lfc.Production(driver=driver)
        assert '__init__() missing 1 required positional argument: \'body\'' in str(excinfo.value)

    def test_init_driver_is_empty_list(self):
        driver = []
        body = ['a', 'b']
        with pytest.raises(ValueError) as excinfo:
            production = lfc.Production(driver, body)
        assert 'driver is empty' in str(excinfo.value)

    def test_init_body_is_empty_list(self):
        driver = ['S']
        body = []
        production = lfc.Production(driver, body)
        assert production.driver == driver
        assert production.body == body

    def test_init_driver_is_not_a_list_of_strings(self):
        driver = ['S', 1, False]
        body = ['a', 'b']
        with pytest.raises(TypeError) as excinfo:
            production = lfc.Production(driver, body)
        assert 'driver is not a list of strings' in str(excinfo.value)

    def test_init_body_is_not_a_list_of_strings(self):
        driver = ['a', 'b']
        body = ['S', 1, False]
        with pytest.raises(TypeError) as excinfo:
            production = lfc.Production(driver, body)
        assert 'body is not a list of strings' in str(excinfo.value)

    def test_init_driver_is_string(self):
        driver = 'aS'
        body = ['b', 'a']
        with pytest.raises(TypeError) as excinfo:
            production = lfc.Production(driver, body)
        assert 'driver is not a list of strings' in str(excinfo.value)

    def test_init_body_is_string(self):
        driver = ['b', 'a']
        body = 'aS'
        with pytest.raises(TypeError) as excinfo:
            production = lfc.Production(driver, body)
        assert 'body is not a list of strings' in str(excinfo.value)

    def test_init_driver_is_none(self):
        driver = None
        body = ['a', 'b']
        with pytest.raises(TypeError) as excinfo:
            production = lfc.Production(driver, body)
        assert 'driver is not a list of strings' in str(excinfo.value)

    def test_init_body_is_none(self):
        driver = ['S']
        body = None
        with pytest.raises(TypeError) as excinfo:
            production = lfc.Production(driver, body)
        assert 'body is not a list of strings' in str(excinfo.value)

    # from_text tests
    def test_from_text_valid(self):
        text = 'S->aSb'
        production = lfc.Production.from_text(text)
        assert production.driver == ['S']
        assert production.body == ['a', 'S', 'b']

    def test_from_text_with_empty_body(self):
        text = 'Ab->'
        production = lfc.Production.from_text(text)
        assert production.driver == ['A', 'b']
        assert production.body == []

    def test_from_text_with_empty_driver(self):
        with pytest.raises(ValueError) as excinfo:
            text = '->ab'
            production = lfc.Production.from_text(text)
        assert 'driver is empty' in str(excinfo.value)

    def test_from_text_no_arrow(self):
        with pytest.raises(ValueError) as excinfo:
            text = 'justatest'
            production = lfc.Production.from_text(text)
        assert 'no arrow (->) in production text' in str(excinfo.value)

    def test_from_text_too_many_arrows(self):
        with pytest.raises(ValueError) as excinfo:
            text = 'A->B->C'
            production = lfc.Production.from_text(text)
        assert 'too many arrows (->) in production text' in str(excinfo.value)

    def test_from_text_text_is_strings_array(self):
        with pytest.raises(TypeError) as excinfo:
            text = ['a', 'b']
            production = lfc.Production.from_text(text)
        assert 'text is not a string' in str(excinfo.value)

    def test_from_text_text_is_not_string(self):
        with pytest.raises(TypeError) as excinfo:
            text = 5
            production = lfc.Production.from_text(text)
        assert 'text is not a string' in str(excinfo.value)

    def test_from_text_no_value(self):
        with pytest.raises(TypeError) as excinfo:
            production = lfc.Production.from_text()
        assert 'from_text() missing 1 required positional argument: \'text\'' in str(excinfo.value)

    # copy tests
    def test_copy_same(self):
        production = lfc.Production(['S'], ['a'])
        copied = production.copy()
        assert production.driver == copied.driver
        assert copied.body == copied.body
        assert production.driver is not copied.driver
        assert production.body is not copied.body
        assert production is not copied

    def test_copy_modified(self):
        production = lfc.Production(['S'], ['a'])
        copied = production.copy()
        production.driver = ['A']
        production.body = ['s']
        assert production.driver != copied.driver
        assert production.body != copied.body

    # __str__ tests
    def test_str_valid(self):
        text = 'S->aSb'
        production = lfc.Production.from_text(text)
        assert text == production.__str__()

    def test_str_empty_body(self):
        text = 'Ab->'
        production = lfc.Production.from_text(text)
        assert text + '𝜀' == production.__str__()

    # __eq__ tests
    def test_eq_between_same_class(self):
        a = lfc.Production.from_text('S->aSb')
        b = lfc.Production.from_text('S->aSb')
        c = lfc.Production.from_text('S->ab')
        assert a == b
        assert a != c
        assert b != c
        assert b.__eq__(a)
        assert not c.__eq__(a)
        assert not c.__eq__(b)

    def test_eq_between_somethin_else(self):
        production = lfc.Production.from_text('S->as')
        a = 8
        assert not production.__eq__(a)
        assert not production == a