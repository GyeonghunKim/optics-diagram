from setuptools import find_packages, setup


setup(
    name="optics-diagram",
    version="0.1.0",
    description="Draw optics diagrams with Python and Matplotlib",
    author="",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "matplotlib>=3.5",
    ],
    python_requires=">=3.9",
)
