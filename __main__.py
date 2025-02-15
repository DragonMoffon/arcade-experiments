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
from rectdemo.window import main as rect_main
from wavrider.window import main as wav_main
# from notifications.window import main as notif_main
from pool.window import main as pool_main
from perspective.window import main as perp_main
from progress.window import main as prog_main
from overlay.window import main as over_main
from oscilliscope.window import main as osc_main
from dos.window import main as dos_main
from portals.window import main as portal_main
from instanced.window import main as instanced_main

# TODO
from rigidbody.window import main as rigid_main

if __name__ == '__main__':
    load_shared_font("gohu")
    main(
        {   
            "DOS Terminal": (dos_main, (), {}),
            "Portal": (portal_main, (), {}),
            "Oscilliscope": (osc_main, (), {}),
            "Pool Demo [TEMP LOCATION]": (pool_main, (), {"show_fps": True}),
            "Perp Demo": (perp_main, (), {}),
            "Progressor Demo": (prog_main, (), {}),
            "DDA 2D": (dda2d_main, (), {}),
            "DDA 3D": (dda3d_main, (), {}),
            "Rect Demo": (rect_main, (), {}),
            # "Notification Demo": (notif_main, (), {}),
            "Marching Squares": (square_main, (), {}),
            "Multi-Variable Sorting": (mvs_main, (), {}),
            "Automatic Animator": (animator_main, (), {}),
            "Sphere 3D": (sphere_main, (), {}),
            "Scale Visualizer 2D": (height2d_main, (), {}),
            "Scale Visualizer 3D": (height_main, (), {}),
            "WavRider": (wav_main, (), {"show_fps": True}),
            "Overlay": (over_main, (), {}),
            "Instanced (Style Rect Takeover)": (instanced_main, (), {}),
            "Rigidbody": (rigid_main, (), {})
        }
    )
