from murano_object import MuranoObject


class AttributeStore(object):
    def __init__(self):
        self._attributes = {}

    def set(self, tagged_object, owner_type, name, value):
        if isinstance(value, MuranoObject):
            value = value.object_id

        self._attributes[
            (tagged_object.object_id, owner_type.name, name)] = value

    def get(self, tagged_object, owner_type, name):
        return self._attributes.get(
            (tagged_object.object_id, owner_type.name, name))