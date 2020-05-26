import matplotlib.pyplot as plt
import networkx as nx
import tkinter as tk

print("------------------------------------------------------------------------\n"
      "Hi, and welcome to Satyrn.\n"
      "Satyrn is an experimental application that extends typical notebook functionality.\n"
      "Satyrn provides the same functionality as a typical notebook, but allows for branching.\n"
      "Therefore, cells can run in parallel. Please type \'help\' for a list of commands. Thank you!\n"
      "------------------------------------------------------------------------\n")


def update_node(node, field, update):
    new_node = node.copy()
    new_node[field] = update
    return new_node


class Cell:

    def __init__(self, name_, graph_, content_type_="code", content_=""):
        self.name = name_
        self.content_type = content_type_
        self.content = content_
        self.graph = graph_

    def execute(self):
        exec(self.content, self.graph.exec_globals)

    def __str__(self):
        return self.name


class Graph:

    def __init__(self):
        self.graph = nx.Graph()
        self.labels = []
        self.edge_labels = {}
        self.exec_globals = {}

    def name_to_idx(self, cell_name):
        if cell_name not in self.labels:
            print("Cell \"" + cell_name + "\" does not exist")
            return -1
        else:
            return self.labels.index(cell_name)

    def get_cell(self, cell_name):
        cells = nx.get_node_attributes(self.graph, 'data').values()
        for cell in cells:
            if cell.name == cell_name:
                return cell

    def add_cell(self, cell: Cell):
        if cell.name in self.labels:
            print("All cells must have unique names")
            return
        else:
            self.graph.add_node(len(self.graph.nodes), data=cell)
            self.labels.append(cell.name)

    def connect_cells(self, idx1, idx2):
        self.graph.add_edge(idx1, idx2)

    def display(self):
        pos = nx.spring_layout(self.graph)
        labels = {idx: moniker for idx, moniker in zip(range(len(self.labels)), self.labels)}
        nx.draw_networkx_nodes(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos)
        nx.draw_networkx_labels(self.graph, pos, labels)
        plt.show()

    def execute_linear_graph(self):
        cells = nx.get_node_attributes(self.graph, 'data').values()
        for cell in cells:
            if cell.content_type == "python":
                cell.execute()


class TextInput:

    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_title("Satyrn Text Editor")
        self.output = ""

    def get_text_from_widget(self, widget):
        self.output = widget.get("1.0", "end")
        self.root.quit()

    def text_input(self):
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

    keywords = ["help", "quit", "create_cell", "link", "execute", "display"]

    def __init__(self):
        self.graph = Graph()
        self.input_type = "live"
        self.file = None
        self.run()

    def run_file(self, command):
        try:
            openfile = open(command[0], "r")
            self.file = openfile.readlines()
            self.input_type = "file"
        except Exception as e:
            print(e)

    def read_input(self):
        if self.input_type == "live" or len(self.file) == 0:
            usr = input("♄: ").strip()
            self.input_type = "live"
        else:
            usr = self.file.pop(0).strip()
        usr = usr.lower()
        return usr.split()

    @staticmethod
    def print_help_menu():
        print("help menu")

    def create_cell(self, command):
        if len(command) != 4:
            print("create_cell takes 3 arguments: [name] [content_type] [add_content]")
            return
        name = command[1]
        if name in self.keywords:
            print("\"" + name + "\" is a restricted keyword and cannot be used for a node name.")
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

    def link(self, command):
        if len(command) != 3:
            print("link takes 2 arguments: [cell_1] [cell_2]")
            return
        name_1 = self.graph.name_to_idx(command[1])
        name_2 = self.graph.name_to_idx(command[2])
        self.graph.connect_cells(name_1, name_2)

    def execute(self, command):
        if len(command) > 1:
            try:
                cell = self.graph.get_cell(command[1])
                cell.execute()
            except Exception as e:
                print("There was an error executing cell \"" + command[1] + "\"")
        else:
            self.graph.execute_linear_graph()

    def display(self, command):
        if len(command) == 1:
            self.graph.display()
        else:
            if len(command) != 2:
                print("display takes 0 or 1 arguments: [name_of_cell_to_print]")
                return
            else:
                print(self.graph.get_cell(command[1]).content)

    def run(self):
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

            elif command[0] == "execute":
                self.execute(command)

            elif command[0] == "display":
                self.display(command)

            elif ".satx" in command[0]:
                self.run_file(command)

            else:
                print("Syntax error: command " + command[0] + " not recognized.")


i = Interpreter()
