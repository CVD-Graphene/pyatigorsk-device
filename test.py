import os

from PyQt5 import QtGui

os.environ.setdefault('GRAPHENE_SETTINGS_MODULE', 'Core.settings')

from Structure.system import AppSystem


def test_init_local():
    system = AppSystem(actions_list=[])


def test_call_class():
    class S(object):
        index = 0

        def __call__(self, *args, **kwargs):
            print("CALL", self.index)
            self.index += 1

    s = S()
    s()
    s()
    s()


if __name__ == '__main__':
    # test_call_class()
    test_init_local()
