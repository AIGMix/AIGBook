from setuptools import setup, find_packages

setup(
    name='aigbook',
    version='1.0.0.2',
    license="MIT Licence",
    description="",

    author='Yaronzz',
    author_email="yaronhuang@foxmail.com",

    packages=find_packages(),
    platforms="any",
    include_package_data=True,
    install_requires=["requests", "aigpy", "lxml"],
)
