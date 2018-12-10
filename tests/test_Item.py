from context import lfc
import pytest


class TestItem():
    # __init__ tests
    def test_init_valid(self):
        production = lfc.Production(['S'], ['a', 'S', 'b'])
        item = lfc.Item(production, 0, {'$'})
        assert item.production == production
        assert item.marker_position == 0
        assert item.lookahead == {'$'}

    def test_init_production_of_wrong_type(self):
        with pytest.raises(TypeError) as excinfo:
            lfc.Item(8, 0, {'$'})
        assert 'production should be a Production object' in str(excinfo.value)

    def test_init_non_int_marker(self):
        with pytest.raises(TypeError) as excinfo:
            lfc.Item(lfc.Production(['S'], []), 'justates', {'$'})
        assert 'marker_position should be an integer' in str(excinfo.value)

    def test_init_lookahead_set_of_non_strings(self):
        with pytest.raises(TypeError) as excinfo:
            lfc.Item(lfc.Production(['S'], []), 0, {8})
        assert 'lookahead should be a set of strings' in str(excinfo.value)

    def test_init_lookahead_not_a_set(self):
        with pytest.raises(TypeError) as excinfo:
            lfc.Item(lfc.Production(['S'], []), 0, ['$'])
        assert 'lookahead should be a set of strings' in str(excinfo.value)

    def test_init_negative_marker(self):
        with pytest.raises(ValueError) as excinfo:
            lfc.Item(lfc.Production(['S'], ['a', 'b']), -1, {'$'})
        assert 'marker_position is not between 0 and the length of the production body' in str(excinfo)

    def test_init_marker_too_big(self):
        with pytest.raises(ValueError) as excinfo:
            lfc.Item(lfc.Production(['S'], ['a', 'b']), 3, {'$'})
        assert 'marker_position is not between 0 and the length of the production body' in str(excinfo)

    def test_init_missing_production(self):
        with pytest.raises(TypeError) as excinfo:
            lfc.Item(marker_position=0, lookahead={'$'})
        assert '__init__() missing 1 positional argument \'production\''

    def test_init_missing_marker(self):
        with pytest.raises(TypeError) as excinfo:
            lfc.Item(production=lfc.Production(['S'], ['a']), lookahead={'$'})
        assert '__init__() missing 1 positional argument \'marker_position\''

    def test_init_missing_lookahead(self):
        with pytest.raises(TypeError) as excinfo:
            lfc.Item(production=lfc.Production(['S'], ['a']), marker_position=0)
        assert '__init__() missing 1 positional argument \'lookahead\''

    # from_text tests
    def test_from_text_valid(self):
        text = '[S->a.Sb, {$}]'
        item = lfc.Item.from_text(text)
        assert item.production == lfc.Production(['S'], ['a', 'S', 'b'])
        assert item.marker_position == 1
        assert item.lookahead == {'$'}

    def test_from_text_missing_text(self):
        with pytest.raises(TypeError) as excinfo:
            lfc.Item.from_text()
        assert 'from_text() missing 1 positional argument \'text\''

    def test_from_text_text_not_string(self):
        with pytest.raises(TypeError) as excinfo:
            lfc.Item.from_text(8)
        assert 'text should be a string'

    def test_from_text_multiple_items_in_lookahead(self):
        text = '[S->.A, {$, a}]'
        item = lfc.Item.from_text(text)
        assert item.production == lfc.Production(['S'], ['A'])
        assert item.marker_position == 0
        assert item.lookahead == {'$', 'a'}

    def test_from_text_missing_production(self):
        pass

    def test_from_text_missing_lookahead(self):
        pass

    def test_from_text_missing_dot(self):
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
