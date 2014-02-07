from murano_object import MuranoObject


class AttributeStore(object):
    def __init__(self):
        self._attributes = {}

    def set(self, tagged_object, owner_type, name, value):
        if isinstance(value, MuranoObject):
            value = value.object_id

        key = (tagged_object.object_id, owner_type.name, name)
        if value is None:
            self._attributes.pop(key, None)
        else:
            self._attributes[key] = value

    def get(self, tagged_object, owner_type, name):
        return self._attributes.get(
            (tagged_object.object_id, owner_type.name, name))

    def serialize(self, known_objects):
        return [
            [key[0], key[1], key[2], value]
            for key, value
            in self._attributes.iteritems()
            if key[0] in known_objects
        ]

    def load(self, data):
        for item in data:
            if item[3] is not None:
                self._attributes[(item[0], item[1], item[2])] = item[3]