import itertools
import types
from yaql.context import ContextAware, EvalArg
from . import MuranoObject
import exceptions
import yaql.exceptions
import helpers


def _resolve(name, obj):
    @EvalArg('this', MuranoObject)
    @ContextAware()
    def invoke(context, this, *args):
        try:
            executor = helpers.get_executor(context)
            murano_class = context.get_data('$?type')
            return executor.invoke_method(name, this, context,
                                          murano_class, *args)
        except exceptions.NoMethodFound:
            raise yaql.exceptions.YaqlExecutionException()
        except exceptions.AmbiguousMethodName:
            raise yaql.exceptions.YaqlExecutionException()

    if not isinstance(obj, MuranoObject):
        return None

    return invoke


@EvalArg('value', MuranoObject)
def _id(value):
    return value.object_id


@EvalArg('value', MuranoObject)
@EvalArg('type', str)
@ContextAware()
def _cast(context, value, type):
    if not '.' in type:
        murano_class = context.get_data('$?type')
        type = murano_class.namespace_resolver.resolve_name(type)
    class_loader = helpers.get_class_loader(context)
    return value.cast(class_loader.get_class(type))


@EvalArg('name', str)
@ContextAware()
def _new(context, name, *args):
    murano_class = helpers.get_type(context)
    name = murano_class.namespace_resolver.resolve_name(name)
    parameters = {}
    arg_values = [t() for t in args]
    if len(arg_values) == 1 and isinstance(
            arg_values[0], types.DictionaryType):
        parameters = arg_values[0]
    elif len(arg_values) > 0:
        for p in arg_values:
            if not isinstance(p, types.TupleType) or \
                    not isinstance(p[0], types.StringType):
                    raise SyntaxError()
            parameters[p[0]] = p[1]

    object_store = helpers.get_object_store(context)
    class_loader = helpers.get_class_loader(context)
    return class_loader.get_class(name).new(
        None, object_store, context, parameters=parameters)


@EvalArg('value', MuranoObject)
def _super(value):
    return [value.cast(type) for type in value.type.parents]


@EvalArg('value', MuranoObject)
def _super2(value, func):
    return itertools.imap(func, _super(value))


@EvalArg('value', MuranoObject)
def _psuper2(value, func):
    helpers.parallel_select(_super(value), func)


@EvalArg('value', object)
def _require(value):
    if value is None:
        raise ValueError()
    return value

@EvalArg('obj', MuranoObject)
@EvalArg('class_name', str)
@ContextAware()
def _get_container(context, obj, class_name):
    namespace_resolver = helpers.get_type(context).namespace_resolver
    class_loader = helpers.get_class_loader(context)
    class_name = namespace_resolver.resolve_name(class_name)
    murano_class = class_loader.get_class(class_name)
    p = obj.parent
    while p is not None:
        if murano_class.is_compatible(p):
            return p
        p = p.parent
    return None


def register(context):
    context.register_function(_resolve, '#resolve')
    context.register_function(_cast, 'cast')
    context.register_function(_new, 'new')
    context.register_function(_id, 'id')
    context.register_function(_super2, 'super')
    context.register_function(_psuper2, 'psuper')
    context.register_function(_super, 'super')
    context.register_function(_require, 'require')
    context.register_function(_get_container, 'getContainer')

