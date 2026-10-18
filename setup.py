from setuptools import setup, find_packages

setup(
    name="remenis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlite-vec>=0.1.0"
    ],
    entry_points={
        "console_scripts": [
            "remenis=remenis.cli:main",
        ],
    },
    description="Enterprise-grade AI memory middleware",
    author="Unique Tomlinson",
)
