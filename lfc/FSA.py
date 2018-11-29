from functools import reduce


class FSA:
    def __init__(self, S: set, A: set, move: dict, s0: int, F: set) -> 'FSA':
        # TODO: control the types
        valid = F.issubset(S)
        valid &= s0 in S

        if valid:
            self.states = S.copy()
            self.alphabet = A.copy()
            self.move = move.copy()
            self.initial_state = s0
            self.final_states = F.copy()
        else:
            raise TypeError

    def pipe(self, other: 'FSA') -> 'FSA':
        nfa1, nfa2, n = self.make_compatible(other)
        final_state = n + 1

        # Assemble the states
        s = nfa1.states.union(nfa2.states)
        s.add(0)
        s.add(final_state)

        a = nfa1.alphabet.union(nfa2.alphabet)

        move = nfa1.move.copy()
        for k in nfa2.move:
            move[k] = nfa2.move[k]

        new_nfa = FSA(s, a, move, 0, {final_state})

        new_nfa.add_transition(0, '', nfa1.initial_state)
        new_nfa.add_transition(0, '', nfa2.initial_state)

        nfa1_final_state = list(nfa1.final_states)[0]
        nfa2_final_state = list(nfa2.final_states)[0]
        new_nfa.add_transition(nfa1_final_state, '', final_state)
        new_nfa.add_transition(nfa2_final_state, '', final_state)

        return new_nfa

    def concat(self, other: 'FSA') -> 'FSA':
        nfa1, nfa2, _ = self.make_compatible(other, start_from=0)

        s = nfa1.states.union(nfa2.states)
        a = nfa1.alphabet.union(nfa2.alphabet)

        move = nfa1.move.copy()
        for k in nfa2.move:
            move[k] = nfa2.move[k]

        new_nfa = FSA(s, a, move, nfa1.initial_state, nfa2.final_states)

        # Add an 𝝴-transition between the final state of nfa1 and the initial
        # state of nfa2
        nfa1_final_state = list(nfa1.final_states)[0]
        new_nfa.add_transition(nfa1_final_state, '', nfa2.initial_state)

        return new_nfa

    def repeated(self) -> 'FSA':
        # Create the space for 2 new states
        n_states = len(self.states)
        nfa = self.rename(range(1, n_states + 1))

        # Find the states we need
        init_state = 0
        nfa_init_state = 1
        nfa_last_state = list(nfa.final_states)[0]
        last_state = n_states + 1 # 2

        nfa.states.add(init_state)
        nfa.states.add(last_state)

        nfa.initial_state = init_state
        nfa.final_states = {last_state}

        # Add the 𝝴-transitions
        nfa.add_transition(init_state, '', nfa_init_state)
        nfa.add_transition(nfa_last_state, '', last_state)
        nfa.add_transition(nfa_init_state, '', nfa_last_state)
        nfa.add_transition(nfa_last_state, '', nfa_init_state)

        return nfa

    def rename(self, r: range) -> 'FSA':
        if len(r) != len(self.states):
            raise ValueError

        # Dictionary that maps old states number with the new one
        mapper = {old: new for old, new in zip(self.states, r)}

        # Translate the final states
        f = {mapper[state] for state in self.final_states}

        # "Translate" the transition function
        move = {}
        for state, char in self.move:
            k = (state, char)
            to = {mapper[s] for s in self.move[k]}
            move[(mapper[state], char)] = to

        return FSA(set(r), self.alphabet, move, mapper[self.initial_state], f)

    def make_compatible(self, other: 'FSA', start_from=1) -> ('FSA', 'FSA', int):
        # Find how many states we need
        states_total_n = len(self.states) + len(other.states)

        # Find the boundaries
        middle = len(self.states) + start_from
        last = middle + len(other.states)

        # Create the ranges
        first_range = range(start_from, middle)
        second_range = range(middle, last)

        # Rename
        n1 = self.rename(first_range)
        n2 = other.rename(second_range)

        return n1, n2, states_total_n

    def add_transition(self, from_state: int, char: str, to: int):
        k = (from_state, char)
        if k not in self.move:
            self.move[k] = {to}
        else:
            self.move[k].add(to)

    def epsilon_closure(self, states: set, visited: set=None) -> set:
        closure = set()
        if visited is None:
            visited = set()

        for state in states:
            closure.add(state)
            visited.add(state)

            k = (state, '')
            if k in self.move:
                not_visited = self.move[k].difference(visited)
                other_closure = self.epsilon_closure(not_visited, visited)
                closure = closure.union(other_closure)

        return closure

    def simulate(self, word: str) -> bool:
        if self.non_deterministic:
            return self.__nfa_simulate(word)

    def non_deterministic(self) -> bool:
        transitions = {c for _, c in self.move}
        states_per_transition = [len(self.move[k]) for k in self.move]

        return '' in transitions or reduce(max, states_per_transition, 0) > 1

    def __nfa_simulate(self, word: str) -> bool:
        input_stack = iter(word)
        symbol = next(input_stack)
        states = self.epsilon_closure({self.initial_state})

        while symbol != '$':
            # closure(U move(t, symbol) for t in states)
            closure = set()
            for state in states:
                k = (state, symbol)
                if k in self.move:
                    closure = closure.union(self.epsilon_closure(self.move[k]))

            states = closure
            symbol = next(input_stack)

        return states.intersection(self.final_states) != set()