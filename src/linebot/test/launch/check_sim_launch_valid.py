import os
import sys

def test_sim_launch_integrity():
    # Just checking if we can parse it without error
    # and if it DOES NOT include 'camera.launch.py' (as it should simulate camera via gazebo)
    launch_path = "src/linebot/launch/sim.launch.py"
    try:
        with open(launch_path, 'r') as f:
            content = f.read()
            if "camera.launch.py" in content:
                 print(f"FAILURE: sim.launch.py seems to reference camera.launch.py which is for physical hardware.")
                 sys.exit(1)
            print("SUCCESS: sim.launch.py appears isolated from physical camera launch.")
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_sim_launch_integrity()
