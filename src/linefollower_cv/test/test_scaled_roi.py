import yaml
import sys

def test_roi_scaled():
    yaml_path = "src/linefollower_cv/config/linefollower_cv_params.yaml"
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            params = data['linefollower_cv_node']['ros__parameters']
            
            # Expected values for 320x240
            if params['roi_y_end'] != 240:
                print(f"FAILURE: roi_y_end should be 240, got {params['roi_y_end']}")
                sys.exit(1)
            if params['roi_x_end'] > 320:
                print(f"FAILURE: roi_x_end should be <= 320, got {params['roi_x_end']}")
                sys.exit(1)
            print("SUCCESS: ROI parameters appear scaled.")
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_roi_scaled()
