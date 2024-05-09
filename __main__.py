from util.experiment_picker import main
from util import load_shared_font

from dda2d.window import main as dda2d_main
from multi_variable_sorting.sorting import main as mvs_main
from animator.main import main as animator_main

if __name__ == '__main__':
    load_shared_font("gohu")
    main(
        {
            "DDA 2D": (dda2d_main, (), {}),
            "Multi-Variable Sorting": (mvs_main, (), {}),
            "Automatic Animator": (animator_main, (), {})
        }
    )
