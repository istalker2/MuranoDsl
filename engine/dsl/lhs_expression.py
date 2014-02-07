import types

import yaql
from yaql.context import EvalArg, Context
import yaql.expressions

import type_scheme
from yaql_expression import YaqlExpression
from murano_object import MuranoObject


class LhsExpression(object):
    class Property(object):
        def __init__(self, getter, setter):
            self._getter = getter
            self._setter = setter

        def get(self):
            return self._getter()

        def set(self, value):
            self._setter(value)

    def __init__(self, expression):
        if isinstance(expression, (YaqlExpression,
                                   yaql.expressions.Expression)):
            self._expression = expression
        else:
            self._expression = yaql.parse(str(expression))
        self._current_obj = None
        self._current_obj_name = None

    def _create_context(self, root_context, murano_class):
        def _get_value(src, key):
            if isinstance(src, types.DictionaryType):
                return src.get(key)
            elif isinstance(src, types.ListType) and isinstance(
                    key, types.IntType):
                return src[key]
            elif isinstance(src, MuranoObject) and isinstance(
                    key, types.StringTypes):
                self._current_obj = src
                self._current_obj_name = key
                return src.get_property(key, murano_class)
            else:
                raise TypeError()

        def _set_value(src, key, value):
            if isinstance(src, types.DictionaryType):
                old_value = src.get(key, type_scheme.NoValue)
                src[key] = value
                if self._current_obj is not None:
                    try:
                        p_value = self._current_obj.get_property(
                            self._current_obj_name, murano_class)
                        self._current_obj.set_property(
                            self._current_obj_name, p_value, murano_class)
                    except Exception as e:
                        if not old_value is type_scheme.NoValue:
                            src[key] = old_value
                        else:
                            src.pop(key, None)
                        raise e
            elif isinstance(src, types.ListType) and isinstance(
                    key, types.IntType):
                old_value = src[key]
                src[key] = value
                if self._current_obj is not None:
                    try:
                        p_value = self._current_obj.get_property(
                            self._current_obj_name, murano_class)
                        self._current_obj.set_property(
                            self._current_obj_name, p_value, murano_class)
                    except Exception as e:
                        src[key] = old_value
                        raise e

            elif isinstance(src, MuranoObject) and isinstance(
                    key, types.StringTypes):
                self._current_spec = src.type.find_property(key)
                src.set_property(key, value, murano_class)
            else:
                raise TypeError()

        def get_context_data(path):
            path = path()

            def set_data(value):
                if not path or path == '$' or path == '$this':
                    raise ValueError()
                root_context.set_data(value, path)

            return LhsExpression.Property(
                lambda: root_context.get_data(path), set_data)

        @EvalArg('this', arg_type=LhsExpression.Property)
        def attribution(this, arg_name):
            arg_name = arg_name()
            return LhsExpression.Property(
                lambda: _get_value(this.get(), arg_name),
                lambda value: _set_value(this.get(), arg_name, value))


        @EvalArg("this", LhsExpression.Property)
        def indexation(this, index):
            return LhsExpression.Property(
                lambda: _get_value(this.get(), index()),
                lambda value: _set_value(this.get(), index(), value))

        context = Context()
        context.register_function(get_context_data, '#get_context_data')
        context.register_function(attribution, '#operator_.')
        context.register_function(indexation, "where")
        return context

    def __call__(self, value, context, murano_class):
        new_context = self._create_context(context, murano_class)
        new_context.set_data(context.get_data('$'))
        self._current_obj = None
        self._current_obj_name = None
        property = self._expression.evaluate(context=new_context)
        property.set(value)
