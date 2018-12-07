def is_collection_of(x: object, c: type, t: type) -> bool:
    """
    Controls if an object is a collection of a specific type
    :param x: The object to control
    :param c: The type of the collection
    :param t: The type of the objects inside the collection
    :return: True if all the objects inside of the collection are the same type
    that's been specified
    """
    return type(x) is c and all(map(lambda a: type(a) is t, x))


def is_set_of(x: object, t: type) -> bool:
    """
    Controls if an object is a set of a specific type
    :param x: The object to control
    :param t: The type all items should be
    :return: True if all the items in the set are the specified type
    """
    return is_collection_of(x, set, t)


def is_frozenset_of(x: object, t: type) -> bool:
    """
    Controls if an object is a frozenset of a specific type
    :param x: The object to control
    :param t: The type all items should be
    :return: True if all the items in the frozenset are the specified type
    """
    return is_collection_of(x, frozenset, t)


def is_list_of(x: object, t: type) -> bool:
    """
    Controls if an object is a list of a specific type
    :param x: The object to control
    :param t: The type all items should be
    :return: True if all the items in the list are the specified type
    """
    return is_collection_of(x, list, t)


def printable_set(x: set) -> str:
    """
    Return a string that represents the set
    :param x: The set we want to stringify
    :return: The set in text form
    """
    if type(x) not in [set, frozenset]:
        raise TypeError('x should be a set or a frozenset')

    return '{' + ', '.join(a.__str__() for a in x) + '}' if len(x) > 0 else '∅'


def union(x: set, y: set) -> set:
    return x.union(y)
