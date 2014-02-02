import inspect
from engine.dsl import classname
from agent import Agent
from agent_listener import AgentListener
from heat_stack import HeatStack
from resource_manager import ResourceManager


def _auto_register(class_loader):
    globs = globals().copy()
    for module_name, value in globs.iteritems():
        if inspect.ismodule(value):
            for class_name in dir(value):
                class_def = getattr(value, class_name)
                if inspect.isclass(class_def) and hasattr(
                        class_def, '_murano_class_name'):
                    class_loader.import_class(class_def)


def register(class_loader, path):
    _auto_register(class_loader)

    @classname('com.mirantis.murano.system.Resources')
    class ResolurceManagerWrapper(ResourceManager):
        def initialize(self, _context, _class=None):
            super(ResolurceManagerWrapper, self).initialize(
                path, _context, _class)

    class_loader.import_class(ResolurceManagerWrapper)
    class_loader.import_class(AgentListener)
    class_loader.import_class(Agent)
    class_loader.import_class(HeatStack)

