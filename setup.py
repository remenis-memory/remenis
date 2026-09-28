from setuptools import setup, find_packages

setup(
    name="remenis",
    version="0.1.0",
    description="Lightweight local AI memory middleware with ring isolation and synthesis",
    packages=find_packages(),
    py_modules=["engine", "retriever", "synthesizer", "rings", "main"],
    python_requires=">=3.8",
)
