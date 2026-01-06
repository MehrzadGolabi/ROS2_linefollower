import sys

def check_launch_logic():
    launch_path = "src/linebot/launch/robot.launch.py"
    try:
        with open(launch_path, 'r') as f:
            content = f.read()
            
        if "linefollower_ir_launch" not in content:
            print("FAILURE: linefollower_ir_launch not found")
            sys.exit(1)
            
        if "ir_condition" not in content:
            print("FAILURE: ir_condition not found")
            sys.exit(1)
            
        if "enable_ir_val =" not in content:
            print("FAILURE: enable_ir_val not found")
            sys.exit(1)
            
        print("SUCCESS: IR mode logic present")
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_launch_logic()
