# Satyrn

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7f9993985a9f4103848b3d41db86edbe)](https://www.codacy.com/manual/CharlesAverill/satyrn?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CharlesAverill/satyrn&amp;utm_campaign=Badge_Grade)

![](media/cover.png?raw=true)
Satyrn is a command-line-based alternative to Jupyter notebooks.
The backend is completely based on node networks, because I soon 
plan to implement branching code graphs in order to provide the user
with visual differentiation while writing code, and perhaps even 
worry-free backend multithreading. 

## Setup
* Install requirements with `python -m pip install -r requirements.txt`
* Run `python interpreter.py`

## Commands
* `quit` - Quits out of interpreter
* `cell [cell_name] [content_type](python/markdown) [add_content](y/n)`
    - Creates cell with given parameters
    - All cells require unique names
    - Set `content_type` to "python" for python cells
    - If `add_content` is "y", a text box will pop up. Input your python code here.
* `remove_cell [cell_name]`
    - Deletes cell and its links from graph. 
* `edit [cell_name]`
    - Reopens text input window so that users can edit cells
* `link [first_cell_name] [second_cell_name]`
    - Links the two cells whose names are provided. You can technically still make branching graphs this way, but they
    will not work at all.
* `sever [first_cell_name] [second_cell_name]`
    - Severs the link between the two cells whose names are provided
* `execute [cell_name_1] [cell_name_2] ... >> output_file.txt`
    - If no cell names are defined, the entire graph will execute sequentially
    - If cell names are defined, they will execute in the order they are named
    - `>> output_file.txt` is optional. If included, will save stdout cell output to `output_file.txt` or whatever filename is provided.
* `display [cell_name]`
    - If `cell_name` is defined, that cell's contents will be printed to the console
    - Otherwise, the entire graph will be displayed in matplotlib.
* `reset_runtime`
    - Deletes all local variables created by cells.
* `reset_graph`
    - Deletes all cells and variables. Equivalent of restarting Satyrn session.
* `[filename].satx`
    - This will run a .satx file. It's just a reformatted version of the normal Satyrn input. [This test file](examples/syntax_example.satx) shows the basic syntax rules.

## Example
Here, code written in [ ] brackets was typed into the text box popup.
```
♄: create_cell root python y
[x = 10]
♄: create_cell mid python y
[x *= 22]
♄: create_cell bottom python y
[print(x)]
♄: link root mid
♄: link mid bottom
♄: execute
220
♄: quit
```
