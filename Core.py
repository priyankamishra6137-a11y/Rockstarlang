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

# Arithmetic, Comparison & Delimiter Tokens
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_LSQUARE = 'LSQUARE'
TT_RSQUARE = 'RSQUARE'
TT_CLPAREN = 'CLPAREN'
TT_CRPAREN = 'CRPAREN'
TT_COMMA = 'COMMA'
TT_COLON = 'COLON'
TT_EQ = 'EQ'
TT_EQUAL = 'EQUAL'
TT_NOT_EQUAL = 'NOT_EQUAL'
TT_LESS_THEN = 'LESS_THEN'
TT_GREATER_THAN = 'GREATER_THAN'
TT_LESS_EQUAL = 'LESS_EQUAL'
TT_GREATER_EQUAL = 'GREATER_EQUAL'

# Block Structure & Control Tokens
TT_NEWLINE = 'NEWLINE'
TT_TAB = 'TAB'
TT_EOF = 'EOF'

# Identifiers & Reserved Keywords
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'

KEYWORDS = {
    'GTA52013',
    'GTA62026',
    'call_CJ',
    'heist',        # Variable declaration & assignment
    'new_mission',  # Function definition
    'ask_Lester',
    'wanted',
    'heat_up',
    'lay_low',
    'on_the_run',
    'busted',
    'evade',
    'loot',
    'stash',
    'dossier'
}


# ==============================================================================
# 2. TOKEN REPRESENTATION & RUNTIME SIGNALS
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


class BreakSignal(Exception):
    """Internal control-flow signal raised by 'busted' inside a loop."""
    pass


class ContinueSignal(Exception):
    """Internal control-flow signal raised by 'evade' inside a loop."""
    pass


class ReturnSignal(Exception):
    """Internal control-flow signal raised by 'loot' inside a 'new_mission' function."""

    def __init__(self, value):
        self.value = value


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

            elif self.current_char == '=':
                tokens.append(self.make_equals())

            elif self.current_char == '<':
                tokens.append(self.make_less_than())

            elif self.current_char == '>':
                tokens.append(self.make_greater_than())

            elif self.current_char == '!':
                tok, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(tok)

            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA))
                self.advance()

            elif self.current_char == ':':
                tokens.append(Token(TT_COLON))
                self.advance()

            elif self.current_char in LETTERS:
                word_tok = self.make_word()
                if word_tok is not None:
                    tokens.append(word_tok)

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

            elif self.current_char == '[':
                tokens.append(Token(TT_LSQUARE))
                self.advance()

            elif self.current_char == ']':
                tokens.append(Token(TT_RSQUARE))
                self.advance()

            elif self.current_char == '{':
                tokens.append(Token(TT_CLPAREN))
                self.advance()

            elif self.current_char == '}':
                tokens.append(Token(TT_CRPAREN))
                self.advance()

            else:
                char = self.current_char
                err_line, err_col = self.line, self.col + 1
                self.advance()
                return [], f"WASTED! Illegal character '{char}' at Line {err_line}, Col {err_col}"

        tokens.append(Token(TT_EOF))
        return tokens, None

    def make_tab(self):
        """Counts leading spaces (1 tab = 4 spaces) and returns Token(TT_TAB, level)."""
        space_count = 0
        err_line = self.line

        while self.current_char is not None and self.current_char in ' \t':
            if self.current_char == '\t':
                space_count += 4
            else:
                space_count += 1
            self.advance()

        # Ignore whitespace-only blank lines
        if self.current_char == '\n' or self.current_char is None:
            return None, None

        # Ignore full-line 'RDR2' comments even when indented
        if self.text[self.pos:self.pos + 4] == 'RDR2' and (
            self.pos + 4 >= len(self.text) or self.text[self.pos + 4] not in LETTERS_DIGITS
        ):
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            return None, None

        if space_count % 4 != 0:
            return None, f"WASTED! IndentationError: Expected a multiple of 4 spaces at Line {err_line}"

        tab_level = space_count // 4
        return Token(TT_TAB, tab_level), None

    def make_word(self):
        """Scans alphanumeric words, handles 'RDR2' comments, and classifies tokens."""
        word_str = ''
        while self.current_char is not None and self.current_char in LETTERS_DIGITS:
            word_str += self.current_char
            self.advance()

        # Single-line comment trigger: skip everything until newline
        if word_str == 'RDR2':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            return None

        tok_type = TT_KEYWORD if word_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, word_str)

    def make_equals(self):
        """Distinguishes assignment '=' from equality comparison '=='."""
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_EQUAL)
        return Token(TT_EQ)

    def make_not_equals(self):
        """Validates and tokenizes inequality comparison '!='."""
        err_line = self.line
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_NOT_EQUAL), None
        return None, f"WASTED! Expected '=' after '!' at Line {err_line}"

    def make_less_than(self):
        """Distinguishes '<' from '<='."""
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_LESS_EQUAL)
        return Token(TT_LESS_THEN)

    def make_greater_than(self):
        """Distinguishes '>' from '>='."""
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_GREATER_EQUAL)
        return Token(TT_GREATER_THAN)

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


class ListNode:
    """AST node representing a 'stash[...]' array literal."""

    def __init__(self, element_nodes):
        self.element_nodes = element_nodes

    def __repr__(self):
        return f'STASH{self.element_nodes}'


class DictNode:
    """AST node representing a 'dossier{key: val, ...}' dictionary literal."""

    def __init__(self, pair_nodes):
        self.pair_nodes = pair_nodes

    def __repr__(self):
        return f'DOSSIER{self.pair_nodes}'


class IndexAccessNode:
    """AST node representing list/dict indexing: target[key_or_index]"""

    def __init__(self, target_node, index_node):
        self.target_node = target_node
        self.index_node = index_node

    def __repr__(self):
        return f'{self.target_node}[{self.index_node}]'


class IndexAssignNode:
    """AST node representing list/dict element assignment: heist x[k] = <expr>"""

    def __init__(self, var_name_tok, index_node, value_node):
        self.var_name_tok = var_name_tok
        self.index_node = index_node
        self.value_node = value_node

    def __repr__(self):
        return f'(SET {self.var_name_tok.value}[{self.index_node}] = {self.value_node})'


class BinOpNode:
    """AST node representing a binary arithmetic or comparison operation."""

    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class PrintNode:
    """AST node representing a 'call_CJ' output statement."""

    def __init__(self, arg_nodes):
        self.arg_nodes = arg_nodes

    def __repr__(self):
        return f'CALL_CJ({self.arg_nodes})'


class VarAssignNode:
    """AST node representing variable assignment: heist x = <expr>"""

    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

    def __repr__(self):
        return f'(SET {self.var_name_tok.value} = {self.value_node})'


class VarAccessNode:
    """AST node representing variable lookup inside expressions."""

    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

    def __repr__(self):
        return f'VAR({self.var_name_tok.value})'


class InputNode:
    """AST node representing user input: ask_Lester("prompt")"""

    def __init__(self, prompt_node=None):
        self.prompt_node = prompt_node

    def __repr__(self):
        return f'ASK_LESTER({self.prompt_node})'


class IfNode:
    """AST node representing wanted / heat_up / lay_low conditional branching."""

    def __init__(self, cases, else_case=None):
        self.cases = cases
        self.else_case = else_case

    def __repr__(self):
        return f'WANTED({self.cases}, ELSE={self.else_case})'


class WhileNode:
    """AST node representing an 'on_the_run <cond>:' loop."""

    def __init__(self, condition_node, body_nodes):
        self.condition_node = condition_node
        self.body_nodes = body_nodes

    def __repr__(self):
        return f'ON_THE_RUN({self.condition_node}, {self.body_nodes})'


class BreakNode:
    """AST node representing 'busted' (break out of loop)."""
    pass


class ContinueNode:
    """AST node representing 'evade' (skip to next loop iteration)."""
    pass


class FuncDefNode:
    """AST node representing a 'new_mission name(arg1, arg2):' function definition."""

    def __init__(self, func_name_tok, arg_name_toks, body_nodes):
        self.func_name_tok = func_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_nodes = body_nodes

    def __repr__(self):
        return f'NEW_MISSION {self.func_name_tok.value}({self.arg_name_toks})'


class FuncCallNode:
    """AST node representing a function call: target(arg1, arg2, ...)"""

    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

    def __repr__(self):
        return f'CALL({self.node_to_call}, {self.arg_nodes})'


class ReturnNode:
    """AST node representing 'loot <expr>' return statement."""

    def __init__(self, value_node=None):
        self.value_node = value_node

    def __repr__(self):
        return f'LOOT({self.value_node})'


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

        if not (self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'GTA52013'):
            return None, "WASTED! Program must start with 'GTA52013'"
        self.advance()

        if self.current_tok.type != TT_NEWLINE:
            return None, "WASTED! Expected newline after 'GTA52013'"
        self.skip_newlines()

        statements, error = self.parse_block(1)
        if error:
            return None, error

        if not (self.current_tok is not None and self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'GTA62026'):
            return None, "WASTED! Program must end with 'GTA62026'"
        self.advance()

        self.skip_newlines()
        if self.current_tok.type != TT_EOF:
            return None, "WASTED! Unexpected code after 'GTA62026'"

        return statements, None

    def parse_block(self, expected_indent):
        """Parses all consecutive statements indented at `expected_indent` level."""
        statements = []

        while self.current_tok is not None:
            self.skip_newlines()

            if self.current_tok.type == TT_TAB:
                if self.current_tok.value == expected_indent:
                    self.advance()
                    stmt, error = self.statement(expected_indent)
                    if error:
                        return None, error
                    statements.append(stmt)

                    if (
                        self.current_tok is not None
                        and self.current_tok.type not in (TT_NEWLINE, TT_TAB, TT_EOF)
                        and not (self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'GTA62026')
                    ):
                        return None, "WASTED! Expected newline after statement"
                elif self.current_tok.value < expected_indent:
                    break
                else:
                    return None, f"WASTED! Unexpected indentation (expected {expected_indent * 4} spaces)"
            else:
                break

        if not statements:
            return None, "WASTED! Expected at least one indented statement inside block"

        return statements, None

    def statement(self, indent_level):
        """Parses individual statements inside an indented mission block."""
        # 1. Print Statement: call_CJ (...)
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

        # 2. Variable / List / Dict Element Assignment: heist x = <expr> or heist x[k] = <expr>
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'heist':
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return None, "WASTED! Expected variable name after 'heist'"
            var_name = self.current_tok
            self.advance()

            index_node = None
            if self.current_tok.type == TT_LSQUARE:
                self.advance()
                index_node, error = self.expr()
                if error:
                    return None, error
                if self.current_tok.type != TT_RSQUARE:
                    return None, "WASTED! Expected ']' after key/index"
                self.advance()

            if self.current_tok.type != TT_EQ:
                return None, f"WASTED! Expected '=' after '{var_name.value}'"
            self.advance()

            val_node, error = self.expr()
            if error:
                return None, error

            if index_node is not None:
                return IndexAssignNode(var_name, index_node, val_node), None
            return VarAssignNode(var_name, val_node), None

        # 3. Conditional Branching: wanted / heat_up / lay_low
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'wanted':
            return self.if_expr(indent_level)

        # 4. While Loop: on_the_run <cond>:
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'on_the_run':
            return self.while_expr(indent_level)

        # 5. Loop Control: busted / evade
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'busted':
            self.advance()
            return BreakNode(), None

        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'evade':
            self.advance()
            return ContinueNode(), None

        # 6. Function Definition: new_mission name(arg1, arg2):
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'new_mission':
            return self.func_def(indent_level)

        # 7. Function Return: loot <expr>
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'loot':
            self.advance()
            if self.current_tok is not None and self.current_tok.type not in (TT_NEWLINE, TT_EOF):
                val_node, error = self.expr()
                if error:
                    return None, error
                return ReturnNode(val_node), None
            return ReturnNode(None), None

        # 8. Standalone Expression / Function Call Statement (e.g., my_mission(10, 20))
        expr_node, error = self.expr()
        if error:
            return None, error
        return expr_node, None

    def if_expr(self, indent_level):
        """Parses 'wanted <cond>:', optional 'heat_up <cond>:', and optional 'lay_low:' blocks."""
        cases = []
        else_case = None

        self.advance()
        condition, error = self.expr()
        if error:
            return None, error

        if self.current_tok.type != TT_COLON:
            return None, "WASTED! Expected ':' after 'wanted' condition"
        self.advance()

        if self.current_tok.type != TT_NEWLINE:
            return None, "WASTED! Expected newline after ':'"
        self.skip_newlines()

        body, error = self.parse_block(indent_level + 1)
        if error:
            return None, error
        cases.append((condition, body))

        while (
            self.current_tok is not None
            and self.current_tok.type == TT_TAB
            and self.current_tok.value == indent_level
            and self.tok_idx + 1 < len(self.tokens)
            and self.tokens[self.tok_idx + 1].type == TT_KEYWORD
            and self.tokens[self.tok_idx + 1].value == 'heat_up'
        ):
            self.advance()
            self.advance()

            condition, error = self.expr()
            if error:
                return None, error

            if self.current_tok.type != TT_COLON:
                return None, "WASTED! Expected ':' after 'heat_up' condition"
            self.advance()

            if self.current_tok.type != TT_NEWLINE:
                return None, "WASTED! Expected newline after ':'"
            self.skip_newlines()

            body, error = self.parse_block(indent_level + 1)
            if error:
                return None, error
            cases.append((condition, body))

        if (
            self.current_tok is not None
            and self.current_tok.type == TT_TAB
            and self.current_tok.value == indent_level
            and self.tok_idx + 1 < len(self.tokens)
            and self.tokens[self.tok_idx + 1].type == TT_KEYWORD
            and self.tokens[self.tok_idx + 1].value == 'lay_low'
        ):
            self.advance()
            self.advance()

            if self.current_tok.type != TT_COLON:
                return None, "WASTED! Expected ':' after 'lay_low'"
            self.advance()

            if self.current_tok.type != TT_NEWLINE:
                return None, "WASTED! Expected newline after ':'"
            self.skip_newlines()

            else_case, error = self.parse_block(indent_level + 1)
            if error:
                return None, error

        return IfNode(cases, else_case), None

    def while_expr(self, indent_level):
        """Parses 'on_the_run <condition>:' loop blocks."""
        self.advance()
        condition, error = self.expr()
        if error:
            return None, error

        if self.current_tok.type != TT_COLON:
            return None, "WASTED! Expected ':' after 'on_the_run' condition"
        self.advance()

        if self.current_tok.type != TT_NEWLINE:
            return None, "WASTED! Expected newline after ':'"
        self.skip_newlines()

        body, error = self.parse_block(indent_level + 1)
        if error:
            return None, error

        return WhileNode(condition, body), None

    def func_def(self, indent_level):
        """Parses 'new_mission func_name(param1, param2):' function definitions."""
        self.advance()  # Consume 'new_mission'

        if self.current_tok.type != TT_IDENTIFIER:
            return None, "WASTED! Expected mission (function) name after 'new_mission'"
        func_name_tok = self.current_tok
        self.advance()

        if self.current_tok.type != TT_LPAREN:
            return None, f"WASTED! Expected '(' after '{func_name_tok.value}'"
        self.advance()

        arg_name_toks = []
        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            self.advance()

            while self.current_tok.type == TT_COMMA:
                self.advance()
                if self.current_tok.type != TT_IDENTIFIER:
                    return None, "WASTED! Expected parameter name after ','"
                arg_name_toks.append(self.current_tok)
                self.advance()

        if self.current_tok.type != TT_RPAREN:
            return None, "WASTED! Expected ')' after mission parameters"
        self.advance()

        if self.current_tok.type != TT_COLON:
            return None, "WASTED! Expected ':' after mission signature"
        self.advance()

        if self.current_tok.type != TT_NEWLINE:
            return None, "WASTED! Expected newline after ':'"
        self.skip_newlines()

        body, error = self.parse_block(indent_level + 1)
        if error:
            return None, error

        return FuncDefNode(func_name_tok, arg_name_toks, body), None

    def list_expr(self):
        """Parses 'stash[elem1, elem2, ...]' array literals."""
        self.advance()

        if self.current_tok.type != TT_LSQUARE:
            return None, "WASTED! Expected '[' after 'stash'"
        self.advance()

        elements = []
        if self.current_tok.type != TT_RSQUARE:
            elem, error = self.expr()
            if error:
                return None, error
            elements.append(elem)

            while self.current_tok.type == TT_COMMA:
                self.advance()
                elem, error = self.expr()
                if error:
                    return None, error
                elements.append(elem)

        if self.current_tok.type != TT_RSQUARE:
            return None, "WASTED! Expected ']' at end of stash"
        self.advance()

        return ListNode(elements), None

    def dict_expr(self):
        """Parses 'dossier{key: value, ...}' dictionary literals."""
        self.advance()

        if self.current_tok.type != TT_CLPAREN:
            return None, "WASTED! Expected '{' after 'dossier'"
        self.advance()

        pairs = []
        if self.current_tok.type != TT_CRPAREN:
            key_node, error = self.expr()
            if error:
                return None, error
            if self.current_tok.type != TT_COLON:
                return None, "WASTED! Expected ':' after dossier key"
            self.advance()
            val_node, error = self.expr()
            if error:
                return None, error
            pairs.append((key_node, val_node))

            while self.current_tok.type == TT_COMMA:
                self.advance()
                key_node, error = self.expr()
                if error:
                    return None, error
                if self.current_tok.type != TT_COLON:
                    return None, "WASTED! Expected ':' after dossier key"
                self.advance()
                val_node, error = self.expr()
                if error:
                    return None, error
                pairs.append((key_node, val_node))

        if self.current_tok.type != TT_CRPAREN:
            return None, "WASTED! Expected '}' at end of dossier"
        self.advance()

        return DictNode(pairs), None

    # --- Expression Grammar (BODMAS, Postfix Calls/Indexing & Comparison) ---

    def atom(self):
        """Parses atomic values: literals, variables, stash, dossier, ask_Lester, parens."""
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(tok), None

        if tok.type == TT_STRING:
            self.advance()
            return StringNode(tok), None

        if tok.type == TT_IDENTIFIER:
            self.advance()
            return VarAccessNode(tok), None

        if tok.type == TT_KEYWORD and tok.value == 'stash':
            return self.list_expr()

        if tok.type == TT_KEYWORD and tok.value == 'dossier':
            return self.dict_expr()

        if tok.type == TT_KEYWORD and tok.value == 'ask_Lester':
            self.advance()
            if self.current_tok.type != TT_LPAREN:
                return None, "WASTED! Expected '(' after 'ask_Lester'"
            self.advance()

            prompt_node = None
            if self.current_tok.type != TT_RPAREN:
                prompt_node, error = self.expr()
                if error:
                    return None, error

            if self.current_tok.type != TT_RPAREN:
                return None, "WASTED! Expected ')' after ask_Lester prompt"
            self.advance()
            return InputNode(prompt_node), None

        if tok.type == TT_LPAREN:
            self.advance()
            node, error = self.expr()
            if error:
                return None, error
            if self.current_tok.type != TT_RPAREN:
                return None, "WASTED! Expected ')'"
            self.advance()
            return node, None

        return None, f"WASTED! Expected value, variable, or '(', got '{tok}'"

    def postfix(self):
        """Handles chained indexing arr[i] and function calls func(a, b)."""
        node, error = self.atom()
        if error:
            return None, error

        while self.current_tok is not None and self.current_tok.type in (TT_LSQUARE, TT_LPAREN):
            if self.current_tok.type == TT_LSQUARE:
                self.advance()
                index_node, error = self.expr()
                if error:
                    return None, error
                if self.current_tok.type != TT_RSQUARE:
                    return None, "WASTED! Expected ']' after key/index"
                self.advance()
                node = IndexAccessNode(node, index_node)

            elif self.current_tok.type == TT_LPAREN:
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
                    return None, "WASTED! Expected ')' after mission arguments"
                self.advance()
                node = FuncCallNode(node, arg_nodes)

        return node, None

    def factor(self):
        """Handles unary +/- signs before postfix expressions."""
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            self.advance()
            node, error = self.factor()
            if error:
                return None, error
            return BinOpNode(NumberNode(Token(TT_INT, 0)), tok, node), None

        return self.postfix()

    def term(self):
        """Parses high-precedence multiplicative operations (* and /)."""
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def arith_expr(self):
        """Parses additive arithmetic operations (+ and -)."""
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def expr(self):
        """Parses comparison operations (==, !=, <, >, <=, >=)."""
        return self.bin_op(
            self.arith_expr,
            (TT_EQUAL, TT_NOT_EQUAL, TT_LESS_THEN, TT_GREATER_THAN, TT_LESS_EQUAL, TT_GREATER_EQUAL)
        )

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
# 6. RUNTIME FUNCTION & TREE-WALK INTERPRETER
# ==============================================================================

class RockstarFunction:
    """Represents a user-defined 'new_mission' function at runtime."""

    def __init__(self, name, arg_names, body_nodes):
        self.name = name
        self.arg_names = arg_names
        self.body_nodes = body_nodes

    def __repr__(self):
        return f'<new_mission {self.name}>'


class Interpreter:
    """Traverses the AST and executes Rockstarlang statements with scoped memory."""

    def __init__(self):
        self.global_symbols = {}
        self.scope_stack = [self.global_symbols]

    @property
    def current_scope(self):
        return self.scope_stack[-1]

    def get_var(self, name):
        """Looks up a variable from innermost local scope out to global scope."""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name], True
        return None, False

    def visit(self, node):
        """Dynamically dispatches execution to the appropriate visit_<NodeType> method."""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name)
        return method(node)

    def visit_NumberNode(self, node):
        return node.tok.value, None

    def visit_StringNode(self, node):
        return node.tok.value, None

    def visit_ListNode(self, node):
        elements = []
        for elem_node in node.element_nodes:
            val, error = self.visit(elem_node)
            if error:
                return None, error
            elements.append(val)
        return elements, None

    def visit_DictNode(self, node):
        dossier_map = {}
        for key_node, val_node in node.pair_nodes:
            key, error = self.visit(key_node)
            if error:
                return None, error
            val, error = self.visit(val_node)
            if error:
                return None, error
            dossier_map[key] = val
        return dossier_map, None

    def visit_IndexAccessNode(self, node):
        target, error = self.visit(node.target_node)
        if error:
            return None, error
        index, error = self.visit(node.index_node)
        if error:
            return None, error

        try:
            return target[index], None
        except (IndexError, KeyError, TypeError) as exc:
            return None, f"WASTED! LookupError: {exc}"

    def visit_IndexAssignNode(self, node):
        var_name = node.var_name_tok.value
        container, found = self.get_var(var_name)
        if not found:
            return None, f"WASTED! NameError: Heist variable '{var_name}' is not defined"

        index, error = self.visit(node.index_node)
        if error:
            return None, error
        val, error = self.visit(node.value_node)
        if error:
            return None, error

        try:
            container[index] = val
            return val, None
        except (IndexError, KeyError, TypeError) as exc:
            return None, f"WASTED! AssignmentError: {exc}"

    def visit_BinOpNode(self, node):
        left, error = self.visit(node.left_node)
        if error:
            return None, error
        right, error = self.visit(node.right_node)
        if error:
            return None, error

        op = node.op_tok.type

        if op == TT_PLUS:
            return left + right, None
        if op == TT_MINUS:
            return left - right, None
        if op == TT_MUL:
            return left * right, None
        if op == TT_DIV:
            if right == 0:
                return None, "WASTED! RuntimeError: Division by zero"
            return left / right, None
        if op == TT_EQUAL:
            return left == right, None
        if op == TT_NOT_EQUAL:
            return left != right, None
        if op == TT_LESS_THEN:
            return left < right, None
        if op == TT_GREATER_THAN:
            return left > right, None
        if op == TT_LESS_EQUAL:
            return left <= right, None
        if op == TT_GREATER_EQUAL:
            return left >= right, None

    def visit_PrintNode(self, node):
        values = []
        for arg in node.arg_nodes:
            val, error = self.visit(arg)
            if error:
                return None, error
            values.append(val)

        print(*values)
        return None, None

    def visit_VarAssignNode(self, node):
        var_name = node.var_name_tok.value
        val, error = self.visit(node.value_node)
        if error:
            return None, error
        self.current_scope[var_name] = val
        return val, None

    def visit_VarAccessNode(self, node):
        var_name = node.var_name_tok.value
        val, found = self.get_var(var_name)
        if not found:
            return None, f"WASTED! NameError: Heist variable '{var_name}' is not defined"
        return val, None

    def visit_InputNode(self, node):
        prompt = ""
        if node.prompt_node is not None:
            prompt_val, error = self.visit(node.prompt_node)
            if error:
                return None, error
            prompt = str(prompt_val)

        user_val = input(prompt)
        if user_val.isdigit():
            return int(user_val), None
        try:
            return float(user_val), None
        except ValueError:
            return user_val, None

    def visit_IfNode(self, node):
        for condition, body in node.cases:
            cond_val, error = self.visit(condition)
            if error:
                return None, error

            if bool(cond_val):
                for stmt in body:
                    _, error = self.visit(stmt)
                    if error:
                        return None, error
                return None, None

        if node.else_case is not None:
            for stmt in node.else_case:
                _, error = self.visit(stmt)
                if error:
                    return None, error

        return None, None

    def visit_WhileNode(self, node):
        while True:
            cond_val, error = self.visit(node.condition_node)
            if error:
                return None, error

            if not bool(cond_val):
                break

            try:
                for stmt in node.body_nodes:
                    _, error = self.visit(stmt)
                    if error:
                        return None, error
            except ContinueSignal:
                continue
            except BreakSignal:
                break

        return None, None

    def visit_BreakNode(self, node):
        raise BreakSignal()

    def visit_ContinueNode(self, node):
        raise ContinueSignal()

    def visit_FuncDefNode(self, node):
        func_name = node.func_name_tok.value
        arg_names = [tok.value for tok in node.arg_name_toks]
        func_obj = RockstarFunction(func_name, arg_names, node.body_nodes)
        self.current_scope[func_name] = func_obj
        return func_obj, None

    def visit_FuncCallNode(self, node):
        func_obj, error = self.visit(node.node_to_call)
        if error:
            return None, error

        if not isinstance(func_obj, RockstarFunction):
            return None, f"WASTED! TypeError: '{func_obj}' is not a callable mission"

        if len(node.arg_nodes) != len(func_obj.arg_names):
            return None, (
                f"WASTED! ArgumentError: Mission '{func_obj.name}' expects "
                f"{len(func_obj.arg_names)} arguments, got {len(node.arg_nodes)}"
            )

        evaluated_args = []
        for arg_node in node.arg_nodes:
            val, error = self.visit(arg_node)
            if error:
                return None, error
            evaluated_args.append(val)

        # Create isolated local call frame
        local_scope = dict(zip(func_obj.arg_names, evaluated_args))
        self.scope_stack.append(local_scope)

        return_val = None
        try:
            for stmt in func_obj.body_nodes:
                _, error = self.visit(stmt)
                if error:
                    return None, error
        except ReturnSignal as ret:
            return_val = ret.value
        finally:
            self.scope_stack.pop()

        return return_val, None

    def visit_ReturnNode(self, node):
        val = None
        if node.value_node is not None:
            val, error = self.visit(node.value_node)
            if error:
                return None, error
        raise ReturnSignal(val)


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
        try:
            _, error = interpreter.visit(stmt)
            if error:
                return None, error
        except (BreakSignal, ContinueSignal):
            return None, "WASTED! SyntaxError: 'busted' or 'evade' used outside 'on_the_run' loop"
        except ReturnSignal:
            return None, "WASTED! SyntaxError: 'loot' used outside 'new_mission' function"

    return None, None
