import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="b2c2-python-client",
    version="0.1.0",
    py_modules=["main"],
    install_requires=requirements,
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": ["b2c2-python-client = src.main:safe_entry_point"]
    }
)
