import json
import types
import uuid
import yaml
import helpers


class MuranoObject(object):
    def __init__(self, murano_class, object_store, context, object_id=None,
                 frozen=False, known_classes=None):
        if known_classes is None:
            known_classes = {}
        self._object_id = object_id or uuid.uuid4().hex
        self._type = murano_class
        self._properties = {}
        self._object_store = object_store
        self._parents = {}
        self._frozen = frozen
        for property_name in murano_class.properties:
            typespec = murano_class.get_property(property_name)
            self._properties[property_name] = typespec.default
        known_classes[murano_class.name] = self
        for parent in murano_class.parents:
            parent_type_name = parent.name
            if not parent_type_name in known_classes:
                known_classes[parent_type_name] = self._parents[
                    parent_type_name] = parent.new(
                        object_store, context, None,
                        object_id=self._object_id,
                        frozen=frozen, known_classes=known_classes)
            else:
                self._parents[parent_type_name] = \
                    known_classes[parent_type_name]

    def initialize(self, **kwargs):
        frozen = self._frozen
        self._frozen = False
        try:
            for property_name, property_value in kwargs.iteritems():
                self.set_property(property_name, property_value,
                                  self._object_store)
        finally:
            self._frozen = frozen

    @property
    def object_id(self):
        return self._object_id

    @property
    def type(self):
        return self._type

    def __getattr__(self, item):
        if item.startswith('__'):
            raise AttributeError('xxx')
        return self.get_property(item)

    def get_property(self, item, caller_class=None):
        #print 'caller_class', caller_class.name
        if item in self._properties and \
                self._is_accessible(item, caller_class):
            return self._properties[item]
        i = 0
        result = None
        for parent in self._parents.values():
            try:
                result = parent.get_property(item, caller_class)
                i += 1
                if i > 1:
                    raise LookupError()
            except AttributeError:
                continue
        if not i:
            raise AttributeError()
        return result

    def set_property(self, key, value, object_store, caller_class=None):
        if self._frozen:
            raise NotImplementedError()
        if key in self._properties and self._is_accessible(key, caller_class):
            spec = self._type.get_property(key)
            self._properties[key] = spec.validate(
                value, object_store)
        else:
            for parent in self._parents.values():
                try:
                    parent.set_property(key, value, object_store, caller_class)
                    return
                except AttributeError:
                    continue
            raise AttributeError(key)

    def _is_accessible(self, property_name, caller_class):
        spec = self._type.get_property(property_name)
        if not spec:
            return False
        if spec.access == 'Public':
            return True
        if caller_class == self.type:
            return True
        return False

    def cast(self, type):
        if self.type == type:
            return self
        for parent in self._parents.values():
            try:
                return parent.cast(type)
            except TypeError as e:
                continue
        raise TypeError('Cannot cast')

    def __repr__(self):
        return yaml.dump(helpers.serialize(self))

    def to_dictionary(self):
        result = {}
        for parent in self._parents.values():
            result.update(parent.to_dictionary())
        result.update({'?': {'type': self.type.name, 'id': self.object_id}})
        result.update(self._properties)
        return result

