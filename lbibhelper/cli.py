"""Console script for lbibhelper."""
import argparse
import sys

from lbibhelper.report_processor.solver_processor import SolverProcessor
from lbibhelper.report_processor.vtk_cell_processor import vtkCellProcessor
from lbibhelper.report_processor.video import png_to_gif
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
        self.banner = f"\n{'*' * 28}\n**   LBIBCell helper CLI  **\n{'*' * 28}"
        print(self.banner)

        parser = argparse.ArgumentParser(
            description="lbibhelper CLI", usage=self._usage()
        )
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
    def gif(self, arguments: list = sys.argv[2:]):
        """Convert the pictures in a directory as gif"""
        parser = argparse.ArgumentParser(
            prog="lb gif", description=f"{self.gif.__doc__}"
        )
        parser.add_argument(
            "-i", "--input_files", required=True, help="Directory of pics"
        )
        parser.add_argument("-f", "--fps", type=int, default=24, help="FPS of the gif")
        parser.add_argument(
            "-o", "--output", type=str, required=True, help="Output.gif"
        )
        args = parser.parse_args(arguments)

        try:
            check_exists(args.input_files)
        except FileNotFoundError:
            pass

        png_to_gif(args.input_files, args.fps, args.output)

    @register
    def solver(self, arguments: list = sys.argv[2:]):
        """Process solver output from LBIBCell"""
        parser = argparse.ArgumentParser(
            prog="lb solver", description=f"{self.solver.__doc__}"
        )
        parser.add_argument(
            "-i", "--input_dir", required=True, help="LBIBCell output dir"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Whether to overwrite exist files if they exist",
        )
        parser.add_argument(
            "--png", action="store_true", help="Whether to plot solve pics"
        )
        parser.add_argument(
            "--gif", action="store_true", help="Whether to make gif from *png"
        )
        args = parser.parse_args(arguments)

        try:
            check_exists(args.input_dir)
        except FileNotFoundError:
            pass

        solver_processor = SolverProcessor(args.input_dir, args.force)
        solver_processor.save_npy()
        if args.png:
            solver_processor.plot_solver()
        if args.gif:
            solver_processor.png_to_gif()

    @register
    def cell(self, arguments: list = sys.argv[2:]):
        """Process vtk cell output from LBIBCell"""
        parser = argparse.ArgumentParser(
            prog="lb cell", description=f"{self.cell.__doc__}"
        )
        parser.add_argument(
            "-i", "--input_dir", required=True, help="LBIBCell output dir"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Whether to overwrite exist files if they exist",
        )
        parser.add_argument(
            "--png", action="store_true", help="Whether to plot cell pics"
        )
        parser.add_argument(
            "--cell_type",
            action="store_true",
            default=True,
            help="Whether to plot cell type",
        )
        parser.add_argument(
            "--gif", action="store_true", help="Whether to make gif from *png"
        )
        parser.add_argument("-w", "--width", required=True, help="LBIBCell output dir")
        parser.add_argument("-h", "--height", required=True, help="LBIBCell output dir")
        args = parser.parse_args(arguments)

        try:
            check_exists(args.input_dir)
        except FileNotFoundError:
            pass

        vtk_cell_processor = vtkCellProcessor(
            args.input_dir, args.force, width=args.width, height=args.height
        )
        if args.png:
            vtk_cell_processor.plot_mesh(args.cell_type)
        if args.gif:
            vtk_cell_processor.png_to_gif()


def main():
    cli = LbibhelperMain()
    return cli()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
