# Satyrn
Satyrn is a command-line-based alternative to Jupyter notebooks.
The backend is completely based on node networks, because I soon 
plan to implement branching code graphs in order to provide the user
with visual differentiation while writing code, and perhaps even 
worry-free backend multithreading. 

# Setup
* Install requirements with `python -m pip install -r requirements.txt`
* Run `python interpreter.py`

# Commands
* `quit` - Quits out of interpreter
* `create_cell [name] [content_type] [add_content](y/n)`
    - All cells require unique names
    - Set `content_type` to "python" for python cells
    - If `add_content` is "y", a text box will pop up. Input your python code here.
* `link [first_name] [second_name]`
    - Links the two cells whose names are provided. You can technically still make branching graphs this way, but they
    will not work at all.
* `execute`
    - Currently executes the linked cells sequentially. 

# Example
Here, code written in [ ] brackets was typed into the text box popup.
```
♄: create_cell root python y
[x = 10]
♄: create_cell mid python y
[x *= 20]
♄: create_cell bottom python y
[print(x)]
♄: link root mid
♄: link mid bottom
♄: execute
220
♄: quit
```