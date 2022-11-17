from setuptools import find_packages, setup

setup(
    name='mb_common_lib',
    packages=find_packages(include=['mb_common_lib']),
    version='0.1.0',
    description='My common library',
    author='Marco Baracchi',
    license='NONE',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)