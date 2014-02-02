import copy
import eventlet
from engine.dsl import helpers
from engine.dsl.murano_object import MuranoObject
from engine.dsl.murano_class import classname


@classname('com.mirantis.murano.Object')
class SysObject(MuranoObject):
    def shadowed(self, _context):
        object_store = helpers.get_shadow_object_store(_context)
        return object_store.get(self.object_id)

    def shadow(self, _context):
        object_store = helpers.get_shadow_object_store(_context)
        object_store.put(copy.deepcopy(helpers.get_this(_context)))

    def sleep(self, seconds):
        eventlet.sleep(seconds)

