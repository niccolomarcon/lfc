from context import lfc


def test_is_collection_of():
    list_of_strings = ['a', 'b', 'c']
    list_of_multiple_type = [1, 'a', []]
    empty_list = []
    not_a_list = {}

    assert lfc.is_collection_of(list_of_strings, list, str)
    assert not lfc.is_collection_of(list_of_multiple_type, list, int)
    assert lfc.is_collection_of(empty_list, list, int)
    assert not lfc.is_collection_of(not_a_list, list, int)
