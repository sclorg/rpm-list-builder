"""Enable direct execution of the module"""

from . import cli

cli.run.main(prog_name=__package__)
