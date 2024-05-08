from util.experiment_picker import main
from util import load_font

from dda3d.window import main as dda3d_main
from multi_variable_sorting.sorting import main as mvs_main
from animator.main import main as animator_main

if __name__ == '__main__':
    load_font()
    main(
        {
            "DDA 3D": (dda3d_main, (), {}),
            "Multi-Variable Sorting": (mvs_main, (), {}),
            "Automatic Animator": (animator_main, (), {})
        }
    )
