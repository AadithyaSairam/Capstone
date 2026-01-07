from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="pressure_visualizer",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
    author="Your Name",
    description="A pressure visualization tool",
    python_requires=">=3.8",
)
