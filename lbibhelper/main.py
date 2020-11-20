"""Console script for lbibhelper."""
import argparse
import sys

from lbibhelper.report_processor.solver_processor import SolverProcessor
from lbibhelper.core.settings import check_exists


def registerableCLI(cls):
    """Class decorator to register methodss with @register into a set."""
    cls.registered_commands = set([])
    for name in dir(cls):
        method = getattr(cls, name)
        if hasattr(method, "registered"):
            cls.registered_commands.add(name)
    return cls


def register(func):
    """Method decorator to register CLI commands."""
    func.registered = True
    return func


@registerableCLI
class LbibhelperMain:
    def __init__(self, test_mode: bool = False):
        self.banner = f"\n{'*' * 43}\n**      LBIBCell helper function Programming Language      **\n{'*' * 43}"
        print(self.banner)

        print(self._get_friend_links())

        parser = argparse.ArgumentParser(description="Taichi CLI", usage=self._usage())
        parser.add_argument("command", help="command from the above list to run")

        # Flag for unit testing
        self.test_mode = test_mode

        self.main_parser = parser

    def __call__(self):
        # Print help if no command provided
        if len(sys.argv[1:2]) == 0:
            self.main_parser.print_help()
            return 1

        # Parse the command
        args = self.main_parser.parse_args(sys.argv[1:2])

        if args.command not in self.registered_commands:
            print(f"{args.command} is not a valid command!")
            self.main_parser.print_help()
            return 1

        return getattr(self, args.command)(sys.argv[2:])

    def _usage(self) -> str:
        """Compose deterministic usage message based on registered_commands."""
        # TODO: add some color to commands
        msg = "\n"
        space = 20
        for command in sorted(self.registered_commands):
            msg += f"    {command}{' ' * (space - len(command))}|-> {getattr(self, command).__doc__}\n"
        return msg

    @register
    def solver(self, arguments: list = sys.argv[2:]):
        """Make a video using *.png files in the current directory"""
        parser = argparse.ArgumentParser(
            prog="lb solver", description=f"{self.solver.__doc__}"
        )
        parser.add_argument(
            "-i",
            "--input_dir",
            required=True,
        )
        parser.add_argument("--png", action="store_true")
        parser.add_argument("--gif", action="store_true")
        args = parser.parse_args(arguments)

        try:
            check_exists(args.input_dir)
        except FileNotFoundError:
            pass

        solver_processor = SolverProcessor(args.input_dir)
        solver_processor.save_npy()
        if args.png:
            solver_processor.plot_solver()
        if args.png:
            solver_processor.png_to_gif()


def main():
    cli = LbibhelperMain()
    return cli()


if __name__ == "__main__":
    sys.exit(main())
