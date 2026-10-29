from setuptools import setup, find_packages

setup(
    name="remenis-memory",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "sqlite-vec",
    ],
    description="Zero-infra embedded memory and security governance middleware for AI agents.",
    author="Remenis Maintainers",
)
