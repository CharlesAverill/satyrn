# CLI

## Commands
- `quit` - Quits out of interpreter
- `cell [cell_name] [content_type](python/markdown) [add_content](y/n)`
    - Creates cell with given parameters
    - All cells require unique names
    - The first cell created will always be treated as the "root" cell, and will always be executed first in a complete execution call.
    - Set `content_type` to "python" for python cells
    - If `add_content` is "y", a text box will pop up. Input your python code here.
- `remove [cell_name]`
    - Deletes cell and its links from graph. 
- `edit [cell_name]`
    - Reopens text input window so that users can edit cells
- `link [first_cell_name] [second_cell_name]`
    - Links the two cells whose names are provided. You can technically still make branching graphs this way, but they
    will not work at all.
- `sever [first_cell_name] [second_cell_name]`
    - Severs the link between the two cells whose names are provided
- `merge [first_cell_name] [second_cell_name]`
    - Merges the two cells if they are adjacent.
- `swap [first_cell_name] [second_cell_name]`
    - Swaps the contents and names of the named cells. e.g. 
        - `a -> b -> c`
        - `swap a b`
        - `b -> a -> c`
- `execute [cell_name_1] [cell_name_2] ...`
    - If no cell names are defined, the entire graph will execute sequentially
    - If cell names are defined, they will execute in the order they are named
- `display [cell_name]`
    - If `cell_name` is defined, that cell's contents will be printed to the console
    - Otherwise, the entire graph will be displayed in matplotlib.
- `list`
    - Prints a list of all cell names and edge pairs in graph
- `reset_runtime`
    - Deletes all local variables created by cells.
- `reset_graph`
    - Deletes all cells and variables. Equivalent of restarting Satyrn session.
- `save [filename]`
    - Saves graph, supported formats are `.satx`, `.py`, and `.ipynb`.
- `[filename]`
    - This will run a .satx file. It's just a reformatted version of the normal Satyrn input. [This test file](examples/syntax_example.satx) shows the basic syntax rules.
    
## Syntax Example
Here, code written inside [ ] brackets was typed into the text box popup.
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