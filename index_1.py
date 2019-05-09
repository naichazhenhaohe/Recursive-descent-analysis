import os

class Analyzer:
  token = ''
  string = ''
  index = 0
  is_end = False
  ch = ''
  error_type = ''
  one_op = ['+', '-', ',', '*', '%', '/', ';','(', ')', "'", '"', ' ', '\n', '.', '{', '}', '[', ']', '`','#']
  not_print = [' ', '\n']
  reserved = ['char','int','float','break','const','return','void','return','void','continue','do','while','if','else','for']
  two_next = {
    '<': ['='],
    '>': ['='],
    '=': ['=',],
    '!': ['='],
    '|': ['|'],
    '&': ['&',],
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
  token_to_category['*'] = '206'
  token_to_category['/'] = '207'
  token_to_category['&&'] = '217'
  token_to_category['||'] = '218'
  token_to_category['&'] = 'AND'
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

  def __init__(self, is_sensitive=False, file='file.txt', out_file='res.txt', log_level=1):
    self.log_level = log_level
    self.is_sensitive = is_sensitive
    if out_file == '':
      out_path = os.path.dirname(file)
      out_file_name = os.path.basename(file)[:file.rindex('.')]
      self.out_file = os.path.join(out_path, out_file_name)
    try:
      self.out_f = open(out_file, 'w', encoding='utf-8')
    except:
      exit('[error] can not open file')
    with open(file, 'r', encoding='utf-8') as f:
      file = f.read()
      self.string = file.replace('\t', '')
      if not self.is_sensitive:
        self.string.lower()

  def lookup(self):
    return True if self.token in self.reserved else False

  def out(self, c=''):
    if c == '':
      if self.token in self.token_to_category.keys():
        if self.token not in self.not_print:
          self.out_f.write(self.token_to_category[self.token] + ' ' + self.token + '\n')
          if self.log_level:
            print(self.token_to_category[self.token] + '\t' + self.token)
        else:
          # self.out_f.write(self.token_to_category[self.token] + '\n')
          # if self.log_level:
          #   print(self.token_to_category[self.token])
          pass
      else:
        self.error_type = "unkown terminal character '%s'" % self.token
        self.report_error()
    else:
      if c == 'NOTE':
        # self.out_f.write(self.token_to_category[self.token] + '\n')
        # if self.log_level:
        #   print(self.token_to_category[self.token])
        pass
      else:
        self.out_f.write(c + ' ' + self.token + '\n')
        if self.log_level:
          print(c + '\t' + self.token)

    self.token = ''

  def get_char(self):
    if self.is_end:
      return False

    self.ch = self.string[self.index]
    self.token += self.ch
    self.index += 1
    if self.log_level == 2:
      print('[get_char]index: %s, ch: %s, token: %s' % (self.index, self.ch, self.token))
    if self.index == len(self.string):
      self.is_end = True
    return self.ch

  def retract(self):
    self.is_end = False
    self.index = max(self.index - 1, 0)
    self.ch = self.string[max(self.index - 1, 0)]
    self.token = self.token[:-1]
    if self.log_level == 2:
      print('[retract]index: %s, ch: %s, token: %s' % (self.index, self.ch, self.token))

  def alpha(self):
    while not self.is_end and self.string[self.index].isalnum() and self.get_char():
      pass

    self.out('' if self.lookup() else 'ID')

  def digit(self):
    while not self.is_end and self.string[self.index].isdigit() and self.get_char():
      pass
    self.out('INTSTR')

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

Analyzer().analyse()