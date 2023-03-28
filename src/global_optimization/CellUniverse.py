import time
from pathlib import Path
from typing import List

import numpy as np

from .Cells import CellFactory
from .Config import load_config, BaseConfig
from .Lineage import Lineage


# Helper functions
def get_image_file_paths(input_pattern: str, first_frame: int, last_frame: int, config: BaseConfig):
    """Gets the list of images that are to be analyzed."""
    z_slices = config.simulation.z_slices
    image_path_stack: List[List[Path]] = []
    i = first_frame
    try:
        while last_frame == -1 or i <= last_frame:
            input_file_stack = []
            for z in range(z_slices):
                if z_slices == 1:
                    file = Path(input_pattern % i)
                else:
                    file = Path(input_pattern % (i, z))
                if file.exists() and file.is_file():
                    input_file_stack.append(file)
                else:
                    raise ValueError(f'Input file not found "{file}"')
            i += 1
            image_path_stack.append(input_file_stack)
    except ValueError as e:
        if last_frame != -1 and len(image_path_stack) != last_frame - first_frame + 1:
            raise e
    return image_path_stack


class CellUniverse:
    def __init__(self, args):
        # --------
        #   Args
        # --------
        # TODO: move arg verification to the function that parses the args

        # set up dask client
        # if not args.no_parallel:
        #     from dask.distributed import Client, LocalCluster
        #     if not args.cluster:
        #         cluster = LocalCluster(
        #             n_workers=args.workers, threads_per_worker=1,
        #         )
        #         client = Client(cluster)
        #     else:
        #         cluster = args.cluster
        #         client = Client(cluster)
        #         client.restart()
        # else:
        #     client = None
        self.client = None

        # --------
        # Config
        # --------
        config = load_config(args.config)


        # --------
        # Cells
        # --------
        cellFactory = CellFactory(config.cellType)
        cells = cellFactory.create_cells(args.initial, z_offset = config.simulation.z_slices // 2, z_scaling = config.simulation.z_scaling)


        # --------
        # Lineage
        # --------
        image_file_paths = get_image_file_paths(args.input, args.first_frame, args.last_frame, config)
        self.lineage = Lineage(cells, image_file_paths, config, args.output, args.continue_from)

    def run(self):
        current_time = time.time()
        self.lineage.save_images(0)
        self.lineage.save_cells(0)

        print(f"Time elapsed: {time.time() - current_time:.2f} seconds")