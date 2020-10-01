from context import lfc
import pytest
import re


class TestItem:
    from_text_error = 'text should be a string in this format [S->a.b, {$, b}]'

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
        assert 'marker_position is not between 0 and the length of the production body' in str(excinfo.value)

    def test_init_marker_too_big(self):
        with pytest.raises(ValueError) as excinfo:
            lfc.Item(lfc.Production(['S'], ['a', 'b']), 3, {'$'})
        assert 'marker_position is not between 0 and the length of the production body' in str(excinfo.value)

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

    def test_from_text_text_not_string(self):
        with pytest.raises(TypeError) as excinfo:
            lfc.Item.from_text(8)
        assert self.from_text_error in str(excinfo.value)

    def test_from_text_multiple_items_in_lookahead(self):
        text = '[S->.A, {$, a}]'
        item = lfc.Item.from_text(text)
        assert item.production == lfc.Production(['S'], ['A'])
        assert item.marker_position == 0
        assert item.lookahead == {'$', 'a'}

    def test_from_text_missing_production(self):
        with pytest.raises(ValueError) as excinfo:
            lfc.Item.from_text('[{$}]')
        assert self.from_text_error in str(excinfo.value)

    def test_from_text_missing_lookahead(self):
        with pytest.raises(ValueError) as excinfo:
            lfc.Item.from_text('[S->a.b]')
        assert self.from_text_error in str(excinfo.value)

    def test_from_text_missing_dot(self):
        with pytest.raises(ValueError) as excinfo:
            lfc.Item.from_text('[S->ab, {$}]')
        assert self.from_text_error in str(excinfo.value)

    def test_from_text_empty_lookahead(self):
        item = lfc.Item.from_text('[S->a.b, {}]')
        assert item.production == lfc.Production(['S'], ['a', 'b'])
        assert item.marker_position == 1
        assert len(item.lookahead) == 0

    def test_from_text_empty_body(self):
        item = lfc.Item.from_text('[S->., {$ ,b}]')
        assert item.production == lfc.Production(['S'], [])
        assert item.marker_position == 0
        assert item.lookahead == {'$', 'b'}

    # next_to_marker tests
    def test_next_to_marker_valid(self):
        prd = lfc.Production(['S'], ['a', 'b', 'c'])
        item = lfc.Item(prd, 1, set())
        assert item.next_to_marker() == 'b'

    def test_next_to_marker_begin(self):
        prd = lfc.Production(['S'], ['a', 'b', 'c'])
        item = lfc.Item(prd, 0, set())
        assert item.next_to_marker() == 'a'

    def test_next_to_marker_end(self):
        prd = lfc.Production(['S'], ['a', 'b', 'c'])
        item = lfc.Item(prd, 3, set())
        assert item.next_to_marker() == ''

    def test_next_to_marker_empty_body(self):
        prd = lfc.Production(['S'], [])
        item = lfc.Item(prd, 0, set())
        assert item.next_to_marker() == ''

    # after_marker tests
    def test_after_marker_valid(self):
        prd = lfc.Production(['S'], ['a', 'b', 'c'])
        item = lfc.Item(prd, 0, set())
        assert item.after_marker() == ['b', 'c']

    def test_after_marker_empty_body(self):
        prd = lfc.Production(['S'], [])
        item = lfc.Item(prd, 0, set())
        assert item.after_marker() == []

    def test_after_marker_before_last(self):
        prd = lfc.Production(['S'], ['a', 'b'])
        item = lfc.Item(prd, 1, set())
        assert item.after_marker() == []

    def test_after_marker_end(self):
        prd = lfc.Production(['S'], ['a', 'b'])
        item = lfc.Item(prd, 2, set())
        assert item.after_marker() == []

    # initial tests
    def test_initial_valid_production(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production([s_first], [s])
        item = lfc.Item(prd, 0, {'$'})
        assert item.initial(s_first, s)

    def test_initial_invalid_production(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production(['A'], ['B'])
        item = lfc.Item(prd, 0, {'$'})
        assert not item.initial(s_first, s)

    def test_initial_invalid_marker(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production([s_first], [s])
        item = lfc.Item(prd, 1, {'$'})
        assert not item.initial(s_first, s)

    def test_initial_invalid_lookahead(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production([s_first], [s])
        item = lfc.Item(prd, 0, {'b'})
        assert not item.initial(s_first, s)

    # final tests
    def test_final_valid_production(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production([s_first], [s])
        item = lfc.Item(prd, 1, {'$'})
        assert item.final(s_first, s)

    def test_final_invalid_production(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production(['A'], ['B'])
        item = lfc.Item(prd, 1, {'$'})
        assert not item.final(s_first, s)

    def test_final_invalid_marker(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production([s_first], [s])
        item = lfc.Item(prd, 0, {'$'})
        assert not item.final(s_first, s)

    def test_final_invalid_lookahead(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production([s_first], [s])
        item = lfc.Item(prd, 1, {'b'})
        assert not item.initial(s_first, s)

    # kernel tests
    def test_kernel_final(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production([s_first], [s])
        item = lfc.Item(prd, 1, {'$'})
        assert item.kernel(s_first, s)

    def test_kernel_intial(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production([s_first], [s])
        item = lfc.Item(prd, 0, {'$'})
        assert item.kernel(s_first, s)

    def test_kernel_valid(self):
        prd = lfc.Production(['A'], ['a', 'b', 'c'])
        item = lfc.Item(prd, 1, {'$'})
        assert item.kernel('S', 'A')

    def test_kernel_invalid(self):
        prd = lfc.Production(['A'], ['a', 'b', 'c'])
        item = lfc.Item(prd, 0, {'$'})
        assert not item.kernel('S', 'A')

    def test_kernel_empty_body(self):
        prd = lfc.Production(['A'], [])
        item = lfc.Item(prd, 0, {'$'})
        assert not item.kernel('S', 'A')

    # closure tests
    def test_closure_valid(self):
        prd = lfc.Production(['A'], ['a', 'b', 'c'])
        item = lfc.Item(prd, 0, set())
        assert item.closure('S', 'A')

    def test_closure_invalid(self):
        prd = lfc.Production(['A'], ['a', 'b', 'c'])
        item = lfc.Item(prd, 1, set())
        assert not item.closure('S', 'A')

    def test_closure_empty_body(self):
        prd = lfc.Production(['A'], [])
        item = lfc.Item(prd, 0, set())
        assert item.closure('S', 'A')

    # reduction tests
    def test_reduction_final(self):
        s_first = 'S'
        s = 'A'
        prd = lfc.Production([s_first], [s])
        item = lfc.Item(prd, 1, {'$'})
        assert not item.reduction(s_first, s)

    def test_reduction_invalid(self):
        prd = lfc.Production(['A'], ['a', 'b'])
        item = lfc.Item(prd, 1, set())
        assert not item.reduction('S', 'A')

    def test_reduction_valid(self):
        prd = lfc.Production(['A'], ['a', 'b'])
        item = lfc.Item(prd, 2, set())
        assert item.reduction('S', 'A')

    def test_reduction_empty_body(self):
        prd = lfc.Production(['A'], [])
        item = lfc.Item(prd, 0, set())
        assert item.reduction('S', 'A')

    # next tests
    def test_next_valid(self):
        item = lfc.Item.from_text('[A->.ab, {}]')
        assert item.next() == lfc.Item.from_text('[A->a.b, {}]')

    def test_next_reduction(self):
        with pytest.raises(ValueError) as excinfo:
            item = lfc.Item.from_text('[A->ab., {}]').next()
        assert 'item is a reduction or final' in str(excinfo.value)

    def test_next_empty_body(self):
        with pytest.raises(ValueError) as excinfo:
            item = lfc.Item.from_text('[A->., {}]').next()
        assert 'item is a reduction or final' in str(excinfo.value)

    # str tests
    def test_str_valid(self):
        text = lfc.Item.from_text('[S->a.b, {$, b}]').__str__()
        matched = re.match(r'\[S->a·b, {(\$|b), (\$|b)}\]', text)
        assert matched
        x, y = matched.group(1, 2)
        assert x != y

    def test_str_empty_body(self):
        assert lfc.Item.from_text('[S->., {$}]').__str__() == '[S->·, {$}]'

    def test_str_empty_lookahead(self):
        assert lfc.Item.from_text('[S->.a, {}]').__str__() == '[S->·a, ∅]'

    # eq tests
    def test_eq_same_obj(self):
        prd = lfc.Production.from_text('S->aSb')
        item = lfc.Item(prd, 0, {'$'})
        assert item == item

    def test_eq_valid_different_obj(self):
        prd = lfc.Production.from_text('S->aSb')
        item_a = lfc.Item(prd, 0, {'$'})
        item_b = lfc.Item(prd, 0, {'$'})
        assert item_a == item_b

    def test_eq_different_prd(self):
        prd_a = lfc.Production.from_text('S->aSb')
        prd_b = lfc.Production.from_text('S->ab')
        assert lfc.Item(prd_a, 0, set()) != lfc.Item(prd_b, 0, set())

    def test_eq_different_dot(self):
        prd = lfc.Production.from_text('S->aSb')
        assert lfc.Item(prd, 1, set()) != lfc.Item(prd, 2, set())

    def test_eq_different_delta(self):
        prd = lfc.Production.from_text('S->aSb')
        assert lfc.Item(prd, 1, {'$'}) != lfc.Item(prd, 1, {'b'})


# kernel tests
def tests_kernel_set():
    state = {lfc.Item.from_text('[S->a.Sb, {$}]'),
             lfc.Item.from_text('[S->.aSb, {b}]'),
             lfc.Item.from_text('[S->.ab, {b}]')
             }
    kernel = {lfc.Item.from_text('[S->a.Sb, {$}]')}
    assert lfc.kernel(state, 'A', 'S') == kernel


def tests_kernel_frozenset():
    state = frozenset({lfc.Item.from_text('[S->a.Sb, {$}]'),
                       lfc.Item.from_text('[S->.aSb, {b}]'),
                       lfc.Item.from_text('[S->.ab, {b}]')
                      })
    kernel = {lfc.Item.from_text('[S->a.Sb, {$}]')}
    assert lfc.kernel(state, 'A', 'S') == kernel


def tests_kernel_set_of_numbers():
    with pytest.raises(TypeError) as excinfo:
        lfc.kernel({1, 2, 3}, 'A', 'S')
    assert 'q should be a set or a frozenset of Item' in str(excinfo.value)
