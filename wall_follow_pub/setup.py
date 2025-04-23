from setuptools import setup, find_packages

package_name = 'wall_follow_pub'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Kerwin Lamberth',
    maintainer_email='Kclamberth@yahoo.com',
    description='ROS 2 wall‑following node (publisher + subscriber).',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'wall_follower = wall_follow_pub.wall_follower:main',
        ],
    },
)
