# ==============================================================================
# 1. CONSTANTS & TOKEN DEFINITIONS
# ==============================================================================

# Character Sets
UPPER_CASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LOWER_CASE = UPPER_CASE.lower()
LETTERS = UPPER_CASE + LOWER_CASE
DIGITS = '0123456789'
LETTERS_DIGITS = LETTERS + DIGITS + '_'

# Literal Data Type Tokens
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_STRING = 'STRING'

# Arithmetic & Delimiter Tokens
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_COMMA = 'COMMA'

# Block Structure & Control Tokens
TT_NEWLINE = 'NEWLINE'
TT_TAB = 'TAB'
TT_EOF = 'EOF'

# Identifiers & Reserved Keywords
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'

KEYWORDS = {
    'GTA52013',   # Program entry block delimiter
    'GTA62026',   # Program exit block delimiter
    'call_CJ'     # Standard console output statement
}


# ==============================================================================
# 2. TOKEN REPRESENTATION
# ==============================================================================

class Token:
    """Represents a single lexical unit produced by the Lexer."""

    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


# ==============================================================================
# 3. LEXICAL ANALYZER (LEXER)
# ==============================================================================

class Lexer:
    """Scans raw source text character-by-character and generates a token list."""

    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.line = 1
        self.col = -1
        self.current_char = None
        self.at_start = True
        self.advance()

    def advance(self):
        """Advances the character pointer and updates line/column tracking."""
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
        """Tokenizes the entire source input into a validated list of Tokens."""
        tokens = []

        while self.current_char is not None:
            if self.current_char == '\n':
                tokens.append(Token(TT_NEWLINE))
                self.advance()

            elif self.current_char in ' \t':
                if self.at_start:
                    tab_token, error = self.make_tab()
                    if error:
                        return [], error
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
                return [], f"WASTED! Illegal character '{char}' at Line {err_line}, Col {err_col}"

        tokens.append(Token(TT_EOF))
        return tokens, None

    def make_tab(self):
        """Validates leading line indentation (requires 4 spaces or 1 tab character)."""
        tab_str = ''
        err_line = self.line

        while self.current_char is not None and self.current_char in ' \t':
            tab_str += self.current_char
            self.advance()

        # Ignore whitespace-only blank lines
        if self.current_char == '\n' or self.current_char is None:
            return None, None

        if tab_str == '    ' or tab_str == '\t':
            return Token(TT_TAB), None

        return None, f"WASTED! IndentationError: Expected 4 spaces or 1 tab at Line {err_line}"

    def make_word(self):
        """Scans alphanumeric words and classifies them as keywords or identifiers."""
        word_str = ''
        while self.current_char is not None and self.current_char in LETTERS_DIGITS:
            word_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if word_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, word_str)

    def make_number(self):
        """Scans integer and floating-point numeric literals."""
        num_str = ''
        dot_count = 0

        while self.current_char is not None and self.current_char in DIGITS + '.':
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
        """Scans single or double-quoted string literals."""
        quote_char = self.current_char
        err_line = self.line
        string_val = ''
        self.advance()

        while self.current_char is not None and self.current_char != quote_char:
            string_val += self.current_char
            self.advance()

        if self.current_char != quote_char:
            return None, f"WASTED! Unterminated string literal at Line {err_line}"

        self.advance()
        return Token(TT_STRING, string_val), None


# ==============================================================================
# 4. ABSTRACT SYNTAX TREE (AST) NODES
# ==============================================================================

class NumberNode:
    """AST node representing a numeric literal (INT or FLOAT)."""

    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    """AST node representing a string literal."""

    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    """AST node representing a binary arithmetic operation (left <op> right)."""

    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class PrintNode:
    """AST node representing a 'call_CJ' output statement with argument nodes."""

    def __init__(self, arg_nodes):
        self.arg_nodes = arg_nodes

    def __repr__(self):
        return f'CALL_CJ({self.arg_nodes})'


# ==============================================================================
# 5. RECURSIVE DESCENT PARSER
# ==============================================================================

class Parser:
    """Parses token streams into an Abstract Syntax Tree enforcing Rockstarlang grammar."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.current_tok = None
        self.advance()

    def advance(self):
        """Moves the parser pointer to the next token in the stream."""
        self.tok_idx += 1
        self.current_tok = self.tokens[self.tok_idx] if self.tok_idx < len(self.tokens) else None
        return self.current_tok

    def skip_newlines(self):
        """Consumes consecutive newline tokens between statements or blocks."""
        while self.current_tok is not None and self.current_tok.type == TT_NEWLINE:
            self.advance()

    def parse(self):
        """Entry point for parsing: validates GTA52013...GTA62026 block boundaries."""
        self.skip_newlines()

        # Verify program opening block
        if not (self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'GTA52013'):
            return None, "WASTED! Program must start with 'GTA52013'"
        self.advance()

        if self.current_tok.type != TT_NEWLINE:
            return None, "WASTED! Expected newline after 'GTA52013'"
        self.skip_newlines()

        # Parse all indented statements inside the main block
        statements = []
        while self.current_tok is not None and self.current_tok.type == TT_TAB:
            self.advance()  # Consume leading indentation

            if self.current_tok.type == TT_NEWLINE:
                self.skip_newlines()
                continue

            stmt, error = self.statement()
            if error:
                return None, error
            statements.append(stmt)

            if self.current_tok.type == TT_NEWLINE:
                self.skip_newlines()
            elif not (self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'GTA62026'):
                return None, "WASTED! Expected newline after statement"

        # Verify program closing block
        if not (self.current_tok is not None and self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'GTA62026'):
            return None, "WASTED! Program must end with 'GTA62026'"
        self.advance()

        self.skip_newlines()
        if self.current_tok.type != TT_EOF:
            return None, "WASTED! Unexpected code after 'GTA62026'"

        return statements, None

    def statement(self):
        """Parses individual statements inside an indented mission block."""
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'call_CJ':
            self.advance()

            if self.current_tok.type != TT_LPAREN:
                return None, "WASTED! Expected '(' after 'call_CJ'"
            self.advance()

            arg_nodes = []
            if self.current_tok.type != TT_RPAREN:
                arg, error = self.expr()
                if error:
                    return None, error
                arg_nodes.append(arg)

                while self.current_tok.type == TT_COMMA:
                    self.advance()
                    arg, error = self.expr()
                    if error:
                        return None, error
                    arg_nodes.append(arg)

            if self.current_tok.type != TT_RPAREN:
                return None, "WASTED! Expected ')' after arguments"
            self.advance()

            return PrintNode(arg_nodes), None

        return None, f"WASTED! Unknown statement '{self.current_tok}'"

    # --- Arithmetic Expression Grammar (BODMAS Precedence) ---

    def factor(self):
        """Parses atomic values: literals, unary signs (+/-), and parenthesized expressions."""
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            self.advance()
            node, error = self.factor()
            if error:
                return None, error
            return BinOpNode(NumberNode(Token(TT_INT, 0)), tok, node), None

        if tok.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(tok), None

        if tok.type == TT_STRING:
            self.advance()
            return StringNode(tok), None

        if tok.type == TT_LPAREN:
            self.advance()
            node, error = self.expr()
            if error:
                return None, error
            if self.current_tok.type != TT_RPAREN:
                return None, "WASTED! Expected ')'"
            self.advance()
            return node, None

        return None, f"WASTED! Expected number, string, or '(', got '{tok}'"

    def term(self):
        """Parses high-precedence multiplicative operations (* and /)."""
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        """Parses low-precedence additive operations (+ and -)."""
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func, ops):
        """Helper method for left-associative binary operator parsing."""
        left, error = func()
        if error:
            return None, error

        while self.current_tok is not None and self.current_tok.type in ops:
            op_tok = self.current_tok
            self.advance()
            right, error = func()
            if error:
                return None, error
            left = BinOpNode(left, op_tok, right)

        return left, None


# ==============================================================================
# 6. TREE-WALK INTERPRETER
# ==============================================================================

class Interpreter:
    """Traverses the AST and executes Rockstarlang statements at runtime."""

    def visit(self, node):
        """Dynamically dispatches execution to the appropriate visit_<NodeType> method."""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name)
        return method(node)

    def visit_NumberNode(self, node):
        return node.tok.value, None

    def visit_StringNode(self, node):
        return node.tok.value, None

    def visit_BinOpNode(self, node):
        left, error = self.visit(node.left_node)
        if error:
            return None, error
        right, error = self.visit(node.right_node)
        if error:
            return None, error

        if node.op_tok.type == TT_PLUS:
            return left + right, None
        if node.op_tok.type == TT_MINUS:
            return left - right, None
        if node.op_tok.type == TT_MUL:
            return left * right, None
        if node.op_tok.type == TT_DIV:
            if right == 0:
                return None, "WASTED! RuntimeError: Division by zero"
            return left / right, None

    def visit_PrintNode(self, node):
        values = []
        for arg in node.arg_nodes:
            val, error = self.visit(arg)
            if error:
                return None, error
            values.append(val)

        print(*values)
        return None, None


# ==============================================================================
# 7. EXECUTION PIPELINE ENTRY POINT
# ==============================================================================

def run(text):
    """Executes the full Lexer -> Parser -> Interpreter pipeline on source text."""
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    parser = Parser(tokens)
    ast, error = parser.parse()
    if error:
        return None, error

    interpreter = Interpreter()
    for stmt in ast:
        _, error = interpreter.visit(stmt)
        if error:
            return None, error

    return None, None
