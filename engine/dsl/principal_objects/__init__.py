import sys_object


def register(class_loader):
    class_loader.import_class(sys_object.SysObject)
