from setuptools import setup, find_packages

setup(
    name="remenis",
    version="0.1.0",
    author="remenis-memory",
    description="Lightweight, sub-gigabyte long-term memory middleware for AI agents.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/remenis-memory/remenis",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Core standard library modules (sqlite3) are included with Python.
    ],
)
