from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pylox",
    version="1.3.0",
    author="Kusuma Bandaru",
    author_email="kusumabandaru199@gmail.com",
    description="A Python implementation of the Lox interpreter from Crafting Interpreters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=["."],
    package_dir={"": "."},
    package_data={"": ["*.py"]},
    install_requires=[],
    extras_require={
        "dev": ["flake8>=7.1.1", "pylint>=3.3.1", "black>=24.8.0"],
    },
   entry_points={
    "console_scripts": [
        "pylox = lox:main",
    ],
},
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
)