import matplotlib.pyplot as plt
import networkx as nx
import io as StringIO
import tkinter as tk

import sys
import contextlib

print("------------------------------------------------------------------------\n"
      "Hi, and welcome to Satyrn.\n"
      "Satyrn is an experimental application that extends typical notebook functionality.\n"
      "Satyrn provides the same functionality as a typical notebook, but allows for branching.\n"
      "Therefore, cells can run in parallel. Please type \'help\' for a list of commands. Thank you!\n"
      "------------------------------------------------------------------------\n")

"""
Structure Guide

Cells, sometimes referred to as nodes, are data points that either hold markdown data or code. They also have names.

The Graph is a collection of Cells. We use networkx as a backend for basic graph operations and add in methods to 
provide functionality specific to our needs.

The Interpreter is the 'frontend' of the application, and provides a text-based interface for users to interact with
the graph and individual nodes.

TextIO is just a handy way of taking multi-line input from users and displaying text back to them.
"""


class TextIO:

    def __init__(self):
        # Root tkinter window
        self.root = None
        self.user_input = ""

    def get_text_from_widget(self, widget):
        """
        :param widget: Widget to pull text from
        """
        self.user_input = widget.get("1.0", "end")
        self.root.quit()

    def text_input(self, existing_text=None):
        self.root = tk.Tk()
        self.root.wm_title("Satyrn Text Editor")
        # Open text input window and return the text
        text = tk.Text(self.root)
        if existing_text:
            text.insert(1.0, existing_text)
        text.pack()

        save_close = tk.Button(self.root,
                               text="Save and Close",
                               command=lambda: self.get_text_from_widget(text))
        save_close.pack()

        self.root.mainloop()
        self.root.destroy()

        return self.user_input


class Cell:

    def __init__(self,
                 name_,
                 graph_,
                 content_type_="python",
                 content_=" "):
        """
        :param name_: The cell's name
        :param graph_: The cell's parent graph
        :param content_type_: The type of content in the cell (markdown or python)
        :param content_: The contents of the cell, either markdown or python code
        """
        self.name = name_
        self.content_type = content_type_
        self.content = content_
        self.graph = graph_

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO.StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    def execute(self, stdout):
        # Execute this cell's content
        if stdout == "internal":
            try:
                exec(self.content, self.graph.exec_globals)
            except Exception as e:
                print("Exception occurred in cell " + self.name)
                print(e)
        elif stdout == "external":
            try:
                with self.stdoutIO() as s:
                    exec(self.content, self.graph.exec_globals)
                    return s.getvalue()
            except Exception as e:
                print("Exception occurred in cell " + self.name)
                print(e)
        else:
            print("stdout setting \"" + stdout + "\" not recognized. Please use internal/external.")
            return


class Graph:

    def __init__(self):
        # Networkx Directed graph
        self.graph = nx.DiGraph()
        # Dict to keep track of cell names vs networkx node names
        self.names_to_indeces = {}
        # Dictionary for variables created by cells
        self.exec_globals = {}
        # TextIO object
        self.ti = TextIO()

    def reset_runtime(self):
        # Erase all runtime variables
        self.exec_globals = {}

    def name_to_idx(self, cell_name):
        """
        :param cell_name: Name of cell
        :return: Corresponding index of provided cell name
        """
        if cell_name not in list(self.names_to_indeces.keys()):
            print("Cell \"" + cell_name + "\" does not exist")
            return -1
        else:
            return self.names_to_indeces[cell_name]

    def get_cell(self, cell_name, cell_index=None):
        """
        :param cell_name: Name of desired cell
        :param cell_index: If this is set, it'll retrieve the cell at this index
        :return: Cell object
        """
        cells = list(nx.get_node_attributes(self.graph, 'data').values())

        if cell_index:
            return cells[cell_index]

        for cell in cells:
            if cell.name == cell_name:
                return cell

    def add_cell(self, new_cell: Cell):
        """
        :param new_cell: Cell object to be added to graph
        """
        if new_cell.name in list(self.names_to_indeces.keys()):
            print("All cells must have unique names")
            return
        else:
            self.graph.add_node(len(self.graph.nodes), data=new_cell, name=new_cell.name)

        self.names_to_indeces.update({new_cell.name: len(self.names_to_indeces)})

    def remove_cell(self, cell_name, cell_index=None):
        """
        :param cell_name: Name of cell to be removed
        :param cell_index: If this is set, it'll remove the cell at this index
        """
        if cell_index:
            cell_name = self.get_cell("", cell_index).name

            self.graph.remove_node(cell_index)
            del self.names_to_indeces[cell_name]
        elif self.get_cell(cell_name):
            idx = self.name_to_idx(cell_name)

            self.graph.remove_node(idx)
            del self.names_to_indeces[cell_name]
        else:
            print("Cell \"" + cell_name + "\" does not exist.")

    def connect_cells(self, idx1, idx2):
        """
        :param idx1: Index of first cell
        :param idx2: Index of second cell
        """
        self.graph.add_edge(idx1, idx2)

    def sever_cells(self, idx1, idx2):
        """
        :param idx1: Index of first cell
        :param idx2: Index of second cell
        """
        self.graph.remove_edge(idx1, idx2)

    def merge_cells(self, idx1, idx2, new_name, new_content_type):
        # Not fully functional yet
        if not self.graph.has_edge(idx1, idx2):
            print("To merge, cells must be adjacent")
            return

        # make new cell
        new_cell = Cell(name_=new_name, graph_=self, content_=new_content_type)
        new_content = self.get_cell("", idx1).content + "\n\n" + self.get_cell("", idx2).content
        new_cell.content = new_content

        # in -> (1 + 2 merged) -> out
        in_edges = list(self.graph.in_edges(idx1))
        out_edges = list(self.graph.out_edges(idx2))

        self.remove_cell("", idx1)
        self.remove_cell("", idx2)
        self.add_cell(new_cell)

        new_cell_index = self.name_to_idx(new_name)

        for edge in in_edges:
            in_node = edge[0]
            self.connect_cells(in_node, new_cell_index)
        for edge in out_edges:
            out_node = edge[1]
            self.connect_cells(new_cell_index, out_node)

    def display(self):
        # Display graph in matplotlib
        pos = nx.spring_layout(self.graph)

        labels = {idx: moniker for moniker, idx in
                  zip(list(self.names_to_indeces.keys()), list(self.names_to_indeces.values()))}

        nx.draw_networkx_nodes(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos)
        nx.draw_networkx_labels(self.graph, pos, labels)

        plt.show()

    def execute_linear_list_of_cells(self, cells_list=None, stdout="internal", output_filename="stdout.txt"):
        if not cells_list:
            cells_list = list(nx.get_node_attributes(self.graph, 'name').values())

        for cell_name in cells_list:
            cell = self.get_cell(cell_name)
            if cell.content_type == "python":
                cell_output = cell.execute(stdout)
                if stdout == "external":
                    with open(output_filename, 'w') as txt:
                        txt.write(cell_output)


# noinspection PyBroadException
class Interpreter:

    def __init__(self):
        # Graph object
        self.graph = Graph()
        # Assume live input first
        self.input_type = "live"
        # This will be set if the user executes a .satx file
        self.file = None
        # This determines whether or not stdout gets sent to an external textbox
        self.stdout = "internal"
        self.stdout_filename = "stdout.txt"
        # Start loop
        self.run()

    def run_file(self, command):
        """
        :param command: command to be executed
        """
        try:
            openfile = open(command[0], "r")
            self.file = openfile.readlines()
            self.input_type = "file"
        except Exception as e:
            print(e)

    def read_input(self):
        # Read input from stdin or external file. Returns list of command params.
        if self.input_type == "live" or len(self.file) == 0:
            usr = input("♄: ").strip()
            self.input_type = "live"
        else:
            usr = self.file.pop(0).strip()
            print("♄: " + usr)

        usr = usr.lower()
        return usr.split()

    @staticmethod
    def print_help_menu():
        print("help menu")

    def create_cell(self, command):
        """
        :param command: command to be executed
        """
        keywords = ["help", "quit", "create_cell", "link", "sever",
                    "execute", "display", "remove_cell", "reset_runtime"]

        if len(command) != 4:
            print("create_cell takes 3 arguments: [name] [content_type] [add_content]")
            return

        name = command[1]
        if name in keywords:
            print("\"" + name + "\" is a restricted keyword and cannot be used for a cell name.")
            return

        if ".satx" in name:
            print("Cell names cannot include \".satx\"")
            return

        content_type = command[2]
        content = ""

        if "y" in command[3]:
            if self.input_type == "file":
                temp = ""
                while ";" not in temp:
                    content += temp
                    temp = self.file.pop(0) + "\n"
            else:
                ti = TextIO()
                content = ti.text_input().strip()

        self.graph.add_cell(Cell(name, self.graph, content_type, content))

    def edit_cell(self, command):
        """
        :param command: command to be executed
        """
        if len(command) != 2:
            print("link takes 1 arguments: [cell_name]")
            return

        target_cell = self.graph.get_cell(command[1])
        old_content = target_cell.content

        ti = TextIO()
        new_content = ti.text_input(old_content).strip()

        target_cell.content = new_content

    def remove_cell(self, command):
        """
        :param command: command to be executed
        """
        self.graph.remove_cell(command[1])

    def link(self, command):
        """
        :param command: command to be executed
        """
        if len(command) != 3:
            print("link takes 2 arguments: [cell_1] [cell_2]")
            return

        name_1 = self.graph.name_to_idx(command[1])
        name_2 = self.graph.name_to_idx(command[2])

        self.graph.connect_cells(name_1, name_2)

    def sever(self, command):
        """
        :param command: command to be executed
        """
        if len(command) != 3:
            print("sever takes 2 arguments: [cell_1] [cell_2]")
            return

        name_1 = self.graph.name_to_idx(command[1])
        name_2 = self.graph.name_to_idx(command[2])

        self.graph.sever_cells(name_1, name_2)

    def merge(self, command):
        """
        :param command: command to be executed
        """
        if not (2 < len(command) < 5):
            print("merge takes 2-4 arguments: [cell_1] [cell_2] (new_name) (new_content_type)")
            return

        name_1 = self.graph.name_to_idx(command[1])
        name_2 = self.graph.name_to_idx(command[2])

        if len(command) >= 4:
            newname = command[3]
        else:
            newname = command[1] + " (merged)"

        if len(command) == 5:
            new_c_type = command[4]
        else:
            new_c_type = self.graph.get_cell(command[1]).content_type

        self.graph.merge_cells(name_1, name_2, newname, new_c_type)

    def execute(self, command):
        """
        :param command: command to be executed
        """
        if len(command) > 1:
            try:
                if ">>" in command:
                    cells_list = command[1:-2]
                    self.stdout_filename = command[-1]
                else:
                    cells_list = command[1:]
                self.graph.execute_linear_list_of_cells(cells_list, self.stdout, self.stdout_filename)
            except Exception as e:
                print("There was an error executing one of the cells")
                print(e)
        else:
            self.graph.execute_linear_list_of_cells(None, self.stdout)

    def display(self, command):
        """
        :param command: command to be executed
        """
        if len(command) == 1:
            self.graph.display()
        else:
            if len(command) != 2:
                print("display takes 0 or 1 arguments: [name_of_cell_to_print]")
                return
            else:
                print(self.graph.get_cell(command[1]).content)

    def set_stdout(self, command):
        """
        :param command: command to be executed
        """
        if len(command) != 2 or (not command[1] == "internal" and not command[1] == "external"):
            print("stdout takes 1 arguments: (internal/external)")
            return
        self.stdout = command[1]

    def reset_runtime(self):
        # Delete all runtime variables
        self.graph.reset_runtime()

    def reset_graph(self):
        confirm = input("Are you sure you want to reset the graph? This will delete all nodes and variables. (y/n) ")
        if "y" in confirm:
            self.graph = Graph()

    def run(self):
        # Main application loop
        while True:
            command = self.read_input()

            if len(command) == 0:
                continue

            elif command[0] == "help":
                self.print_help_menu()

            elif command[0] == "quit":
                break

            elif command[0] == "cell":
                self.create_cell(command)

            elif command[0] == "edit":
                self.edit_cell(command)

            elif command[0] == "remove_cell":
                self.remove_cell(command)

            elif command[0] == "link":
                self.link(command)

            elif command[0] == "sever":
                self.sever(command)

            elif command[0] == "merge":
                self.merge(command)

            elif command[0] == "execute":
                self.execute(command)

            elif command[0] == "display":
                self.display(command)

            elif command[0] == "stdout":
                self.set_stdout(command)

            elif command[0] == "reset_runtime":
                self.reset_runtime()

            elif command[0] == "reset_graph":
                self.reset_graph()

            elif ".satx" in command[0]:
                self.run_file(command)

            else:
                print("Syntax error: command \"" + command[0] + "\" not recognized.")


i = Interpreter()
