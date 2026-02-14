import os
import sys

import yaml


def test_roi_scaled():
    # Try to find the params file relative to this test script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(test_dir)
    yaml_path = os.path.join(package_dir, 'config', 'linefollower_cv_params.yaml')

    try:
        with open(yaml_path, 'r') as f:
            params = yaml.safe_load(f)
            node_params = params['linefollower_cv_node']['ros__parameters']

            # 640x480 resolution
            if node_params['roi_y_end'] > 240 or node_params['roi_x_end'] > 320:
                print('SUCCESS: ROI parameters appear scaled.')
            else:
                print('FAILURE: ROI parameters might be for 320x240 instead of 640x480.')
                sys.exit(1)
    except Exception as e:
        print(f'FAILURE: {e}')
        sys.exit(1)


if __name__ == '__main__':
    test_roi_scaled()
