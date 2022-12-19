#######
## 
## definition of constants
##
#######

DIGITS = '0987654321'


######
##
##ERROR
##
######

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def error_string_with_arrows(text, pos_start, pos_end):
        result = ''
        idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
        idx_end = text.find('\n', idx_start  + 1)
        if idx_end < 0: idx_end = len(text)


        line_count = pos_end.ln - pos_start.ln + 1
        for i in range(line_count):
            line = text[idx_start:idx_end]
            col_start = pos_start.col if i == 0 else 0
            col_end = pos_end.col if i == line_count - 1 else len(line)

            result+=line + '\n'
            result+= ' ' * col_start + '^' * (col_end - col_start)

            idx_start = idx_end
            idx_end = text.find('\n', idx_start + 1)
            if idx_end < 0: idx_end = len(text)

        return result.replace('\t', '')

    def as_string(self):
        result  = f'{self.error_name}: {self.details}'
        result += f'File: {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + Error.error_string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IlegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end,'Illegal Character', details)

class InvalidSyntaxError(Error):
	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)
        self.context = context

######
##Position
######

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col +=1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)



######
##
## Type of the Tokens
##
######

TT_INT      = 'TT_INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_EOF      = 'EOF'

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
            
        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value: 
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    


########
##
##   LEXER - The lexer just turns the meaningless string into a flat list of things like "number literal", "string literal", "identifier", or "operator", and can do things like recognizing reserved identifiers ("keywords") and discarding whitespace. Formally, a lexer recognizes some set of Regular languages
##
########
class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            # print('Pass here')
            if self.current_char in ' \t':
                self.advance()

            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
                
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_RPAREN))
            elif self.current_char == ')':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IlegalCharError(pos_start,self.pos,"'" + char + "'")
            
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if(self.current_char == '.'):
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
                # print(self.current_char)
            self.advance()

        if dot_count == 0:
            # print(num_str)
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))

########
##  NODES
#######

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

#######
##  PARSER Result
#######

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        
        return res

    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self

########
#PARSE
########

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        if(self.tok_idx < len(self.tokens)):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                "Expected '+', '-', '*', '/'"
            ))
        return res


    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        #"Implementing addition and subtraction"
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int or float"
        ))


    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res
        
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

########
# RUNTIME RESULT
########

class RTResult:
    def __init__(self):
        self.value = None
        self.error = None
    
    def register(self, res):
        if res.error: self.error = res.error
        return res.value

    def sucess(self, value):
        self.value = value
        return self

    def failure(self    , error):
        self.error = error
        return self

########
#VALUES
########

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
    
    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        
    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

########
##
## RUN
##
########

def run(fn, text):
    # lexer = Lexer(text)
    tokens, error = Lexer(fn, text).make_tokens()


	# Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error


    return tokens, error


