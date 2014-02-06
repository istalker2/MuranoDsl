import inspect
import helpers
from murano_method import MuranoMethod
from murano_object import MuranoObject
from typespec import PropertySpec


def classname(name):
    def wrapper(cls):
        cls._murano_class_name = name
        return cls
    return wrapper


class MuranoClass(object):
    def __init__(self, class_loader, namespace_resolver, name, parents=None):
        self._class_loader = class_loader
        self._methods = {}
        self._namespace_resolver = namespace_resolver
        self._name = namespace_resolver.resolve_name(name)
        self._properties = {}
        if self._name == 'com.mirantis.murano.Object':
            self._parents = []
        else:
            self._parents = parents or [
                class_loader.get_class('com.mirantis.murano.Object')]
        self.object_class = type(
            'mc' + helpers.generate_id(),
            tuple([p.object_class for p in self._parents]) or (MuranoObject,),
            {})

    @property
    def name(self):
        return self._name

    @property
    def namespace_resolver(self):
        return self._namespace_resolver


    @property
    def parents(self):
        return self._parents

    @property
    def methods(self):
        return self._methods

    def get_method(self, name):
        return self._methods.get(name)

    def add_method(self, name, payload):
        #name = self._namespace_resolver.resolve_name(name, self.name)
        method = MuranoMethod(self._namespace_resolver,
                              self, name, payload)
        self._methods[name] = method
        return method

    @property
    def properties(self):
        return self._properties.keys()

    def add_property(self, name, property_typespec):
        if not isinstance(property_typespec, PropertySpec):
            raise TypeError('property_typespec')
        self._properties[name] = property_typespec

    def get_property(self, name):
        return self._properties[name]

    def find_method(self, name):
        #resolved_name = self._namespace_resolver.resolve_name(name, self.name)
        if name in self._methods:
            return [(self, name)]
        if not self._parents:
            return []
        return list(set(reduce(
            lambda x, y: x + y,
            [p.find_method(name) for p in self._parents])))

    def invoke(self, name, executor, this, parameters):
        args = executor.to_yaql_args(parameters)
        return executor.invoke_method(name, this, None, self, *args)

    def is_compatible(self, obj):
        if isinstance(obj, MuranoObject):
            return self.is_compatible(obj.type)
        if obj is self:
            return True
        for parent in obj.parents:
            if self.is_compatible(parent):
                return True
        return False

    def new(self, parent, object_store, context, parameters=None,
            object_id=None, **kwargs):

        obj = self.object_class(self, parent, object_store, context,
                                object_id=object_id, **kwargs)
        if parameters is not None:
            argspec = inspect.getargspec(obj.initialize).args
            if '_context' in argspec:
                parameters['_context'] = context
            if '_parent' in argspec:
                parameters['_parent'] = parent
            obj.initialize(**parameters)
        return obj

    def __str__(self):
        return 'MuranoClass({0})'.format(self.name)

