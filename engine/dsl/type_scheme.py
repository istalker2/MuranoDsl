import types
import helpers
from murano_object import MuranoObject
from yaql_expression import YaqlExpression
from yaql.context import Context, EvalArg


class TypeScheme(object):
    def __init__(self, spec):
        self._spec = spec

    def prepare_context(self, root_context, this, object_store,
                        namespace_resolver):
        def _int(value):
            value = value()
            if value is None:
                return None
            try:
                return int(value)
            except Exception:
                raise TypeError('test')

        def _string(value):
            value = value()
            if value is None:
                return None
            try:
                return unicode(value)
            except Exception:
                raise TypeError()

        def _bool(value):
            value = value()
            if value is None:
                return None
            return True if value else False


        def _not_null(value):
            value = value()
            if value is None:
                raise TypeError()
            return value

        def _error():
            raise TypeError()

        def _check(value, predicate):
            value = value()
            if predicate(value):
                return value
            else:
                raise TypeError(value)

        @EvalArg('obj', arg_type=(MuranoObject, types.NoneType))
        def _owned(obj):
            if obj is None:
                return None
            elif obj.parent is this:
                return obj
            else:
                raise TypeError()

        @EvalArg('obj', arg_type=MuranoObject)
        def _not_owned(obj):
            if obj is None:
                return None
            elif obj.parent is this:
                raise TypeError()
            else:
                return obj

        @EvalArg('name', arg_type=str)
        def _class(value, name):
            value = value()
            name = namespace_resolver.resolve_name(name)
            class_loader = helpers.get_class_loader(root_context)
            murano_class = class_loader.get_class(name)
            if not murano_class:
                raise TypeError()
            if value is None:
                return None
            if isinstance(value, types.DictionaryType):
                obj = object_store.load(value, this, root_context)
            elif isinstance(value, types.StringType):
                obj = object_store.get(value)
                if obj is None:
                    raise TypeError('Object %s not found' % value)
            else:
                raise TypeError()
            if not murano_class.is_compatible(obj):
                raise TypeError()
            return obj


        context = Context(parent_context=root_context)
        context.register_function(_int, 'int')
        context.register_function(_string, 'string')
        context.register_function(_bool, 'bool')
        context.register_function(_check, 'check')
        context.register_function(_not_null, 'notNull')
        context.register_function(_error, 'error')
        context.register_function(_class, 'class')
        context.register_function(_owned, 'owned')
        context.register_function(_not_owned, 'notOwned')
        return context


    def _map_dict(self, data, spec, context):
        if not isinstance(data, types.DictionaryType):
            raise TypeError()
        result = {}
        yaql_key = None
        for key, value in spec.iteritems():
            if isinstance(key, YaqlExpression):
                if yaql_key is not None:
                    raise SyntaxError()
                else:
                    yaql_key = key
            else:
                result[key] = self._map(data.get(key), value, context)

        if yaql_key is not None:
            yaql_value = spec[yaql_key]
            for key, value in data.iteritems():
                if key in result:
                    continue
                result[self._map(key, yaql_key, context)] = \
                    self._map(value, yaql_value, context)

        return result

    def _map_list(self, data, spec, context):
        if len(spec) < 1:
            raise TypeError()
        if not isinstance(data, types.ListType):
            data = [data]
        result = []
        for index, item in enumerate(data):
            spec_item = spec[-1] if index >= len(spec) else spec[index]
            result.append(self._map(item, spec_item, context))
        return result

    def _map_scalar(self, data, spec, context):
        if data != spec:
            raise TypeError()
        else:
            return data

    def _map(self, data, spec, context):
        child_context = Context(parent_context=context)
        if isinstance(spec, YaqlExpression):
            child_context.set_data(data)
            return spec.evaluate(context=child_context)
        elif isinstance(spec, types.DictionaryType):
            return self._map_dict(data, spec, child_context)
        elif isinstance(spec, types.ListType):
            return self._map_list(data, spec, child_context)
        elif isinstance(spec, (types.IntType,
                               types.StringTypes,
                               types.NoneType)):
            return self._map_scalar(data, spec, child_context)

    def __call__(self, data, context, this, object_store, namespace_resolver):
        context = self.prepare_context(
            context, this, object_store, namespace_resolver)
        return self._map(data, self._spec, context)
