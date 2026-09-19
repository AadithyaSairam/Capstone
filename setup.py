from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="pressure_visualizer",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
    author="Aadithya Sairam",
    description="Pressure sensing and visualisation for an adjustable paediatric prosthetic socket",
    python_requires=">=3.8",
)
