"""
AST Node Definitions for MiniLang Phase 2 (Syntactic Analysis)
These are simple data structures to represent the syntax tree.
No execution or interpretation logic - only structural representation.
"""

from dataclasses import dataclass
from typing import Optional, List, Any


@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    pass


@dataclass
class Program(ASTNode):
    """Root node representing entire program"""
    statements: List['Statement']


@dataclass
class Statement(ASTNode):
    """Base class for statements"""
    pass


@dataclass
class Declaration(Statement):
    """Variable declaration: int x, float y, etc."""
    type_name: str  # 'int', 'float', 'string', 'bool'
    identifier: str


@dataclass
class Assignment(Statement):
    """Variable assignment: x = value, x += value, etc."""
    identifier: str
    operator: str  # '=', '+=', '-=', '*=', '/='
    value: 'Expression'


@dataclass
class FunctionDef(Statement):
    """Function definition: func name(type param1, ...): BLOQUE"""
    name: str
    parameters: List[tuple]  # [(type, name), ...]
    body: 'Block'


@dataclass
class IfStmt(Statement):
    """If/else statement with body"""
    condition: 'Expression'
    then_block: 'Block'
    else_block: Optional['Block'] = None


@dataclass
class WhileStmt(Statement):
    """While loop"""
    condition: 'Expression'
    body: 'Block'


@dataclass
class ReturnStmt(Statement):
    """Return statement"""
    value: Optional['Expression']


@dataclass
class ReadStmt(Statement):
    """Input statement: read(var)"""
    identifier: str


@dataclass
class WriteStmt(Statement):
    """Output statement: write(expr)"""
    expression: 'Expression'


@dataclass
class ExpressionStatement(Statement):
    """Expression as statement (mainly for function calls)"""
    expression: 'Expression'


@dataclass
class Block(ASTNode):
    """Block of statements (indented)"""
    statements: List[Statement]


@dataclass
class Expression(ASTNode):
    """Base class for expressions"""
    pass


@dataclass
class BinaryOp(Expression):
    """Binary operation: a + b, a * b, etc."""
    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryOp(Expression):
    """Unary operation: -x, not x"""
    operator: str
    operand: Expression


@dataclass
class FunctionCall(Expression):
    """Function call: func(arg1, arg2, ...)"""
    name: str
    arguments: List[Expression]


@dataclass
class Identifier(Expression):
    """Variable or function identifier"""
    name: str


@dataclass
class IntLiteral(Expression):
    """Integer literal"""
    value: int


@dataclass
class FloatLiteral(Expression):
    """Float literal"""
    value: float


@dataclass
class StringLiteral(Expression):
    """String literal"""
    value: str


@dataclass
class BoolLiteral(Expression):
    """Boolean literal (true/false)"""
    value: bool


@dataclass
class ParenthesizedExpr(Expression):
    """Parenthesized expression"""
    expression: Expression


# Helper function to create an empty block
def empty_block():
    """Create an empty block"""
    return Block([])
