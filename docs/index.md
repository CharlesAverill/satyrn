# Satyrn

![Satyrn](media/cover.png?raw=true =.5x)

## Installation
Satyrn can be installed via pip: `pip install satyrn-python`

## Launching
Run `satyrn` to launch the UI with default settings

## Command Line Arguments
The `satyrn` keyword precedes all arguments

- `cli` - launches the CLI

- `ui` - launches the UI (default behavior)

- `-h, --hidden` - Starts the UI on 127.0.0.1 instead of 0.0.0.0, preventing machines on your local network to access 
your Satyrn instance

- `-p n, --port=n` - Designates the port for the UI to run on (default is 20787)

- `-l n, --lang=n` - Sets UI Language. Currently supported:
	- `english` (default)
	- `latin`

- `-q --quiet` - Quiet startup + shutdown

## UI Shutdown
The UI can be shutdown with the `Kernel > Shutdown` menu option if no cells are being executed.
If any cell is being executed, 1-3 `Ctrl+c`'s must be provided to the command line you ran the `satyrn` command in.
