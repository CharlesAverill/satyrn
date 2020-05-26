import matplotlib.pyplot as plt
import networkx as nx
import tkinter as tk

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

TextInput is just a handy way of taking multi-line input from users. 
"""


class Cell:

    def __init__(self,
                 name_,
                 graph_,
                 content_type_="code",
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

    def execute(self):
        # Execute this cell's content
        try:
            exec(self.content, self.graph.exec_globals)
        except Exception as e:
            print("Exception occurred in cell " + self.name)
            print(e)


class Graph:

    def __init__(self):
        # Networkx graph
        self.graph = nx.Graph()
        # Dict to keep track of cell names vs networkx node names
        self.indeces = {}
        # Dictionary for variables created by cells
        self.exec_globals = {}

    def reset_runtime(self):
        # Erase all runtime variables
        self.exec_globals = {}

    def name_to_idx(self, cell_name):
        """
        :param cell_name: Name of cell
        :return: Corresponding index of provided cell name
        """
        if cell_name not in list(self.indeces.keys()):
            print("Cell \"" + cell_name + "\" does not exist")
            return -1
        else:
            return self.indeces[cell_name]

    def get_cell(self, cell_name):
        """
        :param cell_name: Name of desired cell
        :return: Cell object
        """
        cells = nx.get_node_attributes(self.graph, 'data').values()
        for cell in cells:
            if cell.name == cell_name:
                return cell

    def add_cell(self, cell: Cell):
        """
        :param cell: Cell object to be added to graph
        """
        if cell.name in list(self.indeces.keys()):
            print("All cells must have unique names")
            return
        else:
            self.graph.add_node(len(self.graph.nodes), data=cell, name=cell.name)
        self.indeces.update({cell.name: len(self.indeces)})

    def remove_cell(self, name):
        """
        :param name: Name of cell to be removed
        """
        if self.get_cell(name):
            idx = self.name_to_idx(name)
            self.graph.remove_node(idx)
            del self.indeces[name]
        else:
            print("Cell \"" + name + "\" does not exist.")

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

    def display(self):
        # Display graph in matplotlib
        pos = nx.spring_layout(self.graph)
        labels = {idx: moniker for moniker, idx in zip(list(self.indeces.keys()), list(self.indeces.values()))}
        nx.draw_networkx_nodes(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos)
        nx.draw_networkx_labels(self.graph, pos, labels)
        plt.show()

    def execute_linear_graph(self):
        # Execute nodes starting from index 0 and proceeding linearly
        cells = list(nx.get_node_attributes(self.graph, 'data').values())
        for cell in cells:
            if cell.content_type == "python":
                cell.execute()


class TextInput:

    def __init__(self):
        # Root tkinter window
        self.root = tk.Tk()
        self.root.wm_title("Satyrn Text Editor")
        self.output = ""

    def get_text_from_widget(self, widget):
        """
        :param widget: Widget to pull text from
        """
        self.output = widget.get("1.0", "end")
        self.root.quit()

    def text_input(self):
        # Open text input window and return the text
        text = tk.Text(self.root)
        text.pack()
        save_close = tk.Button(self.root,
                               text="Save and Close",
                               command=lambda: self.get_text_from_widget(text))
        save_close.pack()
        self.root.mainloop()
        self.root.destroy()

        return self.output


class Interpreter:

    def __init__(self):
        # Graph object
        self.graph = Graph()
        # Assume live input first
        self.input_type = "live"
        # This will be set if the user executes a .satx file
        self.file = None
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
        keywords = ["help", "quit", "create_cell", "link", "sever", "execute", "display", "remove_cell", "reset_runtime"]
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
                ti = TextInput()
                content = ti.text_input().strip()
        self.graph.add_cell(Cell(name, self.graph, content_type, content))

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

    def execute(self, command):
        """
        :param command: command to be executed
        """
        if len(command) > 1:
            try:
                cell = self.graph.get_cell(command[1])
                cell.execute()
            except Exception as e:
                print("There was an error executing cell \"" + command[1] + "\"")
        else:
            self.graph.execute_linear_graph()

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

    def reset_runtime(self):
        # Delete all runtime variables
        self.graph.reset_runtime()

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

            elif command[0] == "create_cell":
                self.create_cell(command)

            elif command[0] == "link":
                self.link(command)

            elif command[0] == "sever":
                self.sever(command)

            elif command[0] == "execute":
                self.execute(command)

            elif command[0] == "display":
                self.display(command)

            elif command[0] == "remove_cell":
                self.remove_cell(command)

            elif command[0] == "reset_runtime" and len(command) == 1:
                self.reset_runtime()

            elif ".satx" in command[0]:
                self.run_file(command)

            else:
                print("Syntax error: command " + command[0] + " not recognized.")


i = Interpreter()
