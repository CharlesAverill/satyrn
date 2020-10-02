import networkx as nx
import matplotlib.pyplot as plt
from io import StringIO
from networkx import algorithms

try:
    import tkinter as tk
except ImportError as error:
    print(error)
    print("Your Python installation may not be configured for TKinter, a dependency of Satyrn")
    print("Visit https://tkdocs.com/tutorial/install.html to install TKinter")
    exit(1)

import threading

exec_vars = {}

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
        """Used to receive text input for Cells."""
        # Root tkinter window
        self.root = None
        self.user_input = ""

    def get_text_from_widget(self, widget):
        """:param widget: Widget to pull text from."""
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
                 content_type_="python",
                 content_=" ",
                 top_=10,
                 left_=10):
        """
        :param name_: The cell's name
        :param content_type_: The type of content in the cell (markdown or python)
        :param content_: The contents of the cell, either markdown or python code
        :param top_: Cell's top position for the frontend
        :param left_: Cell's left position for the frontend
        """
        self.name = name_
        self.content_type = content_type_
        self.content = content_
        self.output = ""

        self.top = top_
        self.left = left_

    def get_copy(self):
        output_cell = Cell(self.name, self.content_type, self.content)
        output_cell.top = self.top
        output_cell.left = self.left
        return output_cell

    def execute(self):
        # Execute this cell's content

        if not self.content_type == "python":
            return

        global exec_vars
        ex_vars_copy = exec_vars.copy()

        try:
            print("<" + self.name + ">")
            exec(self.content, ex_vars_copy)
        except Exception as exception:
            print("Exception occurred in cell " + self.name)
            print(exception)

        exec_vars.update(ex_vars_copy)


class Graph:

    def __init__(self, parent):
        """Contains Cell objects and traverses them for execution."""
        # Networkx Directed graph
        self.graph = nx.DiGraph()
        self.parent = parent
        # Dict to keep track of cell names vs networkx node names
        self.names_to_indeces = {}
        # Dictionaries for variables created by cells
        global exec_vars
        exec_vars = {}
        # TextIO object
        self.ti = TextIO()

        self.executing = False

    def get_lookup_table(self):
        return {idx: moniker for moniker, idx in
                zip(list(self.names_to_indeces.keys()), list(self.names_to_indeces.values()))}

    def name_to_idx(self, cell_name):
        """
        :param cell_name: Name of cell
        :return: Corresponding index of provided cell name
        """
        cell_name = cell_name.strip()
        if cell_name not in self.get_all_cells_edges()[0]:
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

        if cell_index is not None:
            output = cells[cell_index]
            return output

        for cell in cells:
            if cell.name == cell_name:
                return cell

    def add_cell(self, new_cell: Cell):
        """:param new_cell: Cell object to be added to graph."""
        if new_cell.name in list(self.names_to_indeces.keys()):
            print("Cannot use name {}, all cells must have unique names".format(new_cell.name))
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
            return -1

    def connect_cells(self, idx1, idx2):
        """
        :param idx1: Index of first cell
        :param idx2: Index of second cell
        """

        if not (self.graph.has_node(idx1) and self.graph.has_node(idx2)):
            return

        if idx2 == 0:
            return "Can't link to root cell"

        if idx2 in nx.ancestors(self.graph, idx1):
            return "Cycles are not allowed"
        else:
            self.graph.add_edge(idx1, idx2)
            return "Safe"

    def sever_cells(self, idx1, idx2):
        """
        :param idx1: Index of first cell
        :param idx2: Index of second cell
        """
        self.graph.remove_edge(idx1, idx2)

    def swap_cells(self, name1, name2):

        old_cell1 = self.get_cell(name1)
        old_cell2 = self.get_cell(name2)

        cell1 = Cell(name2, old_cell2.content_type, old_cell2.content)
        cell2 = Cell(name1, old_cell1.content_type, old_cell1.content)

        idx1 = self.name_to_idx(name1)
        idx2 = self.name_to_idx(name2)

        self.graph.nodes[idx1]["data"] = cell1
        self.graph.nodes[idx1]["name"] = name2

        self.graph.nodes[idx2]["data"] = cell2
        self.graph.nodes[idx2]["name"] = name1

        self.names_to_indeces[name1] = idx2
        self.names_to_indeces[name2] = idx1

    def merge_cells(self, idx1, idx2, new_name):
        if not self.graph.has_edge(idx1, idx2):
            print("To merge, cells must be adjacent")
            return

        c1 = self.get_cell("", idx1)
        c2 = self.get_cell("", idx2)

        glb = c1.self_globals
        lcl = c1.self_locals

        glb.update(c2.self_globals)
        lcl.update(c2.self_locals)

        # make new cell
        new_cell = Cell(new_name, content_type_=self.get_cell("", idx1).content_type)
        new_content = self.get_cell("", idx1).content + "\n# merge point\n" + self.get_cell("", idx2).content
        new_cell.content = new_content
        self.names_to_indeces[new_name] = self.names_to_indeces[self.get_cell("", idx1).name]
        del self.names_to_indeces[self.get_cell("", idx1).name]
        self.graph.nodes[idx1]["data"] = new_cell
        self.graph.nodes[idx1]["name"] = new_name

        # in -> (1 + 2 merged) -> out
        out_edges = list(self.graph.out_edges(idx2))

        self.remove_cell("", idx2)

        for edge in out_edges:
            out_node = edge[1]
            self.connect_cells(idx1, out_node)

    def update_reverse_lookup_table(self):
        cell_names, _, _2 = self.get_all_cells_edges()
        cell_indeces = list(self.graph.nodes)
        self.names_to_indeces = {name: idx for name, idx in zip(cell_names, cell_indeces)}

    def display(self):
        # Display graph in matplotlib
        pos = nx.spring_layout(self.graph)

        self.update_reverse_lookup_table()
        labels = self.get_lookup_table()

        nx.draw_networkx_nodes(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos)
        nx.draw_networkx_labels(self.graph, pos, labels)

        plt.show()

    def get_all_cells_edges(self):
        lookup_table = self.get_lookup_table()
        return list(nx.get_node_attributes(self.graph, 'name').values()), list(self.graph.edges), \
               [(lookup_table[idx1], lookup_table[idx2]) for idx1, idx2 in list(self.graph.edges)]

    def get_in_out_edges(self, cell_name, cell_index=None):
        if not cell_index:
            cell_index = self.name_to_idx(cell_name)

        lookup_table = self.get_lookup_table()

        in_edges = []
        in_edges_idx = self.graph.in_edges(cell_index)
        for edge in in_edges_idx:
            idx_1 = edge[0]
            idx_2 = edge[1]
            str_edge = "" + str(lookup_table[idx_1]) + " -> " + str(lookup_table[idx_2])
            in_edges.append(str_edge)

        out_edges = []
        out_edges_idx = self.graph.out_edges(cell_index)
        for edge in out_edges_idx:
            idx_1 = edge[0]
            idx_2 = edge[1]
            str_edge = "" + str(lookup_table[idx_1]) + " -> " + str(lookup_table[idx_2])
            out_edges.append(str_edge)

        return in_edges, out_edges

    def get_layer(self, cell_name):
        layer = {}
        toposorted_ls = list(nx.topological_sort(self.graph))
        idx = self.name_to_idx(cell_name)

        if len(toposorted_ls) < 1:
            return

        layer[0] = 1

        for node in toposorted_ls:
            if node == 0:
                continue
            for parent in algorithms.dag.ancestors(self.graph, node):
                layer[node] = max((layer[node] if node in layer.keys() else 0),
                                  (layer[parent] + 1 if parent in layer.keys() else 0))
        if idx in layer.keys():
            return layer[idx]
        return -1

    def execute_linear_list_of_cells(self, cells_list):
        std_file_out = ""

        for cell_name in cells_list:
            cell = self.get_cell(cell_name)

            p = threading.Thread(target=cell.execute)

            if cell.content_type == "python":
                p.start()
                p.join()

            std_file_out += cell.output

    def bfs_traversal_execute(self):
        import time
        if len(self.get_all_cells_edges()[0]) == 0:
            return

        self.executing = True

        root_cell = self.get_cell("", 0)

        root = threading.Thread(target=root_cell.execute)

        std_file_out = root_cell.name

        root.start()
        root.join()

        std_file_out += root_cell.output

        n_ = self.graph.neighbors(0)
        neighbors = [n for n in n_]

        while neighbors:
            new_neighbors = []
            processes = []
            for n in neighbors:
                neighbor_cell = self.get_cell(self.get_lookup_table()[n].strip())

                neighbor = threading.Thread(target=neighbor_cell.execute)

                neighbor.start()
                processes.append(neighbor)

                new_neighbors.extend([i for i in self.graph.neighbors(n)])

            # TODO : check if this is broken
            for proc in processes:
                proc.join()

            for n in neighbors:
                time.sleep(.05)
                neighbor = self.get_cell(self.get_lookup_table()[n])
                std_file_out += "<" + neighbor.name + ">\n"
                std_file_out += neighbor.output

            neighbors = new_neighbors

        self.executing = False

    def save_graph(self, filename):
        txtout = self.get_satx_as_txt()

        filename = filename.replace("\"", "")

        with open(filename, "w+") as file:
            file.write(txtout)

    def get_satx_as_txt(self):
        txtout = ""

        lookup_table = self.get_lookup_table()
        cell_names, edges, _ = self.get_all_cells_edges()
        cells = [self.get_cell(cn) for cn in cell_names]

        for c in cells:
            if c.content:
                fill_with_code = "y:\n"
            else:
                fill_with_code = "n\n"
            temp_text = "cell " + c.name + " " + c.content_type + " " + fill_with_code
            if fill_with_code == "y:\n":
                temp_text += c.content + "\n;\n"

            txtout += temp_text

        for edge in edges:
            name1 = lookup_table[edge[0]]
            name2 = lookup_table[edge[1]]
            txtout += "link " + name1 + " " + name2 + "\n"

        if self.parent.std_capture.getvalue():
            txtout += "<!--SATYRN_DCO_START-->\n"
            txtout += self.parent.std_capture.getvalue()
            txtout += "<execution complete>\n<!--SATYRN_DCO_END-->"

        return txtout

    def get_py_file(self):
        txtout = ""

        cell_names, edges, _ = self.get_all_cells_edges()
        cells = [self.get_cell(cn) for cn in cell_names]

        for c in cells:
            txtout += "# <" + c.name + ">\n"
            if c.content_type == "python":
                txtout += c.content + "\n"
            else:
                txtout += "\"\"\"\n" + c.content + "\n\"\"\"\n"

        txtout += "# <EOF>"

        return txtout

    def get_ipynb_file(self):
        from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
        from nbformat.v4.nbjson import JSONWriter

        json_writer = JSONWriter()

        nb = new_notebook()

        cell_names, edges, _ = self.get_all_cells_edges()
        cells = [self.get_cell(cn) for cn in cell_names]

        for c in cells:
            if c.content_type == "python":
                nb.cells.append(new_code_cell(c.content, metadata={'name': c.name}))
            else:
                nb.cells.append(new_markdown_cell(c.content, metadata={'name': c.name}))

        return json_writer.writes(nb)


class Interpreter:

    def __init__(self):
        """Contains Graph object and interprets user input."""
        # Graph object
        self.graph = Graph(self)
        # Assume live input first
        self.input_type = "live"
        # This will be set if the user executes a .satx file
        self.file = None
        # Start loop
        self.std_capture = StringIO()

        self.filename = "Untitled.SATX"

        self.lock = threading.Lock()

    def run_file(self, command):
        """:param command: command to be executed."""
        try:
            openfile = open(command[0], "r")
            self.file = openfile.readlines()
            self.run_string(self.file)
        except Exception as exception:
            print(exception)

    def run_string(self, content):
        self.file = content
        self.input_type = "file"

        reading_dco_output = False
        reading_positioning = False

        while len(content) > 0:
            command = content.pop(0).split(" ")

            if "<!--SATYRN_DCO_START-->" in command[0]:
                reading_dco_output = True
                continue
            if "<!--SATYRN_DCO_END-->" in command[0]:
                reading_dco_output = False
                continue

            if reading_dco_output:
                self.std_capture.write(" ".join(command) + "\n")
                continue

            if "<!--SATYRN_POSITIONING_START-->" in command[0]:
                reading_positioning = True
                continue

            if "<!--SATYRN_POSITIONING_END-->" in command[0]:
                reading_positioning = False
                continue

            if reading_positioning:
                self.graph.get_cell(command[0]).left = command[1]
                self.graph.get_cell(command[0]).top = command[2]
                continue

            if len(command) == 0 or command == '':
                continue

            elif command[0] == "help":
                print(self.help_menu())

            elif command[0] == "quit":
                break

            self.command_switch(command)

    def read_input(self):
        # Read input from stdin or external file. Returns list of command params.
        if self.input_type == "live" or len(self.file) == 0:
            usr = input(u'\u2644' + ": ").strip()
            self.input_type = "live"
        else:
            usr = self.file.pop(0).strip()
            print(u'\u2644' + ": " + usr)

        usr = usr.lower()
        return usr.split()

    @staticmethod
    def help_menu():
        help_menu = {
            "cell [cell_name] [content_type](python/markdown) [add_content](y/n)": "Creates a cell with the specified "
                                                                                   "parameters",
            "remove [cell_name_1] [cell_name_2] ...": "Removes all listed cells",
            "edit [cell_name]": "Edit contents of cell with specified name",
            "link [first_cell_name] [second_cell_name]": "Creates link from first_cell to second_cell",
            "sever [first_cell_name] [second_cell_name]": "Removes link between first_cell and second_cell",
            "merge [first_cell_name] [second_cell_name]": "Merges the two cells if they are adjacent",
            "swap [first_cell_name] [second_cell_name]": "Swaps name, content type, and contents of specified cells",
            "execute [cell_name_1] [cell_name_2] ...": "Executes graph. If no cell names are provided, "
                                                       "all will be executed. \n\t\t",
            "display [cell_name]": "Displays graph. If cell_name defined, that cell's details will be printed out",
            "list": "Prints out names of all cells in graph",
            "reset_runtime": "Deletes all variables created within cells",
            "reset_graph": "Deletes all variables and cells. Equivalent to restarting satyrn_python session",
            "save [filename].satx": "Saves graph to .satx file",
            "[filename].satx": "Executes satyrn_python code in specified file. File must have .satx extension. "
                               "\n\t\tExamples of "
                               "syntax can be seen at https://github.com/CharlesAverill/satyrn/tree/master/examples ",
            "quit": "Exits satyrn_python session"
        }
        output = ("------------------------------------------------------------------------\n"
                  "Hi, and welcome to Satyrn.\n"
                  "Satyrn is an experimental application that extends typical notebook functionality.\n"
                  "Satyrn provides the same functionality as a typical notebook, but allows for branching.\n"
                  "Therefore, cells can run in parallel. Please type \'help\' for a list of commands. Thank you!\n"
                  "------------------------------------------------------------------------\n\n")
        help_list = [(command, description) for command, description in
                     zip(list(help_menu.keys()), list(help_menu.values()))]
        for item in help_list:
            output += "\t" + item[0] + " :\n\t\t" + item[1] + "\n\n"
        return output

    def create_cell(self, command):
        """
        :param command: command to be executed
        """
        with self.lock:
            keywords = ["help", "quit", "cell", "link", "sever",
                        "execute", "display", "remove", "reset_runtime",
                        "edit", "swap", "list", "reset_graph", "merge", "save"]

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

            self.graph.add_cell(Cell(name, content_type, content.strip()))

    def edit_cell(self, command):
        """:param command: command to be executed."""
        with self.lock:
            if len(command) != 2:
                print("edit takes 1 argument: [cell_name]")
                return

            target_cell = self.graph.get_cell(command[1])
            old_content = target_cell.content

            ti = TextIO()
            new_content = ti.text_input(old_content).strip()

            target_cell.content = new_content

    def set_cell_contents(self, command):
        with self.lock:
            target_cell = self.graph.get_cell(command[1])
            target_cell.content = command[2]

    def rename_cell(self, command):
        """:param command: command to be executed."""
        with self.lock:
            if len(command) != 3:
                print("link takes 2 arguments: [original_cell_name] [new_cell_name]")
                return

            index = self.graph.names_to_indeces[command[1]]
            og_name = self.graph.get_cell(command[1]).name

            self.graph.get_cell(og_name).name = command[2]
            self.graph.names_to_indeces.update({command[2]: index})
            del self.graph.names_to_indeces[og_name]

            for node, data in self.graph.graph.nodes(data=True):
                if data['name'] == command[1]:
                    data['name'] = command[2]
                    break

    def remove_cell(self, command):
        """:param command: command to be executed."""
        to_remove = command[1:]
        for cell in to_remove:
            i = self.graph.remove_cell(cell)
            if i == -1:
                return -1

    def link(self, command):
        """:param command: command to be executed."""
        with self.lock:
            if len(command) != 3:
                print("link takes 2 arguments: [cell_1] [cell_2]")
                return

            idx1 = self.graph.name_to_idx(command[1])
            idx2 = self.graph.name_to_idx(command[2])

            return self.graph.connect_cells(idx1, idx2)

    def sever(self, command):
        """:param command: command to be executed."""
        if len(command) != 3:
            print("sever takes 2 arguments: [cell_1] [cell_2]")
            return

        name_1 = self.graph.name_to_idx(command[1])
        name_2 = self.graph.name_to_idx(command[2])

        self.graph.sever_cells(name_1, name_2)

    def swap(self, command):
        """:param command: command to be executed."""
        if len(command) != 3:
            print("swap takes 2 arguments: [cell_1] [cell_2]")
            return
        self.graph.swap_cells(command[1], command[2])

    def merge(self, command):
        """:param command: command to be executed."""
        if not (2 < len(command) < 4):
            print("merge takes 2-3 arguments: [cell_1] [cell_2] (new_name)")
            return

        name_1 = self.graph.name_to_idx(command[1])
        name_2 = self.graph.name_to_idx(command[2])

        if len(command) >= 4:
            newname = command[3]
        else:
            newname = command[1] + "_merged"

        self.graph.merge_cells(name_1, name_2, newname)

    def execute(self, command):
        """:param command: command to be executed."""
        with self.lock:
            if ">>" in command:
                cells_list = command[1:-2]
            else:
                cells_list = command[1:]
            if len(cells_list) >= 1:
                try:
                    self.graph.execute_linear_list_of_cells(cells_list)
                except Exception as exception:
                    print("There was an error executing one of the cells")
                    print(exception)
            else:
                self.graph.bfs_traversal_execute()

    def display(self, command):
        """:param command: command to be executed."""
        if len(command) == 1:
            self.graph.display()
        else:
            if len(command) != 2:
                print("display takes 0 or 1 arguments: [name_of_cell_to_print]")
                return
            else:
                if not self.graph.get_cell(command[1]):
                    print("Cell " + command[1] + " does not exist")
                    return
                code = self.graph.get_cell(command[1]).content.strip()
                if code:
                    print("\n```\n" + code + "\n```\n")
                in_edges, out_edges = self.graph.get_in_out_edges(command[1])
                if len(in_edges) > 0:
                    print("In Edges:")
                    for edge in in_edges:
                        print(edge)
                print()
                if len(out_edges) > 0:
                    print("Out Edges:")
                    for edge in out_edges:
                        print(edge)
                    print()

    def list_cells(self):
        nodes, _, edge_names = self.graph.get_all_cells_edges()
        print("Cells:", nodes)
        print("Edges:", edge_names)

    def reset_runtime(self):
        # Delete all runtime variables
        with self.lock:
            global exec_vars
            exec_vars = {}

    def reset_graph(self, ask=True):
        if ask:
            confirm = input(
                "Are you sure you want to reset the graph? This will delete all nodes and variables. (y/n) ")
            if "y" in confirm:
                self.graph = Graph(self)
                self.reset_runtime()
                self.std_capture = StringIO()
        else:
            self.graph = Graph(self)
            self.reset_runtime()
            self.std_capture = StringIO()

    def save_graph(self, command):
        """:param command: command to be executed."""
        if len(command) != 2:
            print("save takes 1 argument1: [filename]")
            return
        output_text = ""
        if command[1].lower().endswith(".satx"):
            output_text = self.graph.get_satx_as_txt()
        elif command[1].lower().endswith(".py"):
            output_text = self.graph.get_py_file()
        elif command[1].lower().endswith(".ipynb"):
            output_text = self.graph.get_ipynb_file()
        with open(command[1], "w+") as file:
            file.write(output_text)

    def command_switch(self, command):

        if len(command) == 0:
            return

        elif command[0] == "help":
            print(self.help_menu())

        elif command[0] == "quit":
            return "break"

        elif command[0] == "cell":
            self.create_cell(command)

        elif command[0] == "edit":
            self.edit_cell(command)

        elif command[0] == "rename":
            self.rename_cell(command)

        elif command[0] == "remove":
            self.remove_cell(command)

        elif command[0] == "link":
            self.link(command)

        elif command[0] == "sever":
            self.sever(command)

        elif command[0] == "merge":
            self.merge(command)

        elif command[0] == "swap":
            self.swap(command)

        elif command[0] == "execute":
            self.execute(command)

        elif command[0] == "display":
            self.display(command)

        elif command[0] == "list":
            self.list_cells()

        elif command[0] == "reset_runtime":
            self.reset_runtime()

        elif command[0] == "reset_graph":
            self.reset_graph()

        elif command[0] == "save":
            self.save_graph(command)

        elif ".satx" in command[0]:
            self.run_file(command)

        elif len(command[0]) > 0:
            print("Syntax error: command \"" + command[0] + "\" not recognized.")

    def run(self):
        # Main application loop
        while True:
            command = self.read_input()
            if self.command_switch(command) == "break":
                break
