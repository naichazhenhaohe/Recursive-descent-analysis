from pprint import pprint
from copy import deepcopy
import sys
import os

# 词法分析


class Lexical_Analyzer:
    token = ''
    string = ''
    index = 0
    is_end = False
    ch = ''
    error_type = ''
    one_op = ['+', '-', ',', '*', '%', '/', ';',
              '(', ')', "'", '"', ' ', '\n', '.', '{', '}', '[', ']', '`', '#']
    not_print = [' ', '\n']
    reserved = ['char', 'int', 'float', 'break', 'const', 'return', 'void',
                'return', 'void', 'continue', 'do', 'while', 'if', 'else', 'for']
    two_next = {
        '<': ['='],
        '>': ['='],
        '=': ['=', ],
        '!': ['='],
        '|': ['|'],
        '&': ['&'],
    }
    token_to_category = {word: word.upper() for word in reserved}
    token_to_category['>'] = '213'
    token_to_category['<'] = '211'
    token_to_category['>='] = '214'
    token_to_category['<='] = '212'
    token_to_category['=='] = '215'
    token_to_category['='] = '219'
    token_to_category['!='] = '216'
    token_to_category[';'] = '303'
    token_to_category['#'] = 'HASH'
    token_to_category['+'] = '209'
    token_to_category['.'] = '220'
    token_to_category['-'] = '210'
    token_to_category['!'] = '205'
    token_to_category['*'] = '206'
    token_to_category['/'] = '207'
    token_to_category['&&'] = '217'
    token_to_category['||'] = '218'
    token_to_category['%'] = '208'
    token_to_category[','] = '304'
    token_to_category['('] = '201'
    token_to_category[')'] = '202'
    token_to_category['['] = '203'
    token_to_category[']'] = '204'
    token_to_category['{'] = '301'
    token_to_category['}'] = '302'
    token_to_category['`'] = 'ACCENT'
    token_to_category["'"] = 'QUO'
    token_to_category['"'] = 'DQUO'
    token_to_category[' '] = 'BLANK'
    token_to_category['\n'] = 'ENTER'

    def __init__(self, string=''):
        self.string = string
        self.res = []

    def lookup(self):
        return True if self.token in self.reserved else False

    def out(self, c=''):
        if c == '':
            if self.token in self.token_to_category.keys():
                if self.token not in self.not_print:
                    self.res.append(
                        [self.token_to_category[self.token], self.token])
                else:
                    pass
            else:
                self.error_type = "unkown terminal character '%s'" % self.token
                self.report_error()
        else:
            if c == 'NOTE':
                pass
            else:
                self.res.append([c, self.token])

        self.token = ''

    def get_char(self):
        if self.is_end:
            return False

        self.ch = self.string[self.index]
        self.token += self.ch
        self.index += 1
        if self.index == len(self.string):
            self.is_end = True
        return self.ch

    def retract(self):
        self.is_end = False
        self.index = max(self.index - 1, 0)
        self.ch = self.string[max(self.index - 1, 0)]
        self.token = self.token[:-1]

    def alpha(self):
        while not self.is_end and self.string[self.index].isalnum() and self.get_char():
            pass

        self.out('' if self.lookup() else 'ID')

    def digit(self):
        while not self.is_end and (self.string[self.index].isdigit() or self.string[self.index] == '.' or self.string[self.index] == 'e' or self.string[self.index] == 'E') and self.get_char():
            pass
        self.out('DIGITAL')

    def one(self):
        self.out()

    def two(self):
        now_ch = self.ch
        if self.get_char() in self.two_next[now_ch]:
            self.out()
        else:
            self.retract()
            self.out()

    def back_slant(self):
        self.get_char()
        if self.ch == '*':
            try:
                end_index = self.string.index('*/', self.index)
            except:
                self.error_type = "no pair with '*/'"
                self.report_error()
            self.token = self.token + self.string[self.index:end_index] + '*/'
            self.ch = self.string[end_index + 1]
            if end_index + 2 < len(self.string):
                self.index = end_index + 2
            else:
                self.is_end = True
            self.out('NOTE')
        elif self.ch == '/':
            end_index = self.string.index('\n', self.index)
            self.token = self.token + self.string[self.index:end_index] + '\n'
            self.ch = self.string[end_index]
            if end_index + 1 < len(self.string):
                self.index = end_index + 1
            else:
                self.is_end = True
            self.out('NOTE')
        else:
            self.retract()
            self.out()

    def report_error(self):
        exit('[error]index %s: %s' % (self.index, self.error_type))

    switch = {
        'alpha': alpha, 'digit': digit,  'one': one,  'two': two,
        '/': back_slant,  '': report_error,
    }

    def analyse(self):
        while self.get_char():
            if self.ch.isalpha():
                case = 'alpha'
            elif self.ch.isdigit():
                case = 'digit'
            elif self.ch == '/':
                case = '/'
            elif self.ch in self.one_op:
                case = 'one'
            elif self.ch in self.two_next.keys():
                case = 'two'
            else:
                self.error_type = "unkown character '%s'" % self.ch
                case = ''
            self.switch[case](self)
        return self.res

# 语法分析


class Analyzer:
    def __init__(self, start, terminal, production):
        self.start = start
        self.terminal = terminal
        self.nonterminal = production.keys()
        self.production = production
        self.first = {nonterminal: set() for nonterminal in self.nonterminal}
        self.follow = {nonterminal: set() for nonterminal in self.nonterminal}
        self.get_first()
        # pprint(self.first)
        # print('-----------')
        self.get_follow()
        # pprint(self.follow)
        self.T = 0
        self.code = []

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

    def AriExp(self):
        self.AriItem()
        self.AriExp_foo()

    # 'AriExp_foo': [['+', 'AriExp'], ['-', 'AriExp'], ['ε']]
    def AriExp_foo(self):
        if self.token_list[self.index][0] == '209' or self.token_list[self.index][0] == '210':
            self.index += 1
            self.AriExp()

    def AriItem(self):
        self.AriFactor()
        self.AriItem_foo()

    # 'AriItem_foo': [['*', 'AriItem'], ['/', 'AriItem'], ['%', 'AriItem'], ['ε']],
    def AriItem_foo(self):
        if self.token_list[self.index][0] == '206' or self.token_list[self.index][0] == '207' or self.token_list[self.index][0] == '208':
            self.index += 1
            self.AriItem()

    # 'AriFactor': [['(', 'AriExp', ')'], ['ID'], ['DIGITAL']],
    def AriFactor(self):
        if self.token_list[self.index][0] == '201':
            self.index += 1
            self.AriExp()
            if self.token_list[self.index][0] == '202':
                self.index += 1
            else:
                print(self.string[:-1] + ' 语法错误，缺少 ) ')
                sys.exit()
        elif self.token_list[self.index][0] == 'ID':
            self.index += 1
            if self.token_list[self.index][0] == 'ID' or self.token_list[self.index][0] == '(':
                print(self.string[:-1] + ' 语法错误，下标' + str(self.index) + '处缺少算术运算符')
                sys.exit()
        elif self.token_list[self.index][0] == 'DIGITAL':
            self.index += 1
        else:
            print(self.string[:-1] + " 语法错误，缺少算术运算对象")
            sys.exit()


    # 'BooExp': [['BooItem', 'BooExp_foo']],
    def BooExp(self):
        self.BooItem()
        self.BooExp_foo()

    # 'BooExp_foo': [['||', 'BooExp'], ['ε']],
    def BooExp_foo(self):
        if self.token_list[self.index][0] == '218':
            self.index += 1
            self.BooExp()

    # 'BooItem': [['BooFactor', 'BooItem_foo']],
    def BooItem(self):
        self.BooFactor()
        self.BooItem_foo()

    # 'BooItem_foo': [['&&', 'BooItem'], ['ε']],
    def BooItem_foo(self):
        if self.token_list[self.index][0] == '217':
            self.index += 1
            self.BooItem()

    # 'BooFactor': [['!', 'BooExp'], ['AriExp', 'BooFactor_foo']],
    def BooFactor(self):
        if self.token_list[self.index][0] == '205':
            self.index += 1
            self.BooExp()
        else:
            self.AriExp()
            self.BooFactor_foo()

    # 'BooFactor_foo': [['RelExp', 'AriExp'], ['ε']],
    def BooFactor_foo(self):
        if self.token_list[self.index][1] in self.first['BooFactor_foo']:
            self.RelOperator()
            self.AriExp()

    # 'RelOperator': [['>'], ['<'], ['<='], ['>='], ['=='], ['!=']],
    def RelOperator(self):
        operators = ['<=', '>=', '<', '>', '==', '!=']
        if self.token_list[self.index][1] in operators:
            self.index += 1
        else:
            print(self.string[:-1] + ' 语法错误，下标' + str(self.index) + '处缺少布尔运算符')
            sys.exit()

    def Exp(self):
        self.BooExp()
        self.Exp_foo()

    def Exp_foo(self):
        if self.token_list[self.index][0] == '219':
            self.index += 1
            self.Exp()

    # 'if_Sta': [['if', '(', 'BooExp', ')', '{', 'Exp', '}', 'if_Sta_foo']],
    def if_Sta(self):
        if self.token_list[self.index][0] == 'IF':
            self.index += 1
            print(self.token_list[self.index])
            if self.token_list[self.index][0] == '201':
                self.index += 1
                self.BooExp()
                if self.token_list[self.index][0] == '202':
                    self.index += 1
                    if self.token_list[self.index][0] == '301':
                        self.index += 1
                        self.Exp()
                        if self.token_list[self.index][0] == '302':
                            self.index += 1
                            self.if_Sta_foo()
                        else:
                            print(self.string[:-1] + ' 语法错误, 缺少对应 }')
                            sys.exit()
                    else:
                        print(self.string[:-1] + ' 语法错误，缺少 {')
                        sys.exit()
                else:
                    print(self.string[:-1] + ' 语法错误，缺少对应 ) ')
                    sys.exit()
            else:
                print(self.string[:-1] + ' 语法错误，if关键词后缺少 (')
                sys.exit()
        else:
            print(self.string[:-1] + ' 语法错误，无法找到if关键字')
            sys.exit()


    # # 'if_Sta_foo': [['else', '{', 'Exp', '}'], ['ε']]
    def if_Sta_foo(self):
        if self.token_list[self.index][0] == 'ELSE':
            self.index += 1
            if self.token_list[self.index][0] == '301':
                self.index += 1
                self.Exp()
                if self.token_list[self.index][0] == '302':
                    self.index += 1
                else:
                    print(self.string[:-1] + ' 语法错误，esle区域缺少 }')
                    sys.exit()
            else:
                print(self.string[:-1] + ' 语法错误，else区缺少 {')
                sys.exit()

    def delimiter_check(self):
        marks = ['(', ')', '[', ']', '{', '}', "'", '"', '`']
        mark_num = {mark: 0 for mark in marks}
        for item in self.token_list:
            if item[0] == '201':
                mark_num['('] += 1
            elif item[0] == '202':
                mark_num[')'] += 1
            elif item[0] == '203':
                mark_num['['] += 1
            elif item[0] == '204':
                mark_num[']'] += 1
            elif item[0] == '301':
                mark_num['{'] += 1
            elif item[0] == '302':
                mark_num['}'] += 1
            elif item[0] == 'ACCENT':
                mark_num['`'] += 1
            elif item[0] == 'QUO':
                mark_num["'"] += 1 
            elif item[0] == 'DQUO':
                mark_num['"'] += 1
        if mark_num['('] > mark_num [')']:
            print(self.string[:-1] + ' 语法错误，缺少 ) ')
            sys.exit()
        elif mark_num[')'] > mark_num['(']:
            print(self.string[:-1] + ' 语法错误，缺少 ( ')
            sys.exit()

        if mark_num['['] > mark_num [']']:
            print(self.string[:-1] + ' 语法错误，缺少 ] ')
            sys.exit()
        elif mark_num[']'] > mark_num['[']:
            print(self.string[:-1] + ' 语法错误，缺少 [ ')
            sys.exit()

        if mark_num['{'] > mark_num ['}']:
            print(self.string[:-1] + ' 语法错误，缺少 } ')
            sys.exit()
        elif mark_num['}'] > mark_num['{']:
            print(self.string[:-1] + ' 语法错误，缺少 { ')
            sys.exit()

        if mark_num['`'] % 2 == 0 and mark_num['`'] != 0:
            print(self.string[:-1] + ' 语法错误，出現奇数个 ` ')
            sys.exit()            
        if mark_num["'"] % 2 == 0 and mark_num["'"] != 0:
            print(self.string[:-1] + " 语法错误，出現奇数个 ' ")
            sys.exit()   
        if mark_num['"'] % 2 == 0 and mark_num['"'] != 0:
            print(self.string[:-1] + ' 语法错误，出現奇数个 " ')
            sys.exit()    

    def analyse(self, res):
        res.append(['HASH', '#'])
        self.token_list = res
        self.string = ''
        for item in res:
            self.string += item[1]
        self.index = 0
        # pprint(self.token_list)
        self.delimiter_check()
        if self.start == 'AriExp':
            self.AriExp()
        elif self.start == 'BooExp':
            self.BooExp()
        elif self.start == 'Exp':
            self.Exp()
        elif self.start == 'if_Sta':
            self.if_Sta()

        pprint(self.string[:-1] + " OK!")
        self.Semantic()

    def Semantic(self):
        operators = {'+': 0, '-': 0, '*': 1, '/': 1, '%': 1, ')': -1, '(': -1}
        self.char = []
        self.symbol = []
        self.top_char = 0
        self.top_symbol = 0

        for item in self.token_list[:-1]:
            if item[1] not in operators and item[1] != ')' and item[1] != '(':
                self.char.append(item[1])
                self.top_char += 1
            elif item[1] in operators.keys() and len(self.symbol) == 0:
                self.symbol.append(item[1])
                self.top_symbol += 1
            elif item[1] == '(':
                self.symbol.append(item[1])
                self.top_symbol += 1
            elif item[1] == ')':
                while self.symbol[self.top_symbol-1] != '(':
                    first = self.char.pop()
                    second = self.char.pop()
                    pop_symbol = self.symbol.pop()
                    self.code.append([pop_symbol, second, first, 'T'+str(self.T)])
                    self.top_symbol -= 1
                    self.char.append('T'+str(self.T))
                    self.top_char -= 1
                    self.T += 1
                self.symbol.pop()
                self.top_symbol -= 1
            elif item[1] in operators.keys() and operators[item[1]] > operators[self.symbol[self.top_symbol - 1]]:
                self.symbol.append(item[1])
                self.top_symbol += 1
            elif item[1] in operators.keys() and operators[item[1]] <= operators[self.symbol[self.top_symbol - 1]]:
                first = self.char.pop()
                second = self.char.pop()
                pop_symbol = self.symbol.pop()
                self.code.append([pop_symbol, second, first, 'T'+str(self.T)])
                self.char.append('T'+str(self.T))
                self.top_char -= 1
                self.symbol.append(item[1])
                self.T += 1
        while len(self.symbol)!= 0:
            first = self.char.pop()
            second = self.char.pop()
            pop_symbol = self.symbol.pop()
            self.code.append([pop_symbol, second, first, 'T'+str(self.T)])
            self.top_symbol -= 1
            self.char.append('T'+str(self.T))
            self.top_char -= 1
            self.T += 1
        pprint(self.code)

terminal = ['+', '-', '*', '/', '%', 'ε', '!', '=', 'if', 'else', ':', '{', '}',
            '(', ')', 'ID', '||', '&&', '<', '>', '>=', '<=', '==', '!=', 'DIGITAL']

production = {
    'AriExp': [['AriItem', 'AriExp_foo']],
    'AriExp_foo': [['+', 'AriExp'], ['-', 'AriExp'], ['ε']],
    'AriItem': [['AriFactor', 'AriItem_foo']],
    'AriItem_foo': [['*', 'AriItem'], ['/', 'AriItem'], ['%', 'AriItem'], ['ε']],
    'AriFactor': [['(', 'AriExp', ')'], ['ID'], ['DIGITAL']],

    'BooExp': [['BooItem', 'BooExp_foo']],
    'BooExp_foo': [['||', 'BooExp'], ['ε']],
    'BooItem': [['BooFactor', 'BooItem_foo']],
    'BooItem_foo': [['&&', 'BooItem'], ['ε']],
    'BooFactor': [['!', 'BooExp'], ['AriExp', 'BooFactor_foo']],
    'BooFactor_foo': [['RelOperator', 'AriExp'], ['ε']],

    'RelOperator': [['>'], ['<'], ['<='], ['>='], ['=='], ['!=']],

    'Exp': [['BooExp', 'Exp_foo']],
    'Exp_foo': [['=', 'Exp'], ['ε']],

    'if_Sta': [['if', '(', 'BooExp', ')', '{', 'Exp', '}', 'if_Sta_foo']],
    'if_Sta_foo': [['else', '{', 'Exp', '}'], ['ε']]
}

starter = 'AriExp'
# starter = 'BooExp'
# starter = 'Exp'
# starter = 'if_Sta'
analyzer = Analyzer(starter, terminal, production)

#测试算术运算
# source_string = 'a * (b+test - (c % 3))'
source_string='b*(c-d+f*(g+h-i/j+k))'
# source_string = 'a'
# source_string = 'a +/b'
# source_string = '(a+b- c % a'
#测试布尔运算
# source_string = '!a >= (c + d)'
# source_string = 'a && (a c)'
# source_string = 'demo > 1'
# source_string = '!a || (c + d)'
# source_string = 'i=i&&i<i'
#测试if语句
# source_string = 'if(a==b){c= c-b}else {a = a+1}'
# source_string = 'ifa==b){c>c}'
# source_string = 'if(a>a&& b||c){a+a}else'

res = Lexical_Analyzer(source_string).analyse()
analyzer.analyse(res=res)
