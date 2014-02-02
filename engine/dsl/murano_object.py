import uuid
import yaml
import helpers


class MuranoObject(object):
    def __init__(self, murano_class, parent_obj, object_store, context,
                 object_id=None, frozen=False, known_classes=None):
        if known_classes is None:
            known_classes = {}
        self.__parent_obj = parent_obj
        self.__object_id = object_id or uuid.uuid4().hex
        self.__type = murano_class
        self.__properties = {}
        self.__object_store = object_store
        self.__parents = {}
        self.__frozen = frozen
        self.__context = context
        known_classes[murano_class.name] = self
        for parent_class in murano_class.parents:
            parent_class_name = parent_class.name
            if not parent_class_name in known_classes:
                known_classes[parent_class_name] = self.__parents[
                    parent_class_name] = parent_class.new(
                        parent_obj, object_store, context, None,
                        object_id=self.__object_id,
                        frozen=frozen, known_classes=known_classes)
            else:
                self.__parents[parent_class_name] = \
                    known_classes[parent_class_name]

    def initialize(self, **kwargs):
        frozen = self.__frozen
        self.__frozen = False
        try:
            for property_name in self.__type.properties:
                spec = self.__type.get_property(property_name)
                default = spec.default
                property_value = kwargs.get(property_name, spec.default)
                self.set_property(property_name, property_value)
            for parent in self.__parents.values():
                parent.initialize(**kwargs)
        finally:
            self.__frozen = frozen

    @property
    def object_id(self):
        return self.__object_id

    @property
    def type(self):
        return self.__type

    @property
    def parent(self):
        return self.__parent_obj

    def __getattr__(self, item):
        if item.startswith('__'):
            raise AttributeError('xxx')
        return self.get_property(item)

    def get_property(self, item, caller_class=None):
        try:
            return self.__get_property(item, caller_class)
        except AttributeError as e:
            if not caller_class:
                raise e
            try:
                obj = self.cast(caller_class)
                return obj.__properties[item]
            except KeyError:
                raise AttributeError(item)
            except TypeError:
                raise AttributeError(item)

    def __get_property(self, item, caller_class=None):
        #print 'caller_class', caller_class.name
        if item in self.__properties:
            return self.__properties[item]
        i = 0
        result = None
        for parent in self.__parents.values():
            try:
                result = parent.__get_property(item, caller_class)
                i += 1
                if i > 1:
                    raise LookupError()
            except AttributeError:
                continue
        if not i:
            raise AttributeError()
        return result

    def set_property(self, key, value, caller_class=None):
        try:
            self.__set_property(key, value, caller_class)
        except AttributeError as e:
            if not caller_class:
                raise e
            try:
                obj = self.cast(caller_class)
                obj.__properties[key] = value
            except TypeError:
                raise AttributeError(key)

    def __set_property(self, key, value, caller_class=None):
        if self.__frozen:
            raise NotImplementedError()
        if key in self.__type.properties:
            spec = self.__type.get_property(key)
            self.__properties[key] = spec.validate(
                value, self, self.__context, self.__object_store)
        else:
            for parent in self.__parents.values():
                try:
                    parent.__set_property(key, value, caller_class)
                    return
                except AttributeError:
                    continue
            raise AttributeError(key)

    def cast(self, type):
        if self.type == type:
            return self
        for parent in self.__parents.values():
            try:
                return parent.cast(type)
            except TypeError as e:
                continue
        raise TypeError('Cannot cast')

    def __repr__(self):
        return yaml.safe_dump(helpers.serialize(self))

    def to_dictionary(self):
        result = {}
        for parent in self.__parents.values():
            result.update(parent.to_dictionary())
        result.update({'?': {'type': self.type.name, 'id': self.object_id}})
        result.update(self.__properties)
        return result

