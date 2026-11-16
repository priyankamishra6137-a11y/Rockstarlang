# **********************************
# Constants & Token Definitions
# **********************************

# Alphabets & Digits
UPPER_CASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LOWER_CASE = UPPER_CASE.lower()
LETTERS = UPPER_CASE + LOWER_CASE
DIGITS = '0123456789'
LETTERS_DIGITS = LETTERS + DIGITS + '_'

# Data Type Tokens
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_STRING = 'STRING'

# Operator & Delimiter Tokens
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

# Structure & Control Tokens
TT_NEWLINE = 'NEWLINE'
TT_TAB = 'TAB'
TT_EOF = 'EOF'
TT_COMMA = 'COMMA'

# Identifiers & Keywords
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'

KEYWORDS = [
    'GTA52013',   # Program start block
    'GTA62026',   # Program end block
    'call_CJ'     # Print statement
]


# **********************************
# Token Class
# **********************************

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value != None:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


# **********************************
# Lexical Analyzer (Lexer)
# **********************************

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.line = 1
        self.col = -1
        self.current_char = None
        self.at_start = True
        self.advance()

    def advance(self):
        """Advances the pointer by one character and tracks line/column positions."""
        if self.current_char == '\n':
            self.line += 1
            self.col = 0
            self.at_start = True
        else:
            self.col += 1
            self.at_start = (self.col == 0)

        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def make_tokens(self):
        """Scans raw source text and converts it into a list of tokens."""
        tokens = []

        while self.current_char != None:
            if self.current_char == '\n':
                tokens.append(Token(TT_NEWLINE))
                self.advance()

            elif self.current_char in ' \t':
                if self.at_start:
                    tab_token = self.make_tab()
                    if tab_token:
                        tokens.append(tab_token)
                else:
                    self.advance()

            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA))
                self.advance()

            elif self.current_char in LETTERS:
                tokens.append(self.make_word())

            elif self.current_char in DIGITS:
                tokens.append(self.make_number())

            elif self.current_char in ('"', "'"):
                string_token, error = self.make_string()
                if error:
                    return [], error
                tokens.append(string_token)

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
                tokens.append(Token(TT_LPAREN))
                self.advance()

            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()

            else:
                char = self.current_char
                err_line, err_col = self.line, self.col + 1
                self.advance()
                return [], f"Illegal Character '{char}' at Line {err_line}, Col {err_col}"

        tokens.append(Token(TT_EOF))
        return tokens, None

    def make_tab(self):
        """Captures 4 leading spaces or a tab character as an indentation token."""
        tab_str = ''
        while self.current_char != None and self.current_char in ' \t':
            tab_str += self.current_char
            self.advance()

        if tab_str == '    ' or tab_str == '\t':
            return Token(TT_TAB)
        return None

    def make_word(self):
        """Scans identifiers and checks against reserved Rockstarlang keywords."""
        word_str = ''
        while self.current_char != None and self.current_char in LETTERS_DIGITS:
            word_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if word_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, word_str)

    def make_number(self):
        """Scans integer and floating-point numeric literals."""
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        return Token(TT_FLOAT, float(num_str))

    def make_string(self):
        """Scans double or single-quoted string literals."""
        quote_char = self.current_char
        string_val = ''
        self.advance()

        while self.current_char != None and self.current_char != quote_char:
            string_val += self.current_char
            self.advance()

        if self.current_char != quote_char:
            return None, f"Unterminated String at Line {self.line}"

        self.advance()
        return Token(TT_STRING, string_val), None


# **********************************
# Entry Point
# **********************************

def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    return tokens, error
