from engine.dsl import helpers
from engine.dsl.murano_object import MuranoObject
from engine.dsl.murano_class import classname, MuranoClass


@classname('com.mirantis.murano.Object')
class SysObject(object):
    def setAttr(self, _context, name, value, owner=None):
        if owner is None:
            owner = helpers.get_type(helpers.get_caller_context(_context))
        if not isinstance(owner, MuranoClass):
            raise TypeError()

        attribute_store = helpers.get_attribute_store(_context)
        attribute_store.set(self, owner, name, value)

    def getAttr(self, _context, name, owner=None):
        if owner is None:
            owner = helpers.get_type(helpers.get_caller_context(_context))
        if not isinstance(owner, MuranoClass):
            raise TypeError()

        attribute_store = helpers.get_attribute_store(_context)
        return attribute_store.get(self, owner, name)
