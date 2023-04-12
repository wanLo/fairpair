from setuptools import setup

setup(
    author='Georg Ahnert',
    description='Create and evaluate pairwise comparison graphs',
    name='fairpair',
    version='0.1.0',
    license='MIT',
    packages=['fairpair'],
    install_requires=[
        'pandas>=1.5.3',
        'numpy>=1.24.1',
        'networkx>=3.0'
    ],
    python_requires='>=3.11'
)