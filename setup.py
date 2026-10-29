from setuptools import setup, find_packages

setup(
    name="remenis",
<<<<<<< HEAD
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "sqlite-vec",
    ],
    description="Zero-infra embedded memory and security governance middleware for AI agents.",
=======
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
>>>>>>> 015eb83d7b2f36de80865bc3d29c39b09207bbfb
    author="Unique Tomlinson",
)
