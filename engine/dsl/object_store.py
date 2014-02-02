import helpers
from murano_object import MuranoObject


class ObjectStore(object):
    def __init__(self, class_loader, parent_store=None, frozen=False):
        self._class_loader = class_loader
        self._parent_store = parent_store
        self._store = {}
        self._frozen = frozen

    @property
    def class_loader(self):
        return self._class_loader

    def get(self, object_id):
        if object_id in self._store:
            return self._store[object_id]
        if self._parent_store:
            return self._parent_store.get(object_id)
        return None

    def put(self, murano_object):
        self._store[murano_object.object_id] = murano_object

    def load(self, value, parent, context):
        tmp_store = ObjectStore(self._class_loader, self)

        if '?' not in value or 'type' not in value['?']:
            raise ValueError()
        system_key = value['?']
        #del value['?']
        object_id = system_key['id']
        obj_type = system_key['type']
        class_obj = self._class_loader.get_class(obj_type)
        if not class_obj:
            raise ValueError()
        obj = class_obj.new(parent, tmp_store, context=context,
                            object_id=object_id, frozen=self._frozen)
        tmp_store._store[object_id] = obj
        obj.initialize(**value)

        if not self._frozen:
            executor = helpers.get_executor(context)
            methods = obj.type.find_method('initialize')
            for cls, method in methods:
                cls.invoke(method, executor, obj, {})
        self._store.update(tmp_store._store)
        return obj