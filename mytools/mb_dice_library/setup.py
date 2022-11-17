from setuptools import find_packages, setup

setup(
    name='mb_dice_lib',
    packages=find_packages(include=['mb_dice_lib']),
    version='0.1.0',
    description='My dice library',
    author='Marco Baracchi',
    license='NONE',
    install_requires=[],
    test_suite='tests',
)
