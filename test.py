import os
os.environ.setdefault('GRAPHENE_SETTINGS_MODULE', 'Core.settings')

from Structure.system import CvdSystem


def test_init_local():
    system = CvdSystem()


if __name__ == '__main__':
    test_init_local()
