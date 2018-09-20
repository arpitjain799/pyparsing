#
# simple_unit_tests.py
#
# While these unit tests *do* perform low-level unit testing of the classes in pyparsing,
# this testing module should also serve an instructional purpose, to clearly show simple passing
# and failing parse cases of some basic pyparsing expressions.
#
# Copyright (c) 2018  Paul T. McGuire
#

import unittest
import pyparsing as pp
from collections import namedtuple
from datetime import datetime

# Test spec data class for specifying simple pyparsing test cases
PpTestSpec = namedtuple("PpTestSpec", "desc expr text expected_list expected_dict expected_fail_locn")
PpTestSpec.__new__.__defaults__ = ('', pp.Empty(), '', None, None, None)


class PyparsingExpressionTestCase(unittest.TestCase):
    """
    Base pyparsing testing class to parse various pyparsing expressions against
    given text strings. Subclasses must define a class attribute 'tests' which
    is a list of PpTestSpec instances.
    """
    def test_match(self):
        if self.__class__ is PyparsingExpressionTestCase:
            return

        for test_spec in self.tests:
            # for each spec in the class's tests list, create a subtest
            # that will either:
            #  - parse the string with expected success, display the 
            #    results, and validate the returned ParseResults
            #  - or parse the string with expected failure, display the 
            #    error message and mark the error location, and validate
            #    the location against an expected value
            with self.subTest(test_spec=test_spec):
                test_spec.expr.streamline()
                print("\n{} - {}({})".format(test_spec.desc, 
                                             type(test_spec.expr).__name__, 
                                             test_spec.expr))

                if test_spec.expected_fail_locn is None:
                    # expect success
                    result = test_spec.expr.parseString(test_spec.text)
                    print(result.dump())
                    # compare results against given list and/or dict
                    if test_spec.expected_list is not None:
                        self.assertEqual(result.asList(), test_spec.expected_list)
                    if test_spec.expected_dict is not None:
                        self.assertEqual(result.asDict(), test_spec.expected_dict)

                else:
                    # expect fail
                    with self.assertRaises(pp.ParseException) as ar:
                        test_spec.expr.parseString(test_spec.text)
                    print(' ', test_spec.text or "''")
                    print(' ', ' '*ar.exception.loc+'^')
                    print(' ', ar.exception.msg)
                    self.assertEqual(ar.exception.loc, test_spec.expected_fail_locn)



class TestLiteral(PyparsingExpressionTestCase):
    tests = [
        PpTestSpec(
            desc = "Simple match",
            expr = pp.Literal("xyz"),
            text = "xyz",
            expected_list = ["xyz"],
        ),
        PpTestSpec(
            desc = "Simple match after skipping whitespace",
            expr = pp.Literal("xyz"),
            text = "  xyz",
            expected_list = ["xyz"],
        ),
        PpTestSpec(
            desc = "Simple fail - parse an empty string",
            expr = pp.Literal("xyz"),
            text = "",
            expected_fail_locn = 0,
        ),
        PpTestSpec(
            desc = "Simple fail - parse a mismatching string",
            expr = pp.Literal("xyz"),
            text = "xyu",
            expected_fail_locn = 0,
        ),
        PpTestSpec(
            desc = "Simple fail - parse a partially matching string",
            expr = pp.Literal("xyz"),
            text = "xy",
            expected_fail_locn = 0,
        ),
        PpTestSpec(
            desc = "Fail - parse a partially matching string by matching individual letters",
            expr =  pp.Literal("x") + pp.Literal("y") + pp.Literal("z"),
            text = "xy",
            expected_fail_locn = 2,
        ),
    ]


class TestWord(PyparsingExpressionTestCase):
    tests = [
        PpTestSpec(
            desc = "Simple Word match",
            expr = pp.Word("xy"),
            text = "xxyxxyy",
            expected_list = ["xxyxxyy"],
        ),
        PpTestSpec(
            desc = "Simple Word match of two separate Words",
            expr = pp.Word("x") + pp.Word("y"),
            text = "xxxxxyy",
            expected_list = ["xxxxx", "yy"],
        ),
        PpTestSpec(
            desc = "Simple Word match of two separate Words - implicitly skips whitespace",
            expr = pp.Word("x") + pp.Word("y"),
            text = "xxxxx yy",
            expected_list = ["xxxxx", "yy"],
        ),
    ]


class TestRepetition(PyparsingExpressionTestCase):
    tests = [
        PpTestSpec(
            desc = "Match several words",
            expr = pp.OneOrMore(pp.Word("x") | pp.Word("y")),
            text = "xxyxxyyxxyxyxxxy",
            expected_list = ['xx', 'y', 'xx', 'yy', 'xx', 'y', 'x', 'y', 'xxx', 'y'],
        ),
        PpTestSpec(
            desc = "Match words and numbers - show use of results names to collect types of tokens",
            expr = pp.OneOrMore(pp.Word(pp.alphas)("alpha*") | pp.pyparsing_common.integer("int*")),
            text = "sdlfj23084ksdfs08234kjsdlfkjd0934",
            expected_list = ['sdlfj', 23084, 'ksdfs', 8234, 'kjsdlfkjd', 934],
            expected_dict = { 'alpha': ['sdlfj', 'ksdfs', 'kjsdlfkjd'], 'int': [23084, 8234, 934] }
        ),
        PpTestSpec(
            desc = "Using delimitedList (comma is the default delimiter)",
            expr = pp.delimitedList(pp.Word(pp.alphas)),
            text = "xxyx,xy,y,xxyx,yxx, xy",
            expected_list = ['xxyx', 'xy', 'y', 'xxyx', 'yxx', 'xy'],
        ),
        PpTestSpec(
            desc = "Using delimitedList, with ':' delimiter",
            expr = pp.delimitedList(pp.Word(pp.hexnums, exact=2), delim=':', combine=True),
            text = "0A:4B:73:21:FE:76",
            expected_list = ['0A:4B:73:21:FE:76'],
        ),
    ]


class TestResultsName(PyparsingExpressionTestCase):
    tests = [
        PpTestSpec(
            desc = "Match with results name",
            expr = pp.Literal("xyz").setResultsName("value"),
            text = "xyz",
            expected_dict = {'value': 'xyz'},
            expected_list = ['xyz'],
        ),
        PpTestSpec(
            desc = "Match with results name - using naming short-cut",
            expr = pp.Literal("xyz")("value"),
            text = "xyz",
            expected_dict = {'value': 'xyz'},
            expected_list = ['xyz'],
        ),
        PpTestSpec(
            desc = "Define multiple results names",
            expr = pp.Word(pp.alphas, pp.alphanums)("key") + '=' + pp.pyparsing_common.integer("value"),
            text = "range=5280",
            expected_dict = {'key': 'range', 'value': 5280},
            expected_list = ['range', '=', 5280],
        ),
    ]

class TestGroups(PyparsingExpressionTestCase):
    tests = [
        PpTestSpec(
            desc = "Define multiple results names in groups",
            expr = pp.OneOrMore(pp.Group(pp.Word(pp.alphas, pp.alphanums)("key") 
                                          + pp.Suppress('=') 
                                          + pp.pyparsing_common.number("value"))),
            text = "range=5280 long=-138.52 lat=46.91",
            expected_list = [['range', 5280], ['long', -138.52], ['lat', 46.91]],
        ),
    ]

class TestParseAction(PyparsingExpressionTestCase):
    tests = [
        PpTestSpec(
            desc = "Match with numeric string converted to int",
            expr = pp.Word("0123456789").addParseAction(lambda t: int(t[0])),
            text = "12345",
            expected_list = [12345],  # note - result is type int, not str 
        ),
        PpTestSpec(
            desc = "Use two parse actions to convert numeric string, then convert to datetime",
            expr = pp.Word(pp.nums).addParseAction(lambda t: int(t[0]), 
                                                    lambda t: datetime.fromtimestamp(t[0])),
            text = "1537415628",
            expected_list = [datetime(2018, 9, 19, 22, 53, 48)],
        ),
        PpTestSpec(
            desc = "Use tokenMap for parse actions that operate on a single-length token",
            expr = pp.Word(pp.nums).addParseAction(pp.tokenMap(int), pp.tokenMap(datetime.fromtimestamp)),
            text = "1537415628",
            expected_list = [datetime(2018, 9, 19, 22, 53, 48)],
        ),
    ]

class TestParseCondition(PyparsingExpressionTestCase):
    tests = [
        PpTestSpec(
            desc = "Define a condition to only match numeric values that are multiples of 7",
            expr = pp.OneOrMore(pp.Word(pp.nums).addCondition(lambda t: int(t[0]) % 7 == 0)),
            text = "14 35 77 12 28",
            expected_list = ['14', '35', '77'],
        ),
    ]


if __name__ == '__main__':
    # we use unittest features that are in Py3 only, bail out if run on Py2
    import sys
    if sys.version_info[0] < 3:
        print("simple_unit_tests.py runs on Python 3 only")
        sys.exit(0)
        
    unittest.main()