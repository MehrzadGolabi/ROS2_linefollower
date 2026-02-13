from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'linefollower_ir'
setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (
            os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.[pxy][yma]*')),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Mehrzad Golabi',
    maintainer_email='mehrzadgolabi@gmail.com',
    description='5-array IR sensor line following',
    license='TODO: License declaration',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': ['linefollower_ir_node = linefollower_ir.linefollower_ir_node:main']
    },
)
