import type_scheme


class PropertyTypes(object):
    In = 'In'
    Out = 'Out'
    InOut = 'InOut'
    Runtime = 'Runtime'
    Const = 'Const'
    All = {In, Out, InOut, Runtime, Const}
    Writable = {Out, InOut, Runtime}


class Spec(object):
    def __init__(self, declaration, namespace_resolver):
        self._namespace_resolver = namespace_resolver
        self._contract = type_scheme.TypeScheme(
            declaration['Contract'])
        self._default = declaration.get('Default')
        self._has_default = 'Default' in declaration
        self._type = declaration.get('Type') or 'In'
        if self._type not in PropertyTypes.All:
            raise SyntaxError('Unknown type {0}. Must be one of ({1})'.format(
                self._type, ', '.join(PropertyTypes.All)))

    def validate(self, value, this, context,  object_store, default=None):
        if default is None:
            default = self.default
        return self._contract(value, context, this, object_store,
                              self._namespace_resolver, default)

    @property
    def default(self):
        return self._default

    @property
    def has_default(self):
        return self._has_default

    @property
    def type(self):
        return self._type


class PropertySpec(Spec):
    pass


class ArgumentSpec(Spec):
    pass