import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='satyrn-python',
    version='0.6.2',
    entry_points={"console_scripts": ["satyrn = satyrn_python.__main__:start"]},
    author="Charles Averill",
    author_email="charlesaverill20@gmail.com",
    description="A command-line based alternative to Jupyter notebooks",
    long_description=long_description,
    install_requires=['networkx', 'matplotlib'],
    long_description_content_type="text/markdown",
    url="https://github.com/CharlesAverill/satyrn/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
