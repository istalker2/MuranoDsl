import inspect
import types
from lhs_expression import LhsExpression
import helpers
from yaql_expression import YaqlExpression

_macros = []


def register_macro(cls):
    _macros.append(cls)


class DslExpression(object):
    def execute(self, context, murano_class):
        pass


class Statement(DslExpression):
    def __init__(self, statement):
        if isinstance(statement, YaqlExpression):
            key = None
            value = statement
        elif isinstance(statement, types.DictionaryType):
            if len(statement) != 1:
                raise SyntaxError()
            key = statement.keys()[0]
            value = statement[key]
        else:
            raise SyntaxError()

        self._destination = None if not key else LhsExpression(key)
        self._expression = value

    @property
    def destination(self):
        return self._destination

    @property
    def expression(self):
        return self._expression

    def execute(self, context, murano_class):
        result = helpers.evaluate(self.expression, context)
        if self.destination:
            self.destination(result, context, murano_class)

        return result


def parse_expression(expr):
    result = None
    if isinstance(expr, YaqlExpression):
        result = Statement(expr)
    elif isinstance(expr, types.DictionaryType):
        kwds = {}
        for key, value in expr.iteritems():
            if isinstance(key, YaqlExpression):
                if result is not None:
                    raise ValueError()
                result = Statement(expr)
            else:
                kwds[key] = value

        if result is None:
            for cls in _macros:
                try:
                    return cls(**kwds)
                except TypeError:
                    continue

    if result is None:
        raise SyntaxError()
    return result






