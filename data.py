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
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details == details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        return result

class IlegalCharError:
    def __init__(self, details):
        super().__init__('Illegal Character', details)
        
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


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value: 
            return f'{self.type}:{str(self.value)}'
        return f'{self.type}'
    


########
##
##   LEXER - The lexer just turns the meaningless string into a flat list of things like "number literal", "string literal", "identifier", or "operator", and can do things like recognizing reserved identifiers ("keywords") and discarding whitespace. Formally, a lexer recognizes some set of Regular languages
##
########
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

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
                char = self.current_char
                self.advance()
                return [], IlegalCharError("'" + char + "'")
            
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0


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
            print(num_str)
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))



########
##
## RUN
##
########

def run(text):
    # lexer = Lexer(text)
    tokens, error = Lexer(text).make_tokens()

    return tokens, error