#Hyuntae Kim A01227317
#Copmiler PLY
#Este codigo esta basado en el tutorial de CodePulse
#https://github.com/davidcallanan/py-myopl-code/tree/master/ep9

import string

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

class Error:
	def __init__(self, pos_start, pos_end, error_name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.error_name = error_name
		self.details = details
	
	def as_string(self):
		result  = f'{self.error_name}: {self.details}\n'
		result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
		return result

class IllegalCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Expected Character', details)

class InvalidSyntaxError(Error):
	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
	def __init__(self, pos_start, pos_end, details, context):
		super().__init__(pos_start, pos_end, 'Runtime Error', details)
		self.context = context

	def as_string(self):
		result  = self.generate_traceback()
		result += f'{self.error_name}: {self.details}'
		return result

	def generate_traceback(self):
		result = ''
		pos = self.pos_start
		ctx = self.context

		while ctx:
			result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
			pos = ctx.parent_entry_pos
			ctx = ctx.parent

		return 'Traceback (most recent call last):\n' + result

class Position:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.fn = fn
		self.ftxt = ftxt

	def advance(self, current_pos=None):
		self.idx += 1
		self.col += 1

		if current_pos == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

t_INT				= 'INT'
t_FLOAT    			= 'FLOAT'
t_STRING			= 'STRING'
t_IDENTIFIER		= 'IDENTIFIER'
t_KEYWORD			= 'KEYWORD'
t_PLUS    		 	= 'PLUS'
t_MINUS    			= 'MINUS'
t_MUL      			= 'MUL'
t_DIV      			= 'DIV'
t_POW				= 'POW'
t_EQ				= 'EQ'
t_LPAREN   			= 'LPAREN'
t_RPAREN   			= 'RPAREN'
t_EE				= 'EE'
t_NE				= 'NE'
t_LT				= 'LT'
t_GT				= 'GT'
t_LTE				= 'LTE'
t_GTE				= 'GTE'
t_EOF				= 'EOF'

KEYWORDS = [
	'VAR',
	'AND',
	'OR',
	'IF',
	'ELIF',
	'ELSE',
	'FOR',
	'TO',
	'STEP',
	'WHILE',
	'THEN'
]

class Token:
	def __init__(self, type_, value=None, pos_start=None, pos_end=None):
		self.type = type_
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.advance()

		if pos_end:
			self.pos_end = pos_end.copy()

	def matches(self, type_, value):
		return self.type == type_ and self.value == value
	
	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'

class Lexer:
	def __init__(self, fn, text):
		self.fn = fn
		self.text = text
		self.pos = Position(-1, 0, -1, fn, text)
		self.current_pos = None
		self.advance()
	
	def advance(self):
		self.pos.advance(self.current_pos)
		self.current_pos = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def make_tokens(self):
		tokens = []

		while self.current_pos != None:
			if self.current_pos in ' \t':
				self.advance()
			elif self.current_pos in DIGITS:
				tokens.append(self.is_number())
			elif self.current_pos in LETTERS:
				tokens.append(self.is_identifier())
			elif self.current_pos == '"':
				tokens.append(self.is_string())
			elif self.current_pos == '+':
				tokens.append(Token(t_PLUS, pos_start=self.pos))
				self.advance()
			elif self.current_pos == '-':
				tokens.append(Token(t_MINUS, pos_start=self.pos))
				self.advance()
			elif self.current_pos == '*':
				tokens.append(Token(t_MUL, pos_start=self.pos))
				self.advance()
			elif self.current_pos == '/':
				tokens.append(Token(t_DIV, pos_start=self.pos))
				self.advance()
			elif self.current_pos == '^':
				tokens.append(Token(t_POW, pos_start=self.pos))
				self.advance()
			elif self.current_pos == '(':
				tokens.append(Token(t_LPAREN, pos_start=self.pos))
				self.advance()
			elif self.current_pos == ')':
				tokens.append(Token(t_RPAREN, pos_start=self.pos))
				self.advance()
			elif self.current_pos == '!':
				token, error = self.is_not_equal()
				if error: return [], error
				tokens.append(token)
			elif self.current_pos == '=':
				tokens.append(self.is_equal())
			elif self.current_pos == '<':
				tokens.append(self.is_less_than())
			elif self.current_pos == '>':
				tokens.append(self.is_greater_than())
			else:
				pos_start = self.pos.copy()
				char = self.current_pos
				self.advance()
				return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

		tokens.append(Token(t_EOF, pos_start=self.pos))
		return tokens, None

	def is_number(self):
		num_str = ''
		dot_count = 0
		pos_start = self.pos.copy()

		while self.current_pos != None and self.current_pos in DIGITS + '.':
			if self.current_pos == '.':
				if dot_count == 1: break
				dot_count += 1
			num_str += self.current_pos
			self.advance()

		if dot_count == 0:
			return Token(t_INT, int(num_str), pos_start, self.pos)
		else:
			return Token(t_FLOAT, float(num_str), pos_start, self.pos)

	def is_string(self):
		string = ''
		pos_start = self.pos.copy()
		escape_char = False
		self.advance()

		escape_chars = {
			'n': '\n',
			't': '\t'
		}

		while self.current_pos != None and (self.current_pos != '"' or escape_char):
			if escape_char:
				string += escape_chars.get(self.current_pos, self.current_pos)
			else:
				if self.current_pos == '\\':
					escape_char = True
				else:
					string += self.current_pos
			self.advance()
			escape_char = False
		
		self.advance()
		return Token(t_STRING, string, pos_start, self.pos)

	def is_identifier(self):
		id_str = ''
		pos_start = self.pos.copy()

		while self.current_pos != None and self.current_pos in LETTERS_DIGITS + '_':
			id_str += self.current_pos
			self.advance()

		tok_type = t_KEYWORD if id_str in KEYWORDS else t_IDENTIFIER
		return Token(tok_type, id_str, pos_start, self.pos)

	def is_not_equal(self):
		pos_start = self.pos.copy()
		self.advance()

		if self.current_pos == '=':
			self.advance()
			return Token(t_NE, pos_start=pos_start, pos_end=self.pos), None

		self.advance()
		return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")
	
	def is_equal(self):
		tok_type = t_EQ
		pos_start = self.pos.copy()
		self.advance()

		if self.current_pos == '=':
			self.advance()
			tok_type = t_EE

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

	def is_less_than(self):
		tok_type = t_LT
		pos_start = self.pos.copy()
		self.advance()

		if self.current_pos == '=':
			self.advance()
			tok_type = t_LTE

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

	def is_greater_than(self):
		tok_type = t_GT
		pos_start = self.pos.copy()
		self.advance()

		if self.current_pos == '=':
			self.advance()
			tok_type = t_GTE

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

class NumberNode:
	def __init__(self, tok):
		self.tok = tok

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class StringNode:
	def __init__(self, tok):
		self.tok = tok

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class VarAccessNode:
	def __init__(self, var_name_tok):
		self.var_name_tok = var_name_tok

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
	def __init__(self, var_name_tok, value_node):
		self.var_name_tok = var_name_tok
		self.value_node = value_node

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.value_node.pos_end

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

class IfNode:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.pos_start = self.cases[0][0].pos_start
		self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end

class ForNode:
	def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
		self.var_name_tok = var_name_tok
		self.start_value_node = start_value_node
		self.end_value_node = end_value_node
		self.step_value_node = step_value_node
		self.body_node = body_node

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.body_node.pos_end

class WhileNode:
	def __init__(self, condition_node, body_node):
		self.condition_node = condition_node
		self.body_node = body_node

		self.pos_start = self.condition_node.pos_start
		self.pos_end = self.body_node.pos_end

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.last_registered_advance_count = 0
		self.advance_count = 0

	def register_advancement(self):
		self.last_registered_advance_count = 1
		self.advance_count += 1

	def register(self, res):
		self.last_registered_advance_count = res.advance_count
		self.advance_count += res.advance_count
		if res.error: self.error = res.error
		return res.node

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		if not self.error or self.last_registered_advance_count == 0:
			self.error = error
		return self

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self, ):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.expr()
		if not res.error and self.current_tok.type != t_EOF:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'AND' or 'OR'"
			))
		return res

	def expr(self):
		res = ParseResult()

		if self.current_tok.matches(t_KEYWORD, 'VAR'):
			res.register_advancement()
			self.advance()

			if self.current_tok.type != t_IDENTIFIER:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected identifier"
				))

			var_name = self.current_tok
			res.register_advancement()
			self.advance()

			if self.current_tok.type != t_EQ:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '='"
				))

			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			return res.success(VarAssignNode(var_name, expr))

		node = res.register(self.bin_op(self.comp_expr, ((t_KEYWORD, 'AND'), (t_KEYWORD, 'OR'))))

		if res.error:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'VAR', 'IF', 'FOR', 'WHILE', int, float, identifier, '+', '-', '('"
			))

		return res.success(node)

	def comp_expr(self):
		res = ParseResult()
		node = res.register(self.bin_op(self.arith_expr, (t_EE, t_NE, t_LT, t_GT, t_LTE, t_GTE)))
		
		if res.error:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected int, float, identifier, '+', '-', '(''"
			))

		return res.success(node)

	def arith_expr(self):
		return self.bin_op(self.term, (t_PLUS, t_MINUS))

	def term(self):
		return self.bin_op(self.factor, (t_MUL, t_DIV))

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (t_PLUS, t_MINUS):
			res.register_advancement()
			self.advance()
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))

		return self.power()

	def power(self):
		return self.bin_op(self.call, (t_POW, ), self.factor)

	def call(self):
		res = ParseResult()
		atom = res.register(self.atom())
		if res.error: return res

		if self.current_tok.type == t_LPAREN:
			res.register_advancement()
			self.advance()
			arg_nodes = []

			if self.current_tok.type == t_RPAREN:
				res.register_advancement()
				self.advance()
			else:
				arg_nodes.append(res.register(self.expr()))
				if res.error:
					return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', int, float, identifier, '+', '-', '('"
					))

				if self.current_tok.type != t_RPAREN:
					return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						f"Expected ',' or ')'"
					))

				res.register_advancement()
				self.advance()

		return res.success(atom)

	def atom(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (t_INT, t_FLOAT):
			res.register_advancement()
			self.advance()
			return res.success(NumberNode(tok))

		elif tok.type == t_STRING:
			res.register_advancement()
			self.advance()
			return res.success(StringNode(tok))

		elif tok.type == t_IDENTIFIER:
			res.register_advancement()
			self.advance()
			return res.success(VarAccessNode(tok))

		elif tok.type == t_LPAREN:
			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == t_RPAREN:
				res.register_advancement()
				self.advance()
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))
		
		elif tok.matches(t_KEYWORD, 'IF'):
			if_expr = res.register(self.if_expr())
			if res.error: return res
			return res.success(if_expr)

		elif tok.matches(t_KEYWORD, 'FOR'):
			for_expr = res.register(self.for_expr())
			if res.error: return res
			return res.success(for_expr)

		elif tok.matches(t_KEYWORD, 'WHILE'):
			while_expr = res.register(self.while_expr())
			if res.error: return res
			return res.success(while_expr)

		elif tok.matches(t_KEYWORD, 'FUN'):
			func_def = res.register(self.func_def())
			if res.error: return res
			return res.success(func_def)

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int, float, identifier, '+', '-', '(', 'IF', 'FOR', 'WHILE'"
		))

	def if_expr(self):
		res = ParseResult()
		cases = []
		else_case = None

		if not self.current_tok.matches(t_KEYWORD, 'IF'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'IF'"
			))

		res.register_advancement()
		self.advance()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.matches(t_KEYWORD, 'THEN'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'THEN'"
			))

		res.register_advancement()
		self.advance()

		expr = res.register(self.expr())
		if res.error: return res
		cases.append((condition, expr))

		while self.current_tok.matches(t_KEYWORD, 'ELIF'):
			res.register_advancement()
			self.advance()

			condition = res.register(self.expr())
			if res.error: return res

			if not self.current_tok.matches(t_KEYWORD, 'THEN'):
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					f"Expected 'THEN'"
				))

			res.register_advancement()
			self.advance()

			expr = res.register(self.expr())
			if res.error: return res
			cases.append((condition, expr))

		if self.current_tok.matches(t_KEYWORD, 'ELSE'):
			res.register_advancement()
			self.advance()

			else_case = res.register(self.expr())
			if res.error: return res

		return res.success(IfNode(cases, else_case))

	def for_expr(self):
		res = ParseResult()

		if not self.current_tok.matches(t_KEYWORD, 'FOR'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'FOR'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type != t_IDENTIFIER:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected identifier"
			))

		var_name = self.current_tok
		res.register_advancement()
		self.advance()

		if self.current_tok.type != t_EQ:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected '='"
			))
		
		res.register_advancement()
		self.advance()

		start_value = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.matches(t_KEYWORD, 'TO'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'TO'"
			))
		
		res.register_advancement()
		self.advance()

		end_value = res.register(self.expr())
		if res.error: return res

		if self.current_tok.matches(t_KEYWORD, 'STEP'):
			res.register_advancement()
			self.advance()

			step_value = res.register(self.expr())
			if res.error: return res
		else:
			step_value = None

		if not self.current_tok.matches(t_KEYWORD, 'THEN'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'THEN'"
			))

		res.register_advancement()
		self.advance()

		body = res.register(self.expr())
		if res.error: return res

		return res.success(ForNode(var_name, start_value, end_value, step_value, body))

	def while_expr(self):
		res = ParseResult()

		if not self.current_tok.matches(t_KEYWORD, 'WHILE'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'WHILE'"
			))

		res.register_advancement()
		self.advance()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.matches(t_KEYWORD, 'THEN'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'THEN'"
			))

		res.register_advancement()
		self.advance()

		body = res.register(self.expr())
		if res.error: return res

		return res.success(WhileNode(condition, body))

	def bin_op(self, func_a, ops, func_b=None):
		if func_b == None:
			func_b = func_a
		
		res = ParseResult()
		left = res.register(func_a())
		if res.error: return res

		while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
			op_tok = self.current_tok
			res.register_advancement()
			self.advance()
			right = res.register(func_b())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self

class Value:
	def __init__(self):
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
		return None, self.illegal_operation(other)

	def subbed_by(self, other):
		return None, self.illegal_operation(other)

	def multed_by(self, other):
		return None, self.illegal_operation(other)

	def dived_by(self, other):
		return None, self.illegal_operation(other)

	def powed_by(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_eq(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_ne(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lte(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gte(self, other):
		return None, self.illegal_operation(other)

	def anded_by(self, other):
		return None, self.illegal_operation(other)

	def ored_by(self, other):
		return None, self.illegal_operation(other)

	def copy(self):
		raise Exception('No copy method defined')

	def is_true(self):
		return False

	def illegal_operation(self, other=None):
		if not other: other = self
		return RTError(
			self.pos_start, other.pos_end,
			'Illegal operation',
			self.context
		)

class Number(Value):
	def __init__(self, value):
		super().__init__()
		self.value = value

	def added_to(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def subbed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def multed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def dived_by(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RTError(
					other.pos_start, other.pos_end,
					'Can not divide anything by 0',
					self.context
				)

			return Number(self.value / other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def powed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value ** other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_eq(self, other):
		if isinstance(other, Number):
			return Number(int(self.value == other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_ne(self, other):
		if isinstance(other, Number):
			return Number(int(self.value != other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_lt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value < other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_gt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value > other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_lte(self, other):
		if isinstance(other, Number):
			return Number(int(self.value <= other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_gte(self, other):
		if isinstance(other, Number):
			return Number(int(self.value >= other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def anded_by(self, other):
		if isinstance(other, Number):
			return Number(int(self.value and other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def ored_by(self, other):
		if isinstance(other, Number):
			return Number(int(self.value or other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def notted(self):
		return Number(1 if self.value == 0 else 0).set_context(self.context), None

	def copy(self):
		copy = Number(self.value)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy

	def is_true(self):
		return self.value != 0
	
	def __repr__(self):
		return str(self.value)

class String(Value):
	def __init__(self, value):
		super().__init__()
		self.value = value

	def added_to(self, other):
		if isinstance(other, String):
			return String(self.value + other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def multed_by(self, other):
		if isinstance(other, Number):
			return String(self.value * other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def is_true(self):
		return len(self.value) > 0

	def copy(self):
		copy = String(self.value)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy

	def __repr__(self):
		return f'"{self.value}"'

class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
		self.symbol_table = None

class SymbolTable:
	def __init__(self, parent=None):
		self.symbols = {}
		self.parent = parent

	def get(self, name):
		value = self.symbols.get(name, None)
		if value == None and self.parent:
			return self.parent.get(name)
		return value

	def set(self, name, value):
		self.symbols[name] = value

	def remove(self, name):
		del self.symbols[name]

class Interpreter:
	def visit(self, node, context):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node, context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	def visit_NumberNode(self, node, context):
		return RTResult().success(
			Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_StringNode(self, node, context):
		return RTResult().success(
			String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_VarAccessNode(self, node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = context.symbol_table.get(var_name)

		if not value:
			return res.failure(RTError(
				node.pos_start, node.pos_end,
				f"'{var_name}' is not defined",
				context
			))

		value = value.copy().set_pos(node.pos_start, node.pos_end)
		return res.success(value)

	def visit_VarAssignNode(self, node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = res.register(self.visit(node.value_node, context))
		if res.error: return res

		context.symbol_table.set(var_name, value)
		return res.success(value)

	def visit_BinOpNode(self, node, context):
		res = RTResult()
		left = res.register(self.visit(node.left_node, context))
		if res.error: return res
		right = res.register(self.visit(node.right_node, context))
		if res.error: return res

		if node.op_tok.type == t_PLUS:
			result, error = left.added_to(right)
		elif node.op_tok.type == t_MINUS:
			result, error = left.subbed_by(right)
		elif node.op_tok.type == t_MUL:
			result, error = left.multed_by(right)
		elif node.op_tok.type == t_DIV:
			result, error = left.dived_by(right)
		elif node.op_tok.type == t_POW:
			result, error = left.powed_by(right)
		elif node.op_tok.type == t_EE:
			result, error = left.get_comparison_eq(right)
		elif node.op_tok.type == t_NE:
			result, error = left.get_comparison_ne(right)
		elif node.op_tok.type == t_LT:
			result, error = left.get_comparison_lt(right)
		elif node.op_tok.type == t_GT:
			result, error = left.get_comparison_gt(right)
		elif node.op_tok.type == t_LTE:
			result, error = left.get_comparison_lte(right)
		elif node.op_tok.type == t_GTE:
			result, error = left.get_comparison_gte(right)
		elif node.op_tok.matches(t_KEYWORD, 'AND'):
			result, error = left.anded_by(right)
		elif node.op_tok.matches(t_KEYWORD, 'OR'):
			result, error = left.ored_by(right)

		if error:
			return res.failure(error)
		else:
			return res.success(result.set_pos(node.pos_start, node.pos_end))

	def visit_UnaryOpNode(self, node, context):
		res = RTResult()
		number = res.register(self.visit(node.node, context))
		if res.error: return res

		error = None

		if node.op_tok.type == t_MINUS:
			number, error = number.multed_by(Number(-1))
		elif node.op_tok.matches(t_KEYWORD, 'NOT'):
			number, error = number.notted()

		if error:
			return res.failure(error)
		else:
			return res.success(number.set_pos(node.pos_start, node.pos_end))

	def visit_IfNode(self, node, context):
		res = RTResult()

		for condition, expr in node.cases:
			condition_value = res.register(self.visit(condition, context))
			if res.error: return res

			if condition_value.is_true():
				expr_value = res.register(self.visit(expr, context))
				if res.error: return res
				return res.success(expr_value)

		if node.else_case:
			else_value = res.register(self.visit(node.else_case, context))
			if res.error: return res
			return res.success(else_value)

		return res.success(None)

	def visit_ForNode(self, node, context):
		res = RTResult()

		start_value = res.register(self.visit(node.start_value_node, context))
		if res.error: return res

		end_value = res.register(self.visit(node.end_value_node, context))
		if res.error: return res

		if node.step_value_node:
			step_value = res.register(self.visit(node.step_value_node, context))
			if res.error: return res
		else:
			step_value = Number(1)

		i = start_value.value

		if step_value.value >= 0:
			condition = lambda: i < end_value.value
		else:
			condition = lambda: i > end_value.value
		
		while condition():
			context.symbol_table.set(node.var_name_tok.value, Number(i))
			i += step_value.value

			res.register(self.visit(node.body_node, context))
			if res.error: return res

		return res.success(None)

	def visit_WhileNode(self, node, context):
		res = RTResult()

		while True:
			condition = res.register(self.visit(node.condition_node, context))
			if res.error: return res

			if not condition.is_true(): break

			res.register(self.visit(node.body_node, context))
			if res.error: return res

		return res.success(None)

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number(0))
global_symbol_table.set("FALSE", Number(0))
global_symbol_table.set("TRUE", Number(1))

def run(fn, text):
	# Generate tokens
	lexer = Lexer(fn, text)
	tokens, error = lexer.make_tokens()
	if error: return None, error
	
	# Generate AST
	parser = Parser(tokens)
	ast = parser.parse()
	if ast.error: return None, ast.error

	# Run program
	interpreter = Interpreter()
	context = Context('<program>')
	context.symbol_table = global_symbol_table
	result = interpreter.visit(ast.node, context)

	return result.value, result.error