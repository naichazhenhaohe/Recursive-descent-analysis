from pprint import pprint
from copy import deepcopy
import sys


class Analyzer:
    def __init__(self, start, terminal, production):
        self.start = start
        self.terminal = terminal
        self.nonterminal = production.keys()
        self.production = production
        self.first = {nonterminal: set() for nonterminal in self.nonterminal}
        self.follow = {nonterminal: set() for nonterminal in self.nonterminal}
        self.get_first()
        pprint(self.first)
        print('-----------')
        self.get_follow()
        pprint(self.follow)

    def handle_get_first(self, nonterminal):
        for right in self.production[nonterminal]:
            for item in right:
                if item in self.terminal:
                    break
                if item in self.nonterminal:
                    self.first[nonterminal].update(self.first[item])
                    if ('ε' not in self.first[item]):
                        break

    def get_first(self):
        # S->aL First[S].add(a)
        for nonterminal in self.nonterminal:
            for right in self.production[nonterminal]:
                if(right[0] in self.terminal):
                    self.first[nonterminal].add(right[0])
        # pprint(self.first)
        # S->LMα First[S].add(First[L]) 若ε属于First[L], First[S].add(First[M]) ...直到First[S]不再增加
        while True:
            old_first = deepcopy(self.first)
            for nonterminal in self.nonterminal:
                self.handle_get_first(nonterminal)
            if old_first == self.first:
                break

    def get_follow(self):
        self.follow[self.start].add('#')
        while True:
            # old_follow和old_first用于判断是否已经不再更新
            old_follow = deepcopy(self.follow)
            for nonterminal in self.nonterminal:
                for right in self.production[nonterminal]:
                    for index, content in enumerate(right):
                        if content in self.terminal:
                            # 若该符号为终结符，则跳过
                            continue
                        if index == len(right) - 1:
                            # S->αL ,follow[L] |= follow[S]
                            self.follow[content] |= self.follow[nonterminal]
                        elif right[index+1] in self.terminal:
                            # S->La ,follow[L].add(a)
                            self.follow[content].add(right[index+1])
                        else:
                            # S->LB ,follow[L] |= first[B]/ε
                            temp = {
                                key for key in self.first[right[index + 1]] if key != 'ε'}
                            self.follow[content] |= temp
            if old_follow == self.follow:
                break

    def analyse(self, string=''):
        self.string = string + '#'
        self.index = 0
        self.BooExp()
        pprint(self.string[:-1] + " OK!")

    def AriExp(self):
        self.AriItem()
        self.AriExp_foo()

    # 'AriExp_foo': [['+', 'AriExp'], ['-', 'AriExp'], ['ε']]
    def AriExp_foo(self):
        if self.string[self.index] == '+' or self.string[self.index] == '-':
            self.index += 1
            self.AriExp()

    def AriItem(self):
        self.AriFactor()
        self.AriItem_foo()

    # 'AriItem_foo': [['*', 'AriItem'], ['/', 'AriItem'], ['ε']],
    def AriItem_foo(self):
        if self.string[self.index] == '*' or self.string[self.index] == '/' or self.string[self.index] == '%':
            self.index += 1
            self.AriExp()

    # 'AriFactor': [['(', 'AriExp', ')'], ['i']],
    def AriFactor(self):
        if self.string[self.index] == 'i':
            self.index += 1
            if self.string[self.index] == 'i' or self.string[self.index] == '(':
                print(self.string[:-1] + '语法错误，下标' +
                      str(self.index) + '处缺少算术运算符')
                sys.exit()
            if self.string[self.index] == ')' and '(' not in self.string[:self.index]:
                print(self.string[:-1] + '语法错误，缺少 (')
                sys.exit()
        elif self.string[self.index] == '(':
            self.index += 1
            self.AriExp()
            if self.string[self.index] == ')':
                self.index += 1
            else:
                print(self.string[:-1] + '语法错误，缺少 ) ')
                sys.exit()
        else:
            print(self.string[:-1] + '语法错误，下标' + str(self.index) + '处缺少算术运算对象')
            sys.exit()

    # 'BooExp': [['BooItem', 'BooExp_foo']],
    def BooExp(self):
        self.BooItem()
        self.BooExp_foo()

    # 'BooExp_foo': [['||', 'BooExp'], ['ε']],
    def BooExp_foo(self):
        if self.string[self.index] == '|' and self.string[self.index + 1] != '|':
            print(self.string[:-1] + ' 语法错误，非法运算符|')
            sys.exit()
        if self.string[self.index: self.index + 2] == '||':
            self.index += 2
            self.BooExp()

    # 'BooItem': [['BooFactor', 'BooItem_foo']],
    def BooItem(self):
        self.BooFactor()
        self.BooItem_foo()

    # 'BooItem_foo': [['&&', 'BooItem'], ['ε']],
    def BooItem_foo(self):
        if self.string[self.index] == '&' and self.string[self.index + 1] != '&':
            print(self.string[:-1] + ' 语法错误，非法运算符&')
            sys.exit()
        if self.string[self.index: self.index + 2] == '&&':
            self.index += 2
            self.BooItem()

    # 'BooFactor': [['!', 'BooExp'], ['AriExp', 'BooFactor_foo']],
    # 'BooFactor': [['!', 'BooExp'], ['AriExp'], ['RelExp']]
    def BooFactor(self):
        if self.string[self.index] == '!':
            self.index += 1
            self.BooExp()
        else:
            self.AriExp()
            self.BooFactor_foo()

    # 'BooFactor_foo': [['RelExp', 'AriExp'], ['ε']],
    def BooFactor_foo(self):
        if self.string[self.index : self.index+2] in self.first['BooFactor_foo'] or self.string[self.index] in self.first['BooFactor_foo']:
            self.RelOperator()
            self.AriExp()

    # 'RelExp': [['AriExp', 'RelOperator', 'AriExp']],
    def RelExp(self):
        self.AriExp()
        self.RelOperator()
        print(self.index)
        self.AriExp()

    def RelOperator(self):
        # print(self.string[self.index: self.index + 2] == )
        if self.string[self.index: self.index + 2] == '<=':
            self.index += 2
        elif self.string[self.index: self.index + 2] == '>=':
            self.index += 2
        elif self.string[self.index: self.index + 2] == '==':
            self.index += 2
        elif self.string[self.index: self.index + 2] == '!=':
            self.index += 2
        elif self.string[self.index] == '>':
            self.index += 1
        elif self.string[self.index] == '<':
            self.index += 1
        else:
            print(self.string[:-1] + '语法错误，下标' + str(self.index) + '处缺少布尔运算符')
            sys.exit()


terminal = ['+', '-', '*', '/', '%', 'ε', '!', '(', ')', 'i', '||', '&&', '<', '>', '>=', '<=', '==', '!=']

production = {
    'AriExp': [['AriItem', 'AriExp_foo']],
    'AriExp_foo': [['+', 'AriExp'], ['-', 'AriExp'], ['ε']],
    'AriItem': [['AriFactor', 'AriItem_foo']],
    'AriItem_foo': [['*', 'AriItem'], ['/', 'AriItem'], ['%', 'AriItem'], ['ε']],
    'AriFactor': [['(', 'AriExp', ')'], ['i']],

    'BooExp': [['BooItem', 'BooExp_foo']],
    'BooExp_foo': [['||', 'BooExp'], ['ε']],
    'BooItem': [['BooFactor', 'BooItem_foo']],
    'BooItem_foo': [['&&', 'BooItem'], ['ε']],
    'BooFactor': [['!', 'BooExp'], ['AriExp', 'BooFactor_foo']],
    'BooFactor_foo': [['RelOperator', 'AriExp'], ['ε']],

    'RelExp': [['AriExp', 'RelOperator', 'AriExp']],
    'RelOperator': [['>'], ['<'], ['<='], ['>='], ['=='], ['!=']],

}


starter = 'BooExp'
analyzer = Analyzer(starter, terminal, production)

# demo = 'i'
# demo = 'i+@'
# demo = '+/i'
# demo = 'i+i)++i'
# demo = '(i+(i-i+i)%i'
# demo = 'i+ii'
# demo = 'i+i/i%i-i*(i+i-i)'
#Boolean
# demo = 'i&&i+'
# demo = 'i'
# demo = 'i&&i|i'
# demo = 'i==i&&i<i'
demo = 'i<'
# demo = '!i||i+i'
# demo = 'i<=i&&(i/i)||i!=i'
analyzer.analyse(string=demo)
