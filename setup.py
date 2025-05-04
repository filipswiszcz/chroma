from setuptools import setup


setup(
    name="chroma",
    version="0.0.1",
    packages=["chroma", "chroma.request"],
    install_requires=["mysql-connector-python", "psutil"],
    python_requires=">=3.10"
)