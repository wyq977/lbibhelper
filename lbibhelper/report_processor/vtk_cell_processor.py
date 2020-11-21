import os
from lbibhelper.core.settings import *
from .video import png_to_gif

CELL_DIR = "vtk_cell"
CAMERA_POS = [(125, 505, 2200), (125, 505, 0), (0, 1, 0)]  # only for 300 x 1000 box


def plot_mesh(filename, figname, plot_cell_type=True):
    # TODO: Fix colorbar location and camera location
    # TODO: change canvas resolution
    # cell_type = mesh["cell_type"]
    # blue = np.array([12 / 256, 238 / 256, 246 / 256, 1])
    # red = np.array([1, 0, 0, 1])
    # mapping = np.array([0.0, 1.0])
    # my_colormap = ListedColormap(newcolors)
    try:
        import pyvista as pv
    except ImportError:
        warning(
            "vtk python or pyvista not set up properly"
            "try installing pip install vtk==8.1.1"
            "try installing pip install pyvista"
        )

    if filename.endswith(".vtm"):
        dir = os.path.dirname(filename)
        cell_idx, _ = os.path.splitext(os.path.basename(filename))
        vtp = os.path.join(dir, cell_idx, "{}_0.vtp".format(cell_idx))
        pass
    elif filename.endswith(".vtp"):
        vtp = filename
    else:
        raise Exception("Not a valid vtp or vtm format")
    mesh = pv.read(vtp)

    if plot_cell_type:
        mesh.plot(
            cpos=CAMERA_POS,
            scalars="cell_type",
            show_edges=True,
            color=True,
            off_screen=True,
            screenshot=figname,
        )
    else:
        mesh.plot(
            cpos=CAMERA_POS,
            show_edges=True,
            color=True,
            off_screen=True,
            screenshot=figname,
        )


class vtkCellProcessor:
    def __init__(self, output_dir, force_reset=False, width=1024, height=768):
        if is_on_euler():
            module_purge()
            module_load_pyvista()
            set_headless_display(width, height)

        self.directory = output_dir
        self.width = width
        self.height = height
        self.force_reset = force_reset
        try:
            check_exists(output_dir)
        except FileNotFoundError:
            raise FileNotFoundError(
                f'"{output_dir}" does not exist. Try initilize with correct directory.'
            )

        try:
            self.vtk_cell = self.verify_output()  # .vtm
        except FileNotFoundError:
            raise FileNotFoundError(
                f'"{output_dir}" does not exist. Try initilize with correct directory.'
            )
        n_cell = len(self.vtk_cell)
        if n_cell > 30:
            print(f"Dealing with {n_cell} files, please be patient :)")

        self.cell_directory = os.path.join(self.directory, CELL_DIR)
        try:
            os.makedirs(self.cell_directory, exist_ok=True)
        except:
            raise FileNotFoundError(
                f'"{self.cell_directory}" does not exist or cannot be createed.'
            )

    def verify_output(self):
        lst = []
        for file in os.listdir(self.directory):
            if file.endswith(".vtm"):
                lst.append(file)

        if len(lst) == 0:
            raise FileNotFoundError(
                f"No cell output saved like Cells_100.vtm in {self.directory}"
            )

        print("{:d} cell output in {:s}".format(len(lst), self.directory))

        return lst

    def plot_mesh(self, plot_cell_type=True):
        for f in self.vtk_cell:
            filename, _ = os.path.splitext(os.path.basename(f))
            vtp_cell_name = os.path.join(
                self.directory, filename, "{}_0.vtp".format(filename)
            )
            mesh_png_name = os.path.join(self.cell_directory, "{}.png".format(filename))
            # skip if present
            if not self.force_reset and os.path.isfile(mesh_png_name):
                continue
            plot_mesh(vtp_cell_name, mesh_png_name, plot_cell_type=plot_cell_type)
            print(f"\rPlotting {vtp_cell_name}...", end="")

        print()

    def png_to_gif(self, frame_rate=24, output_path="Cells.gif"):
        input_files = os.path.join(self.cell_directory, "Cells_*.png")

        print(f"Making Cells.gif...")
        try:
            png_to_gif(
                input_files, frame_rate, os.path.join(self.cell_directory, output_path)
            )
        except AssertionError:
            pass
