[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5f7ad54d352245df9099321c281b2db2)](https://app.codacy.com/manual/CharlesAverill/satyrn?utm_source=github.com&utm_medium=referral&utm_content=CharlesAverill/satyrn&utm_campaign=Badge_Grade_Dashboard)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/satyrn-python)](https://pypi.org/project/satyrn-python/)

[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/CharlesAverill/satyrn/blob/master/LICENSE)
[![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)


[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/CharlesAverill/satyrn/graphs/commit-activity)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

[![GitHub issues](https://img.shields.io/github/issues/CharlesAverill/satyrn?label=open%20issues)](https://github.com/CharlesAverill/satyrn/issues)
[![GitHub issues-closed](https://img.shields.io/github/issues-closed-raw/CharlesAverill/satyrn?color=gree)](https://github.com/CharlesAverill/satyrn/issues?q=is%3Aissue+is%3Aclosed)

[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/charlesaverill20@gmail.com)

# Satyrn

![Satyrn](https://github.com/CharlesAverill/satyrn/blob/master/satyrn_python/static/cover.png?raw=true)
Satyrn is an alternative to Jupyter notebooks that supports branching code cells.

## What that means
Code in Satyrn is executed in "Cells", which are small blocks of code that should perform a few small functions, but share variables, functions, imports, etc. Splitting code into these Cells allows users to run lots of "setup" cells and then play around with a cell that depends on the setup to function. This prevents users from having to run lengthy code over and over again. A similar application is Jupyter's Notebook.


Most code is executed as a list of instructions,
```python
print(1)
print(2)
print(3)
```
However, Satyrn's code execution is different. Code inside of cells still executes normally, but cells are not necessarily linked linearly. One cell, which we'll call "root", can have two "Children", "childA" and "childB". Because root is the parent, it will run first. But because childA and childB are siblings on the same level in the heirarchy, they will be run <b>simultaneously</b>. This is particularly useful in situations like data analysis, where lots of data must be preprocessed before they can be used. If you have multiple sets of data to preprocess, why not preprocess them simultaneously instead of waiting for them to finish 1-by-1?

Satyrn is also a great tool for collaboration. While using the UI, the graph state is shared over your local network via a CherryPy WSGI server. This allows machines on your local network to edit the same code you're working on by navigating to your IP address in their browser, no Python/Satyrn installations required. <b>Use caution when working with Satyrn on public networks.</b>

## Contributors
- [Charles Averill](https://github.com/CharlesAverill) - Author, back- & front-end feature integration
- [Nathan Huckleberry](https://github.com/Nathan-Huckleberry) - Networking, optimization
- [Tristan Wiesepape](https://github.com/qwetboy10) - Networking, optimization
- [Ronak Malik](https://github.com/BeyondPerception) - Networking, optimization
- [Merkie](https://githuh.com/Merkie) - Frontend design
- [syrinsaya](https://github.com/syrinsaya) - UI design

[Join the dev Discord!](https://discord.gg/AEZtttJ)

## Setup
- Run `python -m pip install satyrn-python`
- Run `satyrnCLI` in your terminal to open the Satyrn CLI
- Run `satyrn` in your terminal to open the Satyrn UI (unstable)

## CLI Commands
* `quit` - Quits out of interpreter
* `cell [cell_name] [content_type](python/markdown) [add_content](y/n)`
    - Creates cell with given parameters
    - All cells require unique names
    - The first cell created will always be treated as the "root" cell, and will always be executed first in a complete execution call.
    - Set `content_type` to "python" for python cells
    - If `add_content` is "y", a text box will pop up. Input your python code here.
* `remove [cell_name]`
    - Deletes cell and its links from graph. 
* `edit [cell_name]`
    - Reopens text input window so that users can edit cells
* `link [first_cell_name] [second_cell_name]`
    - Links the two cells whose names are provided. You can technically still make branching graphs this way, but they
    will not work at all.
* `sever [first_cell_name] [second_cell_name]`
    - Severs the link between the two cells whose names are provided
* `merge [first_cell_name] [second_cell_name]`
    - Merges the two cells if they are adjacent.
* `swap [first_cell_name] [second_cell_name]`
    - Swaps the contents and names of the named cells. e.g. 
        - `a -> b -> c`
        - `swap a b`
        - `b -> a -> c`
* `execute [cell_name_1] [cell_name_2] ... >> (filename)`
    - If no cell names are defined, the entire graph will execute sequentially
    - If cell names are defined, they will execute in the order they are named
    - `>> (filename)` is optional. If included, will save stdout cell output to whatever filename is provided.
* `display [cell_name]`
    - If `cell_name` is defined, that cell's contents will be printed to the console
    - Otherwise, the entire graph will be displayed in matplotlib.
* `list`
    - Prints a list of all cell names and edge pairs in graph
* `reset_runtime`
    - Deletes all local variables created by cells.
* `reset_graph`
    - Deletes all cells and variables. Equivalent of restarting Satyrn session.
* `save [filename].satx`
    - Saves graph to .satx file.
* `[filename].satx`
    - This will run a .satx file. It's just a reformatted version of the normal Satyrn input. [This test file](examples/syntax_example.satx) shows the basic syntax rules.

## CLI Example
Here, code written in [ ] brackets was typed into the text box popup.
```
♄: cell root python y
[x = 10]
♄: cell mid python y
[x *= 22]
♄: cell bottom python y
[print(x)]
♄: link root mid
♄: link mid bottom
♄: execute
220
♄: quit
```
