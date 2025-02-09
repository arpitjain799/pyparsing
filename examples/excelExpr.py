# excelExpr.py
#
# Copyright 2010, Paul McGuire
#
# A partial implementation of a parser of Excel formula expressions.
#
from pyparsing import (
    CaselessKeyword,
    Suppress,
    Word,
    alphas,
    alphanums,
    nums,
    Opt,
    Group,
    one_of,
    Forward,
    infix_notation,
    OpAssoc,
    dblQuotedString,
    DelimitedList,
    Combine,
    Literal,
    QuotedString,
    ParserElement,
    pyparsing_common as ppc,
)

ParserElement.enablePackrat()

EQ, LPAR, RPAR, COLON, COMMA = Suppress.using_each("=():,")
EXCL, DOLLAR = Literal.using_each("!$")
sheetRef = Word(alphas, alphanums) | QuotedString("'", escQuote="''")
colRef = Opt(DOLLAR) + Word(alphas, max=2)
rowRef = Opt(DOLLAR) + Word(nums)
cellRef = Combine(
    Group(Opt(sheetRef + EXCL)("sheet") + colRef("col") + rowRef("row"))
)

cellRange = (
    Group(cellRef("start") + COLON + cellRef("end"))("range")
    | cellRef
    | Word(alphas, alphanums)
)

expr = Forward()

COMPARISON_OP = one_of("< = > >= <= != <>")
condExpr = expr + COMPARISON_OP + expr

ifFunc = (
    CaselessKeyword("if")
    - LPAR
    + Group(condExpr)("condition")
    + COMMA
    + Group(expr)("if_true")
    + COMMA
    + Group(expr)("if_false")
    + RPAR
)


def stat_function(name):
    return Group(CaselessKeyword(name) + Group(LPAR + DelimitedList(expr) + RPAR))


sumFunc = stat_function("sum")
minFunc = stat_function("min")
maxFunc = stat_function("max")
aveFunc = stat_function("ave")
funcCall = ifFunc | sumFunc | minFunc | maxFunc | aveFunc

multOp = one_of("* /")
addOp = one_of("+ -")
numericLiteral = ppc.number
operand = numericLiteral | funcCall | cellRange | cellRef
arithExpr = infix_notation(
    operand,
    [
        (multOp, 2, OpAssoc.LEFT),
        (addOp, 2, OpAssoc.LEFT),
    ],
)

textOperand = dblQuotedString | cellRef
textExpr = infix_notation(
    textOperand,
    [
        ("&", 2, OpAssoc.LEFT),
    ],
)

expr <<= arithExpr | textExpr


def main():
    success, report = (EQ + expr).run_tests(
        """\
        =3*A7+5
        =3*Sheet1!$A$7+5
        =3*'Sheet 1'!$A$7+5
        =3*'O''Reilly''s sheet'!$A$7+5
        =if(Sum(A1:A25)>42,Min(B1:B25),if(Sum(C1:C25)>3.14, (Min(C1:C25)+3)*18,Max(B1:B25)))
        =sum(a1:a25,10,min(b1,c2,d3))
        =if("T"&a2="TTime", "Ready", "Not ready")
    """
    )
    assert success


if __name__ == '__main__':
    main()