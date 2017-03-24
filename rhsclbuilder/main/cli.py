from rhsclbuilder.application import Application


def main(argv=None):
    app = Application()
    app.run(argv)
    app.exit()
