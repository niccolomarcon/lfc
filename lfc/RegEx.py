from lfc import Production, Grammar, NFA


def translate(text):
    def not_operator(t):
        return t not in {'|', '(', ')', '*'}

    stack = list(filter(not_operator, text))
    translation = ''.join(['a' if not_operator(t) else t for t in text] + ['$'])

    return stack, translation


def parse(r):
    prds = ['R->a', 'R->R|R', 'R->RR', 'R->R*', 'R->(R)']
    prds = [Production.from_text(p) for p in prds]
    g = Grammar.from_productions(prds)
    PT = [{} for _ in range(18)]
    PT[0]['a'] = ('SHIFT', 13)
    PT[0]['R'] = ('GOTO', 2)
    PT[0]['('] = ('SHIFT', 1)
    PT[1]['a'] = ('SHIFT', 3)
    PT[1]['R'] = ('GOTO', 15)
    PT[1]['('] = ('SHIFT', 5)
    PT[2]['a'] = ('SHIFT', 13)
    PT[2]['$'] = ('ACCEPT', '')
    PT[2]['|'] = ('SHIFT', 4)
    PT[2]['R'] = ('GOTO', 6)
    PT[2]['*'] = ('SHIFT', 9)
    PT[2]['('] = ('SHIFT', 1)
    PT[3]['a'] = ('REDUCE', Production.from_text('R->a'))
    PT[3]['|'] = ('REDUCE', Production.from_text('R->a'))
    PT[3][')'] = ('REDUCE', Production.from_text('R->a'))
    PT[3]['*'] = ('REDUCE', Production.from_text('R->a'))
    PT[3]['('] = ('REDUCE', Production.from_text('R->a'))
    PT[4]['a'] = ('SHIFT', 13)
    PT[4]['R'] = ('GOTO', 11)
    PT[4]['('] = ('SHIFT', 1)
    PT[5]['a'] = ('SHIFT', 3)
    PT[5]['R'] = ('GOTO', 7)
    PT[5]['('] = ('SHIFT', 5)
    PT[6]['a'] = ('REDUCE', Production.from_text('R->RR'))
    PT[6]['|'] = ('REDUCE', Production.from_text('R->RR'))
    PT[6]['*'] = ('SHIFT', 9)
    PT[6]['$'] = ('REDUCE', Production.from_text('R->RR'))
    PT[6]['('] = ('REDUCE', Production.from_text('R->RR'))
    PT[6]['R'] = ('GOTO', 6)
    PT[7]['a'] = ('SHIFT', 3)
    PT[7]['|'] = ('SHIFT', 14)
    PT[7][')'] = ('SHIFT', 10)
    PT[7]['R'] = ('GOTO', 8)
    PT[7]['*'] = ('SHIFT', 17)
    PT[7]['('] = ('SHIFT', 5)
    PT[8]['a'] = ('REDUCE', Production.from_text('R->RR'))
    PT[8]['|'] = ('REDUCE', Production.from_text('R->RR'))
    PT[8][')'] = ('REDUCE', Production.from_text('R->RR'))
    PT[8]['*'] = ('SHIFT', 17)
    PT[8]['('] = ('REDUCE', Production.from_text('R->RR'))
    PT[8]['R'] = ('GOTO', 8)
    PT[9]['a'] = ('REDUCE', Production.from_text('R->R*'))
    PT[9]['|'] = ('REDUCE', Production.from_text('R->R*'))
    PT[9]['*'] = ('REDUCE', Production.from_text('R->R*'))
    PT[9]['$'] = ('REDUCE', Production.from_text('R->R*'))
    PT[9]['('] = ('REDUCE', Production.from_text('R->R*'))
    PT[10]['a'] = ('REDUCE', Production.from_text('R->(R)'))
    PT[10]['|'] = ('REDUCE', Production.from_text('R->(R)'))
    PT[10][')'] = ('REDUCE', Production.from_text('R->(R)'))
    PT[10]['*'] = ('REDUCE', Production.from_text('R->(R)'))
    PT[10]['('] = ('REDUCE', Production.from_text('R->(R)'))
    PT[11]['a'] = ('SHIFT', 13)
    PT[11]['|'] = ('REDUCE', Production.from_text('R->R|R'))
    PT[11]['*'] = ('SHIFT', 9)
    PT[11]['$'] = ('REDUCE', Production.from_text('R->R|R'))
    PT[11]['('] = ('SHIFT', 1)
    PT[11]['R'] = ('GOTO', 6)
    PT[12]['a'] = ('SHIFT', 3)
    PT[12]['|'] = ('REDUCE', Production.from_text('R->R|R'))
    PT[12][')'] = ('REDUCE', Production.from_text('R->R|R'))
    PT[12]['*'] = ('SHIFT', 17)
    PT[12]['('] = ('SHIFT', 5)
    PT[12]['R'] = ('GOTO', 8)
    PT[13]['a'] = ('REDUCE', Production.from_text('R->a'))
    PT[13]['|'] = ('REDUCE', Production.from_text('R->a'))
    PT[13]['*'] = ('REDUCE', Production.from_text('R->a'))
    PT[13]['$'] = ('REDUCE', Production.from_text('R->a'))
    PT[13]['('] = ('REDUCE', Production.from_text('R->a'))
    PT[14]['a'] = ('SHIFT', 3)
    PT[14]['R'] = ('GOTO', 12)
    PT[14]['('] = ('SHIFT', 5)
    PT[15]['a'] = ('SHIFT', 3)
    PT[15]['|'] = ('SHIFT', 14)
    PT[15][')'] = ('SHIFT', 16)
    PT[15]['R'] = ('GOTO', 8)
    PT[15]['*'] = ('SHIFT', 17)
    PT[15]['('] = ('SHIFT', 5)
    PT[16]['a'] = ('REDUCE', Production.from_text('R->(R)'))
    PT[16]['|'] = ('REDUCE', Production.from_text('R->(R)'))
    PT[16]['*'] = ('REDUCE', Production.from_text('R->(R)'))
    PT[16]['$'] = ('REDUCE', Production.from_text('R->(R)'))
    PT[16]['('] = ('REDUCE', Production.from_text('R->(R)'))
    PT[17]['a'] = ('REDUCE', Production.from_text('R->R*'))
    PT[17]['|'] = ('REDUCE', Production.from_text('R->R*'))
    PT[17][')'] = ('REDUCE', Production.from_text('R->R*'))
    PT[17]['*'] = ('REDUCE', Production.from_text('R->R*'))
    PT[17]['('] = ('REDUCE', Production.from_text('R->R*'))

    return g.shift_reduce(PT, r)


def thompson(ops: list, names: list, epsilon: str='𝝴') -> 'NFA':
    op: Production = ops.pop()
    if op == Production.from_text('R->a'):
        name = names.pop() if names[-1] != epsilon else ''
        a = {name} if name != epsilon else set()
        move = {(0, name): {1}}

        return NFA({0, 1}, a, move, 0, {1})

    elif op == Production.from_text('R->(R)'):
        return thompson(ops, names, epsilon)

    elif op == Production.from_text('R->R|R'):
        r2 = thompson(ops, names, epsilon)
        r1 = thompson(ops, names, epsilon)
        return r1.pipe(r2)

    elif op == Production.from_text('R->RR'):
        r2 = thompson(ops, names, epsilon)
        r1 = thompson(ops, names, epsilon)
        return r1.concat(r2)

    elif op == Production.from_text('R->R*'):
        r = thompson(ops, names, epsilon)
        return r.repeated()

    else:
        raise ValueError


class RegEx:
    def __init__(self, regex: str, epsilon: str='𝝴') -> 'RegEx':
        if any(type(arg) is not str for arg in (regex, epsilon)):
            raise TypeError

        names, r = translate(regex)
        operations = parse(r)

        if len(operations) > 0:
            self.NFA = thompson(operations, names)
        else:
            raise ValueError