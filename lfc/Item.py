from .Production import Production
from .utils import is_set_of, printable_set, is_frozenset_of
import re


class Item:
    @property
    def production(self) -> Production:
        return self._prd

    @production.setter
    def production(self, value: Production):
        if type(value) is not Production:
            raise TypeError('production should be a Production object')

        self._prd = value.copy()

    @property
    def marker_position(self) -> int:
        return self._dot

    @marker_position.setter
    def marker_position(self, value: int):
        if type(value) is not int:
            raise TypeError('marker_position should be an integer')

        if not 0 <= value <= len(self.production.body):
            raise ValueError('marker_position is not between 0 and the length of the production body')

        self._dot = value

    @property
    def lookahead(self):
        return self._delta

    @lookahead.setter
    def lookahead(self, value):
        if not is_set_of(value, str):
            raise TypeError('lookahead should be a set of strings')

        self._delta = value.copy()

    def __init__(self, production: Production, marker_position: int, lookahead: set) -> 'Item':
        """
        Create an LR(1)-item from a _prd, the marker's position in the
        production's body and the lookahead set
        :param production:
        :param marker_position:
        :param lookahead_set:
        """
        self.production = production
        self.marker_position = marker_position
        self.lookahead = lookahead

    def from_text(text: str) -> 'Item':
        """
        Create an LR(1)-item from a string in this format:
        [driver->body_with_marker, {list_of_strings}]
        :return:
        """
        error = 'text should be a string in this format [S->a.b, {$, b}]'

        if type(text) is not str:
            raise TypeError(error)

        matched = re.match(r'\[ *(.*)->(.*)\.(.*) *, *{((?: *.* *,?)*)}\]', text)
        if not matched:
            raise ValueError(error)

        driver, fst_body, snd_body, lookahead = matched.group(1, 2, 3, 4)

        # Creates the Production object
        len_of_after_marker = len(snd_body)  # need this for later
        production_text = f'{driver}->{fst_body}{snd_body}'
        prd = Production.from_text(production_text)

        # Calculate the marker_position
        marker = len(prd.body) - len_of_after_marker

        # Creates the lookahead set
        lookahead = lookahead.split(',')
        lookahead = filter(lambda c: c != '', lookahead)
        lookahead = map(lambda c: c.strip(), lookahead)
        lookahead = set(lookahead)

        return Item(prd, marker, lookahead)

    def next_to_marker(self) -> str:
        """
        Get the string in the body right after the marker
        :return:
        """
        empty = self._dot >= len(self._prd.body)
        return self._prd.body[self._dot] if not empty else ''

    def after_marker(self) -> list:
        """
        Get a list of strings after the string right after the marker
        :return:
        """
        return self._prd.body[self._dot + 1:]

    def initial(self, s_first: str, s: str) -> bool:
        """
        Find if the item is the initial one, [S'->·S, {$}]
        :param s_first: The new starting symbol used for the creation of the
        automate
        :param s: The original starting symbol
        :return: True if the item is the initial one, False otherwise
        """
        res = self._prd == Production([s_first], [s])
        res &= self._dot == 0
        res &= self._delta == {'$'}
        return res

    def final(self, s_first: str, s: str) -> bool:
        """
        Find if the item is the final one, [S'->S·, {$}]
        :param s_first: The new starting symbol used for the creation of the
        automate
        :param s: The original starting symbol
        :return: True if the item is the final one, False otherwise
        """
        res = self._prd == Production([s_first], [s])
        res &= self._dot == 1
        res &= self._delta == {'$'}
        return res

    def kernel(self, s_first: str, s: str) -> bool:
        """
        Find if the item is a kernel item, initial or [A->𝝰·𝝱,𝝙] with 𝝰≠𝝴
        :param s_first: The new starting symbol used for the creation of the
        automate
        :param s: The original starting symbol
        :return: True if the item is a kernel item
        """
        return self.initial(s_first, s) or self._dot > 0

    def closure(self, s_first: str, s: str) -> bool:
        """
        Find if the item is a closure item, so not a kernel one
        :param s_first: The new starting symbol used for the creation of the
        automate
        :param s: The original starting symbol
        :return: True if the item is a closure item
        """
        return not self.kernel(s_first, s)

    def reduction(self, s_first: str, s: str) -> bool:
        """
        Find if the item is a reduction item, 𝝱=𝝴 and not final
        :param s_first: The new starting symbol used for the creation of the
        automate
        :param s: The original starting symbol
        :return: True if the item is a reduction item
        """
        return self._dot >= len(self._prd.body) and not self.final(s_first, s)

    def next(self) -> 'Item':
        """
        Get the item with the marker moved by one element.
        [A->𝝰·B𝝱,𝝙].next() => [A->𝝰B·𝝱,𝝙]
        :return:
        """
        if self._dot >= len(self._prd.body):
            raise ValueError('item is a reduction or final')

        return Item(self._prd, self._dot + 1, self._delta)

    def __str__(self) -> str:
        driver = ''.join(self._prd.driver)
        body = self._prd.body[:self._dot] + ['·'] + self._prd.body[self._dot:]
        delta = printable_set(self._delta)
        return f'[{driver}->{"".join(body)}, {delta}]'

    def __eq__(self, other) -> bool:
        res = self._prd == other._prd
        res &= self._dot == other._dot
        res &= self._delta == other._delta
        return res

    def __lt__(self, other: 'Item') -> bool:
        return self.__str__() < other.__str__()

    def __hash__(self) -> int:
        return self.__str__().__hash__()


def kernel(q: set, s_first: str, s: str) -> set:
    """
    Get the kernel items out of a set of Item
    :param q: The set of items
    :param s_first: The new starting symbol used for the creation of the
    automate
    :param s: The original starting symbol
    :return:
    """
    if not (is_set_of(q, Item) or is_frozenset_of(q, Item)):
        raise TypeError('q should be a set or a frozenset of Item')

    return set(filter(lambda i: i.kernel(s_first, s), q))
