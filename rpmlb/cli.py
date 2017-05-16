import sys

from rpmlb.app import Application


def main(argv=None):
    app = Application()
    is_success = app.run(argv)
    sys.exit(0 if is_success else 1)
