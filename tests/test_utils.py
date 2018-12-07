from context import lfc
import pytest


# is_collection_of tests
def test_is_collection_of_array_of_strings():
    list_of_strings = ['a', 'b', 'c']
    assert lfc.is_collection_of(list_of_strings, list, str)


def test_is_collection_of_array_of_different_objects():
    list_of_multiple_type = [1, 'a', []]
    assert not lfc.is_collection_of(list_of_multiple_type, list, int)
    assert not lfc.is_collection_of(list_of_multiple_type, list, str)
    assert not lfc.is_collection_of(list_of_multiple_type, list, list)


def test_is_collection_of_empty_array():
    empty_list = []
    assert lfc.is_collection_of(empty_list, list, int)


def test_is_collection_of_not_a_list():
    not_a_list = {}
    assert not lfc.is_collection_of(not_a_list, list, int)


def test_is_collection_of_collection_not_passed():
    with pytest.raises(TypeError) as excinfo:
        lfc.is_collection_of(c=set, t=int)
    assert 'is_collection_of() missing 1 required positional argument: \'x\'' in str(excinfo.value)


def test_is_collection_of_collection_type_not_passed():
    with pytest.raises(TypeError) as excinfo:
        lfc.is_collection_of(x=[], t=int)
    assert 'is_collection_of() missing 1 required positional argument: \'c\'' in str(excinfo.value)


def test_is_collection_of_element_type_not_passed():
    with pytest.raises(TypeError) as excinfo:
        lfc.is_collection_of(x=[], c=set)
    assert 'is_collection_of() missing 1 required positional argument: \'t\'' in str(excinfo.value)


# printable_set tests
def test_printable_set_valid():
    text = lfc.printable_set({1, 'a', 3.14})
    assert '1' in text
    assert 'a' in text
    assert '3.14' in text
    assert text[0] == '{'
    assert text[-1] == '}'
    assert len(text.split(', ')) == 3


def test_printable_set_frozen_set():
    text = lfc.printable_set(frozenset([1, 2, 3]))
    assert '1' in text
    assert '2' in text
    assert '3' in text
    assert text[0] == '{'
    assert text[-1] == '}'
    assert len(text.split(', ')) == 3


def test_printable_set_empty_set():
    assert lfc.printable_set(set()) == '∅'


def test_printable_set_missing_set():
    with pytest.raises(TypeError) as excinfo:
        lfc.printable_set()
    assert 'printable_set() missing 1 required positional argument: \'x\'' in str(excinfo.value)


def test_printable_set_not_a_set():
    with pytest.raises(TypeError) as excinfo:
        lfc.printable_set([1, 2, 3])
    assert 'x should be a set or a frozenset' in str(excinfo.value)