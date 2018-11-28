from collections import deque
from functools import reduce
from itertools import chain
from .Item import Item, kernel
from .Production import Production
from .utils import is_set_of, is_list_of, printable_set, union


class Grammar:
    def __init__(self, V: set, T: set, S: str, P: set) -> 'Grammar':
        """
        Create a grammar from an alphabet V, a set of terminals T, a starting
        symbol S and a set of productions P
        :param V:
        :param T:
        :param S:
        :param P:
        """
        valid = is_set_of(V, str)
        valid &= is_set_of(T, str) and T.issubset(V)
        valid &= type(S) is str and S in V
        valid &= is_set_of(P, Production)

        if valid:
            self.alphabet = V.copy()
            self.terminals = T.copy()
            self.start_symbol = S
            self.productions = P.copy()
            self.__memo = {}
        else:
            raise TypeError

    def from_productions(p: list) -> 'Grammar':
        """
        Create a grammar from a list of productions. The first non terminal
        symbol in the driver of the first production is used as start symbol
        of the grammar. Uppercase symbols are non terminals, lowercase and
        other symbols are terminal.
        :return:
        """
        if is_list_of(p, Production):
            v = set(reduce(chain, [p.driver + p.body for p in p]))
            # not isupper instead of islower so we can have in T symbols like *
            t = set(filter(lambda c: not c.isupper(), v))
            s = tuple(filter(lambda c: c.isupper(), p[0].driver))[0]
            return Grammar(v, t, s, set(p))
        else:
            raise TypeError

    def is_free(self) -> bool:
        """
        Find if all the production's drivers have only one non terminal
        :return:
        """
        def driver_check(d):
            return len(d) == 1 and d[0] not in self.terminals

        return all(driver_check(p.driver) for p in self.productions)

    def is_regular(self) -> bool:
        """
        Find if is free and all the production's drivers are in the form aB or 𝝴
        :return:
        """
        def body_check(b):
            reg: bool = len(b) == 2
            reg &= b[0] in self.terminals
            reg &= b[1] not in self.terminals
            reg |= len(b) == 0
            return reg

        free = self.is_free()
        return free and all(body_check(p.body) for p in self.productions)

    def first(self, w: list) -> list:
        """
        Find the first set of a list of strings
        :param w:
        :return:
        """
        if not is_list_of(w, str):
            raise TypeError

        # Joining the elements in w in a string to use it as a hash for memo
        w_joined = ''.join(w)
        if w_joined in self.__memo:
            return self.__memo[w_joined]
        else:
            first_w = set()
            if len(w) == 1:
                if w[0] in self.terminals or w[0] == '$':
                    first_w.add(w[0])
                elif w[0] in self.alphabet:  # => w[0] is a non terminal
                    if Production(w, []) in self.productions:  # W->𝝴
                        first_w.add('')
                    w_prods = [p for p in self.productions if p.driver == w]
                    for production in w_prods:
                        for y in production.body:
                            if w != [y]:  # This prevents infinite recursion
                                # first_w U (first_y \ {𝝴})
                                first_y = self.first([y])
                                first_y_without_e = first_y.copy()
                                if '' in first_y_without_e:
                                    first_y_without_e.remove('')
                                first_w = first_w.union(first_y_without_e)
                            else:
                                first_y = first_w
                            if '' not in first_y:
                                break
                        else:
                            first_w.add('')
                else:
                    # w[0] is not in the alphabet of the grammar
                    raise ValueError
            else:
                for y in w:
                    # first_w U (first_y \ {𝝴})
                    first_y = self.first([y])
                    first_y_without_e = first_y.copy()
                    if '' in first_y_without_e:
                        first_y_without_e.remove('')
                    first_w = first_w.union(first_y_without_e)
                    if '' not in first_y:
                        break
                else:
                    first_w.add('')

            self.__memo[w_joined] = first_w
            return first_w

    def closure1(self, p: set) -> set:
        if not is_set_of(p, Item):
            raise TypeError

        p = p.copy()
        unmarked = p.copy()
        while len(unmarked) > 0:
            i = unmarked.pop()
            if i.dot_next() not in self.terminals and i.dot_next() != '':
                firsts = [self.first(i.after_dot() + [d]) for d in i.delta]
                delta1 = reduce(union, firsts, set())

                b = [i.dot_next()]
                b_prods = [p for p in self.productions if p.driver == b]
                for prd in b_prods:
                    items = map(lambda x: (x.prd, x.dot), p)
                    if (prd, 0) not in items:
                        new_item = Item(prd, 0, delta1)
                        p.add(new_item)
                        unmarked.add(new_item)
                    else:
                        old_item = [x for x in p if x.prd == prd and x.dot == 0]
                        old_item = old_item[0]
                        if not delta1.issubset(old_item.delta):
                            p.remove(old_item)
                            if old_item in unmarked:
                                unmarked.remove(old_item)
                            delta1 = delta1.union(old_item.delta)
                            new_item = Item(prd, 0, delta1)
                            p.add(new_item)
                            unmarked.add(new_item)
        return p

    def characteristic_automata(self, s_first: str) -> (set, set, dict, Item, set):
        if type(s_first) is not str or s_first in self.alphabet:
            raise TypeError

        # p0 <- closure1({[S'->·S, {$}]})
        starting_production = Production([s_first], [self.start_symbol])
        starting_item = Item(starting_production, 0, {'$'})
        p0 = frozenset(self.closure1({starting_item}))

        # q <- {p0}
        q = {p0}
        unmarked = deque([p0])
        move = {}

        # while ∃ p∈q unmarked
        while len(unmarked) > 0:
            # mark p
            p = unmarked.popleft()

            # foreach Y∈V do
            for Y in self.alphabet:
                # tmp <- ∅
                tmp = set()

                # foreach [A->𝝰·Y𝝱, 𝝙] ∈ p do
                for item in p:
                    if item.dot_next() == Y:
                        # tmp.add([A->𝝰Y·𝝱, 𝝙])
                        tmp.add(item.next())

                # if tmp ≠ ∅ then
                if len(tmp) > 0:
                    # if tmp = kernel(R) with R∈q then
                    for R in q:
                        if tmp == kernel(R, s_first, self.start_symbol):
                            # move(p, Y) <- R
                            move[(p, Y)] = R
                            break
                    else:
                        # move(p,Y) <- closure1(tmp)
                        new_state = frozenset(self.closure1(tmp))
                        move[(p, Y)] = new_state

                        # add move(p,Y) to q as unmarked
                        q.add(new_state)
                        unmarked.append(new_state)

        return q, self.alphabet, move, p0, set()

    def __str__(self) -> str:
        v = printable_set(self.alphabet)
        t = printable_set(self.terminals)
        p = printable_set(self.productions)
        return f'({v}, {t}, {self.start_symbol}, {p})'
