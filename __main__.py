from experiment_picker import main
from common.util import load_shared_font

from dda2d.window import main as dda2d_main
from multi_variable_sorting.sorting import main as mvs_main
from animator.main import main as animator_main
from sphere.window import main as sphere_main
from heightviz.window import main as height_main

if __name__ == '__main__':
    load_shared_font("gohu")
    main(
        {
            "DDA 2D": (dda2d_main, (), {}),
            "Multi-Variable Sorting": (mvs_main, (), {}),
            "Automatic Animator": (animator_main, (), {}),
            "Sphere 3D": (sphere_main, (), {}),
            "Scale Visualizer": (height_main, (), {})
        }
    )
