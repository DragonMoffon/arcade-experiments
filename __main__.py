from experiment_picker import main
from common.util import load_shared_font

from dda2d.window import main as dda2d_main
from dda3d.window import main as dda3d_main
from marching2d.window import main as square_main
from multi_variable_sorting.sorting import main as mvs_main
from animator.main import main as animator_main
from sphere.window import main as sphere_main
from heightviz.window import main as height_main
from heightviz2d.window import main as height2d_main

if __name__ == '__main__':
    load_shared_font("gohu")
    main(
        {
            "DDA 2D": (dda2d_main, (), {}),
            "DDA 3D": (dda3d_main, (), {}),
            "Marching Squares": (square_main, (), {}),
            "Multi-Variable Sorting": (mvs_main, (), {}),
            "Automatic Animator": (animator_main, (), {}),
            "Sphere 3D": (sphere_main, (), {}),
            "Scale Visualizer 2D": (height2d_main, (), {}),
            "Scale Visualizer 3D": (height_main, (), {})
        }
    )
