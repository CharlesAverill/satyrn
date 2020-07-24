import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='satyrn-python',
    version='0.7.7',
    entry_points={"console_scripts": ["satyrnCLI = satyrnCLI.__main__:start",
                                      "satyrn = satyrn_flask.run_frontend:run"]},
    author="Charles Averill",
    author_email="charlesaverill20@gmail.com",
    description="A Notebook alternative that supports branching code",
    long_description=long_description,
    install_requires=['networkx', 'matplotlib', 'flask'],
    long_description_content_type="text/markdown",
    url="https://github.com/CharlesAverill/satyrn/",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
