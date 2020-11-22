import os
import platform
import multiprocessing
import subprocess
import sys

default_num_threads = multiprocessing.cpu_count()

# TODO: use colorama instead like taichi
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def is_on_euler():
    # get node name and see if its on euler
    on_euler = False
    node = platform.node()
    if node.lower().startswith("eu-login"):
        on_euler = True

    return on_euler


def get_os_name():
    name = platform.platform()
    # in python 3.8, platform.platform() uses mac_ver() on macOS
    # it will return 'macOS-XXXX' instead of 'Darwin-XXXX'
    if name.lower().startswith("darwin") or name.lower().startswith("macos"):
        return "osx"
    elif name.lower().startswith("windows"):
        return "win"
    elif name.lower().startswith("linux"):
        return "linux"
    assert False, "Unknown platform name %s" % name


def check_exists(src):
    if not os.path.exists(src):
        raise FileNotFoundError(f'File "{src}" not exist.')


def readlast(filename):
    # not pythonic, only works on unix platform
    # https://stackoverflow.com/questions/3346430/what-is-the-most-efficient-way-to-get-first-and-last-line-of-a-text-file # too complicated
    if get_os_name() == "win":
        with open(filename, "r") as f:
            res = f.readlines()[-1]
    else:
        res = subprocess.check_output(["tail", "-1", filename]).decode(
            sys.stdout.encoding
        )

    return res


# The builtin `warnings` module is unreliable as it may be supressed
# by other packages, e.g. IPython.
def warning(msg, type=UserWarning, stacklevel=1):
    import traceback

    s = traceback.extract_stack()[:-stacklevel]
    raw = "".join(traceback.format_list(s))
    print(f"{bcolors.WARNING}{bcolors.BOLD}{type.__name__}: {msg}{bcolors.ENDC}")
    print(f"{bcolors.WARNING}{bcolors.BOLD}\n{raw}{bcolors.ENDC}")


def module_purge():
    command = "module purge"
    os.system(command)


def module_load_pyvista():
    command = "module load " \
    + "new gcc/4.8.2 open_mpi/1.6.5 java/1.8.0_91 netcdf/4.3.2 python/3.6.1 " \
    + "qt/5.8.0 vtk/8.1.1 mesa/12.0.6"
    from pkg_resources import get_distribution

    assert (
        get_distribution("PyQt5").version == "5.8",
        "PyQt5 Binding version not matching with qt/5.8.0 on Euler, Please install PyQt5==5.8.0",
    )
    os.system(command)


def set_headless_display(width=1024, height=768):
    os.environ["DISPLAY"] = ":99.0"
    os.environ["PYVISTA_OFF_SCREEN"] = "true"
    os.environ["PYVISTA_USE_IPYVTK"] = "true"
    command = f"Xvfb :99 -screen 0 {width}x{height}x24 > /dev/null 2>&1 &"
    print(f"Display set to {width}x{height}, change if needed")
    os.system(command)


__all__ = [
    "set_headless_display",
    "module_load_pyvista",
    "module_purge",
    "warning",
    "readlast",
    "check_exists",
    "get_os_name",
    "is_on_euler",
]
