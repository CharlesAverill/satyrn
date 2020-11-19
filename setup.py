import setuptools

from bs4 import BeautifulSoup


version = '0.10.2'

with open("satyrn_python/templates/index.html", "r") as read_index:
    html = read_index.read()
    soup = BeautifulSoup(html, features="lxml")

    version_tag = soup.find("p", {'id': "version"})

    version_tag.string.replace_with(version)

with open("satyrn_python/templates/index.html", "w+") as write_index:
    write_index.write(str(soup.prettify()))

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='satyrn_python',
    version=version,
    entry_points={"console_scripts": ["satyrn = satyrn_python.entry_point:main"]},
    author="Charles Averill",
    author_email="charlesaverill20@gmail.com",
    description="A Notebook alternative that supports branching code",
    long_description=long_description,
    install_requires=['networkx', 'matplotlib', 'flask', 'cherrypy', 'nbformat', 'beautifulsoup4'],
    long_description_content_type="text/markdown",
    url="https://github.com/CharlesAverill/satyrn/",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    project_urls={
            "Documentation": "https://satyrn.readthedocs.io/"
    }
)
