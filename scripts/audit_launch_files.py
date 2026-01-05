import os
import fnmatch

def find_launch_files(root_dir):
    launch_files = []
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith('.launch.py') or filename.endswith('_launch.py'):
                launch_files.append(os.path.join(root, filename))
    return launch_files
