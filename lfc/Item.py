from .Production import Production
from .utils import is_set_of, printable_set, is_frozenset_of


class Item:
    def __init__(self, production: Production, marker_position: int, lookahead_set: set) -> 'Item':
        """
        Create an LR(1)-item from a production, the marker's position in the
        production's body and the lookahead set
        :param production:
        :param marker_position:
        :param lookahead_set:
        """
        valid: bool = type(production) is Production
        valid &= type(marker_position) is int
        valid &= 0 <= marker_position <= len(production.body)
        valid &= is_set_of(lookahead_set, str)

        if valid:
            self.prd: Production = production.copy()
            self.dot: int = marker_position
            self.delta: set = lookahead_set.copy()
        else:
            raise TypeError

    def from_text(text: str) -> 'Item':
        """
        Create an LR(1)-item from a string in this format:
        [driver->body_with_marker, {list_of_string}]
        :return:
        """
        pass

    def __str__(self) -> str:
        driver = ''.join(self.prd.driver)
        body = self.prd.body[:self.dot] + ['·'] + self.prd.body[self.dot:]
        delta = printable_set(sorted(self.delta))
        return f'[{driver}->{"".join(body)}, {delta}]'

    def dot_next(self) -> str:
        """
        Get the string in the body right after the marker
        :return:
        """
        if self.dot < len(self.prd.body):
            return self.prd.body[self.dot]
        else:
            return ''

    def after_dot(self) -> list:
        """
        Get a list of strings after the string right after the marker
        :return:
        """
        return self.prd.body[self.dot + 1:]

    def initial(self, s_first: str, s: str) -> bool:
        """
        Find if the item is the initial one, [S'->·S, {$}]
        :param s_first:
        :param s:
        :return:
        """
        res = self.prd == Production([s_first], [s])
        res &= self.dot == 0
        res &= self.delta == {'$'}
        return res

    def final(self, s_first: str, s: str) -> bool:
        """
        Find if the item is the final one, [S'->S·, {$}]
        :param s_first:
        :param s:
        :return:
        """
        res = self.prd == Production([s_first], [s])
        res &= self.dot == 1
        res &= self.delta == {'$'}
        return res

    def kernel(self, s_first: str, s: str) -> bool:
        """
        Find if the item is a kernel item, initial or [A->𝝰·𝝱,𝝙] with 𝝰≠𝝴
        :param s_first:
        :param s:
        :return:
        """
        return self.initial(s_first, s) or self.dot > 0

    def closure(self, s_first: str, s: str) -> bool:
        """
        Find if the item is a closure item, so not a kernel one
        :param s_first:
        :param s:
        :return:
        """
        return not self.kernel(s_first, s)

    def reduction(self, s_first: str, s: str) -> bool:
        """
        Find if the item is a reduction item, 𝝱=𝝴 and not final
        :param s_first:
        :param s:
        :return:
        """
        return len(self.after_dot()) == 0 and not self.final(s_first, s)

    def next(self) -> 'Item':
        """
        Get the item with the marker moved by one element.
        [A->𝝰·B𝝱,𝝙].next() => [A->𝝰B·𝝱,𝝙]
        :return:
        """
        return Item(self.prd, self.dot + 1, self.delta)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        res = self.prd == other.prd
        res &= self.dot == other.dot
        res &= self.delta == other.delta
        return res

    def __lt__(self, other: 'Item') -> bool:
        return self.__str__() < other.__str__()

    def __hash__(self) -> int:
        return self.__str__().__hash__()


def kernel(q: set, s_first: str, s: str) -> set:
    """
    Get the kernel items out of a set of Item
    :param q:
    :param s_first:
    :param s:
    :return:
    """
    if not (is_set_of(q, Item) or is_frozenset_of(q, Item)):
        raise TypeError
    return set(filter(lambda i: i.kernel(s_first, s), q))
