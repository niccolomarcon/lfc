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

    def first(self, X: list) -> list:
        """
        Find the first set of a list of strings
        :param X:
        :return:
        """
        if not is_list_of(X, str):
            raise TypeError

        # Joining the elements in X in a string to use it as a hash for memo
        X_joined = ''.join(X)
        if X_joined in self.__memo:
            return self.__memo[X_joined]
        else:
            first_X = set()

            # if |X| = 1
            if len(X) == 1:
                # if X∈T then
                X = X[0]
                if X in self.terminals or X == '$':
                    # first(X) <- {X}
                    first_X = {X}
                # if X∈V∖T then
                elif X in self.alphabet:
                    # first(X) <- ∅
                    first_X = set()

                    # if X->𝝴 ∈ P then
                    if Production([X], []) in self.productions:
                        # 𝝴 ∈ first(X)
                        first_X.add('')

                    # foreach X->Y1...Yn ∈ P with n≥1 do
                    def X_filter(p):
                        return p.driver == [X] and len(p.body) > 0

                    X_productions = filter(X_filter, self.productions)
                    for p in X_productions:
                        # j <- 1
                        # while j ≤ n do
                        for Y in p.body:
                            # first(X) <- first(X) ∪ (first(Yj) ∖ {𝝴})
                            if X != Y:
                                first_Y = self.first([Y])
                                first_X = first_X.union(first_Y.difference({''}))
                            else:
                                first_Y = first_X

                            # if 𝝴 ∈ first(Yj) then
                            if '' in first_Y:
                                # j <- j + 1 then
                                pass
                            # else
                            else:
                                # break
                                break
                        # if j = n + 1 then
                        else:
                            # 𝝴 ∈ first(X)
                            first_X.add('')
            # else
            elif len(X) > 1:
                # j <- 1
                # while j ≤ n where n = |X| do
                for Y in X:
                    # first(X) <- first(X) ∪ (first(Yj) ∖ {𝝴})
                    first_Y = self.first([Y])
                    first_X = first_X.union(first_Y.difference({''}))

                    # if 𝝴 ∈ first(Yj) then
                    if '' in first_Y:
                        # j <- j + 1 then
                        pass
                    # else
                    else:
                        # break
                        break
                # if j = n + 1 then
                else:
                    # 𝝴 ∈ first(X)
                    first_X.add('')

            self.__memo[X_joined] = first_X
            return first_X

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

    def bottom_up_parsing_table(self, s_first: str, automata=None) -> list:
        if automata is None:
            Q, V, move, s0, F = self.characteristic_automata(s_first)
        else:
            Q, V, move, s0, F = automata
        states_list = [s0] + list(Q.difference({s0}))
        conversion_table = {state: i for i, state in enumerate(states_list)}

        PT = [{} for _ in states_list]

        def add(P, Y, op):
            if Y not in PT[conversion_table[P]]:
                PT[conversion_table[P]][Y] = []
            if op not in PT[conversion_table[P]][Y]:
                PT[conversion_table[P]][Y].append(op)

        for P in Q:
            for Y in V.union({'$'}):
                if Y in self.terminals and (P, Y) in move and move[(P, Y)] in Q:
                    add(P, Y, ('SHIFT', conversion_table[move[(P, Y)]]))
                if any(item.reduction(s_first, self.start_symbol) for item in P):
                    for item in filter(lambda i: i.reduction(s_first, self.start_symbol), P):
                        for X in item.delta:
                            add(P, X, ('REDUCE', item.prd))
                if any(item.final(s_first, self.start_symbol) for item in P):
                    add(P, '$', ('ACCEPT', ''))
                if Y not in self.terminals and (P, Y) in move and move[(P, Y)] in Q:
                    add(P, Y, ('GOTO', conversion_table[move[(P, Y)]]))

        return PT

    def shift_reduce(self, T, input):
        # c <- get_next_char(input_stack)
        input_stack = iter(input)
        c = next(input_stack)

        # state_stack.push(0)
        state_stack = [0]
        symbol_stack = []
        production_stack = []

        while True:
            if len(state_stack) == 0 or c not in T[state_stack[-1]]:
                return []
            op, arg = T[state_stack[-1]][c]
            if op == 'SHIFT':  # T[state_stack.top(), c] == shift Q
                symbol_stack.append(c)
                state_stack.append(arg)
                c = next(input_stack)
            elif op == 'REDUCE':  # T[state_stack.top(), c] == reduce A->𝝱
                A = arg.driver[0]
                beta = arg.body

                # for i ∈ [1...|𝝱|] do
                for i in range(len(beta)):
                    symbol_stack.pop()
                    state_stack.pop()

                symbol_stack.append(A)
                # state_stack.push(T[state_stack.top(), A])
                if len(state_stack) == 0 or A not in T[state_stack[-1]]:
                    return []
                goto, state = T[state_stack[-1]][A]
                if goto == 'GOTO':
                    state_stack.append(state)
                    # print(A->𝝱)
                    production_stack.append(arg)
                else:
                    return []
            elif op == 'ACCEPT':
                break
            else:
                return []

        return production_stack

    def __str__(self) -> str:
        v = printable_set(self.alphabet)
        t = printable_set(self.terminals)
        p = printable_set(self.productions)
        return f'({v}, {t}, {self.start_symbol}, {p})'
