"""
Rockstarlang Core Engine (v0.5 - Phase 2: OOP & Standard Libraries)
------------------------------------------------------------------
A Rockstar Games-inspired esoteric programming language pipeline built from scratch.
Implements a three-stage execution architecture:
    1. Lexer       : Converts raw .rsl source code into a stream of lexical tokens.
    2. Parser      : Validates block grammar (GTA52013...GTA62026) and constructs an AST.
    3. Interpreter : Walks the AST with scoped memory, OOP instances, and native modules.
"""

import os
import sys
import math
import time
import json
import random
import threading

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
TT_DOT = 'DOT'
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
    'new_mission',  # Function / method definition
    'ask_Lester',
    'wanted',
    'heat_up',
    'lay_low',
    'on_the_run',
    'busted',
    'evade',
    'loot',
    'stash',
    'dossier',
    'gang',         # Class definition
    'blueprint',    # Struct definition
    'recruit',      # Object instantiation
    'hire',         # Module / .rsl import
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

            elif self.current_char == '.':
                tokens.append(Token(TT_DOT))
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

        if self.current_char == '\n' or self.current_char is None:
            return None, None

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

        if word_str == 'RDR2':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            return None

        tok_type = TT_KEYWORD if word_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, word_str)

    def make_equals(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_EQUAL)
        return Token(TT_EQ)

    def make_not_equals(self):
        err_line = self.line
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_NOT_EQUAL), None
        return None, f"WASTED! Expected '=' after '!' at Line {err_line}"

    def make_less_than(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_LESS_EQUAL)
        return Token(TT_LESS_THEN)

    def make_greater_than(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_GREATER_EQUAL)
        return Token(TT_GREATER_THAN)

    def make_number(self):
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
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class ListNode:
    def __init__(self, element_nodes):
        self.element_nodes = element_nodes

    def __repr__(self):
        return f'STASH{self.element_nodes}'


class DictNode:
    def __init__(self, pair_nodes):
        self.pair_nodes = pair_nodes

    def __repr__(self):
        return f'DOSSIER{self.pair_nodes}'


class IndexAccessNode:
    def __init__(self, target_node, index_node):
        self.target_node = target_node
        self.index_node = index_node

    def __repr__(self):
        return f'{self.target_node}[{self.index_node}]'


class IndexAssignNode:
    def __init__(self, target_node, index_node, value_node):
        self.target_node = target_node
        self.index_node = index_node
        self.value_node = value_node

    def __repr__(self):
        return f'(SET {self.target_node}[{self.index_node}] = {self.value_node})'


class MemberAccessNode:
    def __init__(self, target_node, member_tok):
        self.target_node = target_node
        self.member_tok = member_tok

    def __repr__(self):
        return f'{self.target_node}.{self.member_tok.value}'


class MemberAssignNode:
    def __init__(self, target_node, member_tok, value_node):
        self.target_node = target_node
        self.member_tok = member_tok
        self.value_node = value_node

    def __repr__(self):
        return f'(SET {self.target_node}.{self.member_tok.value} = {self.value_node})'


class StructDefNode:
    def __init__(self, struct_name_tok, field_toks):
        self.struct_name_tok = struct_name_tok
        self.field_toks = field_toks

    def __repr__(self):
        return f'BLUEPRINT {self.struct_name_tok.value}({self.field_toks})'


class ClassDefNode:
    def __init__(self, class_name_tok, method_nodes):
        self.class_name_tok = class_name_tok
        self.method_nodes = method_nodes

    def __repr__(self):
        return f'GANG {self.class_name_tok.value}'


class RecruitNode:
    def __init__(self, class_name_tok, arg_nodes):
        self.class_name_tok = class_name_tok
        self.arg_nodes = arg_nodes

    def __repr__(self):
        return f'RECRUIT {self.class_name_tok.value}({self.arg_nodes})'


class HireNode:
    """AST node representing 'hire <module>' or 'hire "file.rsl"' import statements."""

    def __init__(self, target_tok, is_file=False):
        self.target_tok = target_tok
        self.is_file = is_file

    def __repr__(self):
        return f'HIRE({self.target_tok.value})'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class PrintNode:
    def __init__(self, arg_nodes):
        self.arg_nodes = arg_nodes

    def __repr__(self):
        return f'CALL_CJ({self.arg_nodes})'


class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

    def __repr__(self):
        return f'(SET {self.var_name_tok.value} = {self.value_node})'


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

    def __repr__(self):
        return f'VAR({self.var_name_tok.value})'


class InputNode:
    def __init__(self, prompt_node=None):
        self.prompt_node = prompt_node

    def __repr__(self):
        return f'ASK_LESTER({self.prompt_node})'


class IfNode:
    def __init__(self, cases, else_case=None):
        self.cases = cases
        self.else_case = else_case

    def __repr__(self):
        return f'WANTED({self.cases}, ELSE={self.else_case})'


class WhileNode:
    def __init__(self, condition_node, body_nodes):
        self.condition_node = condition_node
        self.body_nodes = body_nodes

    def __repr__(self):
        return f'ON_THE_RUN({self.condition_node}, {self.body_nodes})'


class BreakNode:
    pass


class ContinueNode:
    pass


class FuncDefNode:
    def __init__(self, func_name_tok, arg_name_toks, body_nodes):
        self.func_name_tok = func_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_nodes = body_nodes

    def __repr__(self):
        return f'NEW_MISSION {self.func_name_tok.value}({self.arg_name_toks})'


class FuncCallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

    def __repr__(self):
        return f'CALL({self.node_to_call}, {self.arg_nodes})'


class ReturnNode:
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
        self.tok_idx += 1
        self.current_tok = self.tokens[self.tok_idx] if self.tok_idx < len(self.tokens) else None
        return self.current_tok

    def skip_newlines(self):
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

        # 2. Variable / Member / Index Assignment: heist x = <expr>
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'heist':
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return None, "WASTED! Expected target name after 'heist'"
            target_node = VarAccessNode(self.current_tok)
            root_tok = self.current_tok
            self.advance()

            while self.current_tok is not None and self.current_tok.type in (TT_DOT, TT_LSQUARE):
                if self.current_tok.type == TT_DOT:
                    self.advance()
                    if self.current_tok.type != TT_IDENTIFIER:
                        return None, "WASTED! Expected field name after '.'"
                    member_tok = self.current_tok
                    self.advance()
                    target_node = MemberAccessNode(target_node, member_tok)
                elif self.current_tok.type == TT_LSQUARE:
                    self.advance()
                    index_node, error = self.expr()
                    if error:
                        return None, error
                    if self.current_tok.type != TT_RSQUARE:
                        return None, "WASTED! Expected ']' after key/index"
                    self.advance()
                    target_node = IndexAccessNode(target_node, index_node)

            if self.current_tok.type != TT_EQ:
                return None, "WASTED! Expected '=' in 'heist' assignment"
            self.advance()

            val_node, error = self.expr()
            if error:
                return None, error

            if isinstance(target_node, MemberAccessNode):
                return MemberAssignNode(target_node.target_node, target_node.member_tok, val_node), None
            if isinstance(target_node, IndexAccessNode):
                return IndexAssignNode(target_node.target_node, target_node.index_node, val_node), None
            return VarAssignNode(root_tok, val_node), None

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

        # 8. Struct Definition: blueprint Name(field1, field2)
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'blueprint':
            return self.struct_def()

        # 9. Class Definition: gang Name:
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'gang':
            return self.class_def(indent_level)

        # 10. Module / File Import: hire math | hire "weapons.rsl"
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'hire':
            self.advance()
            if self.current_tok.type == TT_IDENTIFIER:
                mod_tok = self.current_tok
                self.advance()
                return HireNode(mod_tok, is_file=False), None
            if self.current_tok.type == TT_STRING:
                file_tok = self.current_tok
                self.advance()
                return HireNode(file_tok, is_file=True), None
            return None, "WASTED! Expected module name or '.rsl' file string after 'hire'"

        # 11. Standalone Expression / Method or Function Call
        expr_node, error = self.expr()
        if error:
            return None, error
        return expr_node, None

    def struct_def(self):
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return None, "WASTED! Expected struct name after 'blueprint'"
        struct_name_tok = self.current_tok
        self.advance()

        if self.current_tok.type != TT_LPAREN:
            return None, f"WASTED! Expected '(' after '{struct_name_tok.value}'"
        self.advance()

        field_toks = []
        if self.current_tok.type == TT_IDENTIFIER:
            field_toks.append(self.current_tok)
            self.advance()

            while self.current_tok.type == TT_COMMA:
                self.advance()
                if self.current_tok.type != TT_IDENTIFIER:
                    return None, "WASTED! Expected field name after ','"
                field_toks.append(self.current_tok)
                self.advance()

        if self.current_tok.type != TT_RPAREN:
            return None, "WASTED! Expected ')' after blueprint fields"
        self.advance()

        return StructDefNode(struct_name_tok, field_toks), None

    def class_def(self, indent_level):
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return None, "WASTED! Expected gang (class) name after 'gang'"
        class_name_tok = self.current_tok
        self.advance()

        if self.current_tok.type != TT_COLON:
            return None, f"WASTED! Expected ':' after 'gang {class_name_tok.value}'"
        self.advance()

        if self.current_tok.type != TT_NEWLINE:
            return None, "WASTED! Expected newline after ':'"
        self.skip_newlines()

        body_nodes, error = self.parse_block(indent_level + 1)
        if error:
            return None, error

        for node in body_nodes:
            if not isinstance(node, FuncDefNode):
                return None, f"WASTED! Only 'new_mission' methods allowed inside 'gang {class_name_tok.value}'"

        return ClassDefNode(class_name_tok, body_nodes), None

    def if_expr(self, indent_level):
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
        self.advance()

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

    def recruit_expr(self):
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return None, "WASTED! Expected gang or blueprint name after 'recruit'"
        class_name_tok = self.current_tok
        self.advance()

        if self.current_tok.type != TT_LPAREN:
            return None, f"WASTED! Expected '(' after '{class_name_tok.value}'"
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
            return None, "WASTED! Expected ')' after recruit arguments"
        self.advance()

        return RecruitNode(class_name_tok, arg_nodes), None

    # --- Expression Grammar (BODMAS, Postfix Calls/Indexing/Dot & Comparison) ---

    def atom(self):
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

        if tok.type == TT_KEYWORD and tok.value == 'recruit':
            return self.recruit_expr()

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
        node, error = self.atom()
        if error:
            return None, error

        while self.current_tok is not None and self.current_tok.type in (TT_LSQUARE, TT_LPAREN, TT_DOT):
            if self.current_tok.type == TT_LSQUARE:
                self.advance()
                index_node, error = self.expr()
                if error:
                    return None, error
                if self.current_tok.type != TT_RSQUARE:
                    return None, "WASTED! Expected ']' after key/index"
                self.advance()
                node = IndexAccessNode(node, index_node)

            elif self.current_tok.type == TT_DOT:
                self.advance()
                if self.current_tok.type != TT_IDENTIFIER:
                    return None, "WASTED! Expected member name after '.'"
                member_tok = self.current_tok
                self.advance()
                node = MemberAccessNode(node, member_tok)

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
                    return None, "WASTED! Expected ')' after arguments"
                self.advance()
                node = FuncCallNode(node, arg_nodes)

        return node, None

    def factor(self):
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            self.advance()
            node, error = self.factor()
            if error:
                return None, error
            return BinOpNode(NumberNode(Token(TT_INT, 0)), tok, node), None

        return self.postfix()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def expr(self):
        return self.bin_op(
            self.arith_expr,
            (TT_EQUAL, TT_NOT_EQUAL, TT_LESS_THEN, TT_GREATER_THAN, TT_LESS_EQUAL, TT_GREATER_EQUAL)
        )

    def bin_op(self, func, ops):
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
# 6. RUNTIME OBJECTS, NATIVE MODULES & TREE-WALK INTERPRETER
# ==============================================================================

class RockstarFunction:
    """Represents a user-defined 'new_mission' function or bound method at runtime."""

    def __init__(self, name, arg_names, body_nodes, bound_instance=None):
        self.name = name
        self.arg_names = arg_names
        self.body_nodes = body_nodes
        self.bound_instance = bound_instance

    def __repr__(self):
        return f'<new_mission {self.name}>'


class NativeFunction:
    """Wraps a built-in Python callable for Rockstarlang standard modules."""

    def __init__(self, name, py_func):
        self.name = name
        self.py_func = py_func

    def __repr__(self):
        return f'<native_mission {self.name}>'


class RockstarModule:
    """Represents a standard library module imported via 'hire'."""

    def __init__(self, name, members):
        self.name = name
        self.members = members  # dict: member_name -> NativeFunction or constant

    def __repr__(self):
        return f'<module {self.name}>'


class RockstarStruct:
    def __init__(self, name, field_names):
        self.name = name
        self.field_names = field_names

    def __repr__(self):
        return f'<blueprint {self.name}>'


class RockstarClass:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def __repr__(self):
        return f'<gang {self.name}>'


class RockstarInstance:
    def __init__(self, type_name, methods=None, initial_fields=None):
        self.type_name = type_name
        self.methods = methods or {}
        self.fields = initial_fields or {}

    def __repr__(self):
        return f'<{self.type_name} {self.fields}>'


class Interpreter:
    """Traverses the AST and executes Rockstarlang statements with scoped memory, OOP & modules."""

    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.global_symbols = {}
        self.scope_stack = [self.global_symbols]
        self._last_frame_time = time.perf_counter()

    @property
    def current_scope(self):
        return self.scope_stack[-1]

    def get_var(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name], True
        return None, False

    def _build_stdlib_module(self, mod_name):
        """Constructs game-dev friendly native modules for 'hire <module>'."""
        if mod_name == 'math':
            return RockstarModule('math', {
                'pi': math.pi,
                'sin': NativeFunction('math.sin', lambda x: math.sin(x)),
                'cos': NativeFunction('math.cos', lambda x: math.cos(x)),
                'sqrt': NativeFunction('math.sqrt', lambda x: math.sqrt(x)),
                'abs': NativeFunction('math.abs', lambda x: abs(x)),
                'floor': NativeFunction('math.floor', lambda x: math.floor(x)),
                'ceil': NativeFunction('math.ceil', lambda x: math.ceil(x)),
                'dist': NativeFunction('math.dist', lambda x1, y1, x2, y2: math.hypot(x2 - x1, y2 - y1)),
                'rand': NativeFunction(
                    'math.rand',
                    lambda lo, hi: random.randint(lo, hi) if isinstance(lo, int) and isinstance(hi, int) else random.uniform(lo, hi)
                ),
                'clamp': NativeFunction('math.clamp', lambda val, lo, hi: max(lo, min(hi, val))),
            }), None

        if mod_name == 'time':
            def fps_limiter(target_fps):
                if target_fps <= 0:
                    return 0.0
                target_dt = 1.0 / target_fps
                now = time.perf_counter()
                elapsed = now - self._last_frame_time
                if elapsed < target_dt:
                    time.sleep(target_dt - elapsed)
                new_now = time.perf_counter()
                dt = new_now - self._last_frame_time
                self._last_frame_time = new_now
                return dt

            return RockstarModule('time', {
                'now': NativeFunction('time.now', lambda: time.time()),
                'wait': NativeFunction('time.wait', lambda sec: time.sleep(sec)),
                'fps': NativeFunction('time.fps', fps_limiter),
            }), None

        if mod_name == 'thread':
            def spawn_thread(mission_fn, *args):
                if not isinstance(mission_fn, RockstarFunction):
                    raise TypeError("thread.run() requires a 'new_mission' function as first argument")

                def worker():
                    # Execute on a dedicated child interpreter sharing global_symbols
                    worker_interp = Interpreter(base_dir=self.base_dir)
                    worker_interp.global_symbols = self.global_symbols
                    worker_interp.scope_stack = [self.global_symbols]
                    _, err = worker_interp._invoke_function(mission_fn, list(args))
                    if err:
                        print(f"[THREAD ERROR] {err}")

                t = threading.Thread(target=worker, daemon=True)
                t.start()
                return t.name

            return RockstarModule('thread', {
                'run': NativeFunction('thread.run', spawn_thread),
                'sleep': NativeFunction('thread.sleep', lambda sec: time.sleep(sec)),
            }), None

        if mod_name == 'json':
            def json_save(filepath, data):
                full_path = filepath if os.path.isabs(filepath) else os.path.join(self.base_dir, filepath)
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                return True

            def json_load(filepath):
                full_path = filepath if os.path.isabs(filepath) else os.path.join(self.base_dir, filepath)
                with open(full_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

            return RockstarModule('json', {
                'save': NativeFunction('json.save', json_save),
                'load': NativeFunction('json.load', json_load),
                'encode': NativeFunction('json.encode', lambda data: json.dumps(data)),
                'decode': NativeFunction('json.decode', lambda text: json.loads(text)),
            }), None

        if mod_name == 'os':
            def resolve_path(p):
                return p if os.path.isabs(p) else os.path.join(self.base_dir, p)

            return RockstarModule('os', {
                'exists': NativeFunction('os.exists', lambda p: os.path.exists(resolve_path(p))),
                'mkdir': NativeFunction('os.mkdir', lambda p: os.makedirs(resolve_path(p), exist_ok=True)),
                'remove': NativeFunction('os.remove', lambda p: os.remove(resolve_path(p)) if os.path.exists(resolve_path(p)) else None),
                'clear': NativeFunction('os.clear', lambda: os.system('cls' if os.name == 'nt' else 'clear')),
                'cwd': NativeFunction('os.cwd', lambda: os.getcwd()),
            }), None

        if mod_name == 'sys':
            def clean_exit(code=0):
                sys.exit(code)

            return RockstarModule('sys', {
                'args': NativeFunction('sys.args', lambda: list(sys.argv[1:])),
                'exit': NativeFunction('sys.exit', clean_exit),
                'platform': sys.platform,
            }), None

        return None, f"WASTED! ImportError: Unknown module '{mod_name}'"

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name)
        return method(node)

    def visit_HireNode(self, node):
        if not node.is_file:
            mod_name = node.target_tok.value
            mod_obj, error = self._build_stdlib_module(mod_name)
            if error:
                return None, error
            self.current_scope[mod_name] = mod_obj
            return mod_obj, None

        # Import external .rsl file into current symbol scope
        rel_path = node.target_tok.value
        full_path = rel_path if os.path.isabs(rel_path) else os.path.join(self.base_dir, rel_path)
        if not os.path.exists(full_path):
            return None, f"WASTED! ImportError: Mission file '{rel_path}' not found"

        with open(full_path, 'r', encoding='utf-8') as f:
            ext_code = f.read()

        lexer = Lexer(ext_code)
        tokens, error = lexer.make_tokens()
        if error:
            return None, error

        parser = Parser(tokens)
        ast, error = parser.parse()
        if error:
            return None, error

        for stmt in ast:
            _, error = self.visit(stmt)
            if error:
                return None, error

        return None, None

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
        container, error = self.visit(node.target_node)
        if error:
            return None, error
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

    def visit_MemberAccessNode(self, node):
        target, error = self.visit(node.target_node)
        if error:
            return None, error
        member_name = node.member_tok.value

        if isinstance(target, RockstarModule):
            if member_name in target.members:
                return target.members[member_name], None
            return None, f"WASTED! AttributeError: Module '{target.name}' has no member '{member_name}'"

        if isinstance(target, RockstarInstance):
            if member_name in target.fields:
                return target.fields[member_name], None
            if member_name in target.methods:
                raw_fn = target.methods[member_name]
                return RockstarFunction(
                    raw_fn.name,
                    raw_fn.arg_names,
                    raw_fn.body_nodes,
                    bound_instance=target
                ), None
            return None, f"WASTED! AttributeError: '{target.type_name}' has no member '{member_name}'"

        return None, f"WASTED! TypeError: Cannot access '.{member_name}' on '{target}'"

    def visit_MemberAssignNode(self, node):
        target, error = self.visit(node.target_node)
        if error:
            return None, error
        val, error = self.visit(node.value_node)
        if error:
            return None, error
        member_name = node.member_tok.value

        if isinstance(target, RockstarInstance):
            target.fields[member_name] = val
            return val, None

        return None, f"WASTED! TypeError: Cannot assign '.{member_name}' on '{target}'"

    def visit_StructDefNode(self, node):
        struct_name = node.struct_name_tok.value
        field_names = [tok.value for tok in node.field_toks]
        struct_obj = RockstarStruct(struct_name, field_names)
        self.current_scope[struct_name] = struct_obj
        return struct_obj, None

    def visit_ClassDefNode(self, node):
        class_name = node.class_name_tok.value
        methods = {}
        for m_node in node.method_nodes:
            m_name = m_node.func_name_tok.value
            m_args = [tok.value for tok in m_node.arg_name_toks]
            methods[m_name] = RockstarFunction(m_name, m_args, m_node.body_nodes)

        class_obj = RockstarClass(class_name, methods)
        self.current_scope[class_name] = class_obj
        return class_obj, None

    def visit_RecruitNode(self, node):
        type_name = node.class_name_tok.value
        blueprint_or_class, found = self.get_var(type_name)
        if not found:
            return None, f"WASTED! NameError: Gang or blueprint '{type_name}' is not defined"

        evaluated_args = []
        for arg_node in node.arg_nodes:
            val, error = self.visit(arg_node)
            if error:
                return None, error
            evaluated_args.append(val)

        if isinstance(blueprint_or_class, RockstarStruct):
            if len(evaluated_args) != len(blueprint_or_class.field_names):
                return None, (
                    f"WASTED! ArgumentError: Blueprint '{type_name}' expects "
                    f"{len(blueprint_or_class.field_names)} fields, got {len(evaluated_args)}"
                )
            fields = dict(zip(blueprint_or_class.field_names, evaluated_args))
            return RockstarInstance(type_name, initial_fields=fields), None

        if isinstance(blueprint_or_class, RockstarClass):
            instance = RockstarInstance(type_name, methods=blueprint_or_class.methods)
            if 'spawn' in blueprint_or_class.methods:
                spawn_fn = blueprint_or_class.methods['spawn']
                bound_spawn = RockstarFunction(
                    spawn_fn.name,
                    spawn_fn.arg_names,
                    spawn_fn.body_nodes,
                    bound_instance=instance
                )
                _, error = self._invoke_function(bound_spawn, evaluated_args)
                if error:
                    return None, error
            elif evaluated_args:
                return None, f"WASTED! ArgumentError: Gang '{type_name}' has no 'spawn' constructor"

            return instance, None

        return None, f"WASTED! TypeError: '{type_name}' cannot be recruited"

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

    def _invoke_function(self, func_obj, evaluated_args):
        all_args = (
            [func_obj.bound_instance] + evaluated_args
            if func_obj.bound_instance is not None
            else evaluated_args
        )

        if len(all_args) != len(func_obj.arg_names):
            expected_count = (
                len(func_obj.arg_names) - 1
                if func_obj.bound_instance is not None
                else len(func_obj.arg_names)
            )
            return None, (
                f"WASTED! ArgumentError: Mission '{func_obj.name}' expects "
                f"{expected_count} arguments, got {len(evaluated_args)}"
            )

        local_scope = dict(zip(func_obj.arg_names, all_args))
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

    def visit_FuncCallNode(self, node):
        callable_obj, error = self.visit(node.node_to_call)
        if error:
            return None, error

        evaluated_args = []
        for arg_node in node.arg_nodes:
            val, error = self.visit(arg_node)
            if error:
                return None, error
            evaluated_args.append(val)

        if isinstance(callable_obj, NativeFunction):
            try:
                return callable_obj.py_func(*evaluated_args), None
            except Exception as exc:
                return None, f"WASTED! NativeMissionError ({callable_obj.name}): {exc}"

        if isinstance(callable_obj, RockstarFunction):
            return self._invoke_function(callable_obj, evaluated_args)

        return None, f"WASTED! TypeError: '{callable_obj}' is not a callable mission"

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

def run(text, base_dir="/storage/emulated/0/Coding/rockstarlang"):
    """Executes the full Lexer -> Parser -> Interpreter pipeline on source text."""
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    parser = Parser(tokens)
    ast, error = parser.parse()
    if error:
        return None, error

    interpreter = Interpreter(base_dir=base_dir)
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
