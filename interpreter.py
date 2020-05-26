import networkx as nx
import tkinter as tk
import matplotlib.pyplot as plt

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
        self.exec_globals = {}

    def name_to_idx(self, cell_name):
        if cell_name not in self.labels:
            raise Exception("That cell name does not exist")
        else:
            return self.labels.index(cell_name)

    def add_cell(self, cell: Cell):
        self.graph.add_node(len(self.graph.nodes), data=cell)
        self.labels.append(cell.name)

    def connect_cells(self, idx1, idx2):
        self.graph.add_edge(idx1, idx2)

    def display(self):
        nx.draw_networkx(self.graph, label={idx: moniker for idx, moniker in zip(range(len(self.labels)), self.labels)})
        plt.show()

    def execute_linear_graph(self):
        cells = nx.get_node_attributes(self.graph, 'data').values()
        for cell in cells:
            if cell.content_type == "python":
                cell.execute()


class TextInput:

    def __init__(self):
        self.root = tk.Tk()
        self.output = ""

    def get_text_from_widget(self, widget):
        self.output = widget.get("1.0", "end")
        self.root.destroy()

    def text_input(self):
        text = tk.Text(self.root)
        text.pack()
        save_close = tk.Button(self.root,
                               text="Save and Close",
                               command=lambda: self.get_text_from_widget(text))
        save_close.pack()
        self.root.mainloop()

        return self.output


graph = Graph()

while True:
    try:
        usr = input("♄: ").strip()
    except EOFError as e:
        usr = ""
    usr = usr.lower()
    words = usr.split()

    if len(words) == 0:
        continue

    if usr == "help":
        print("help menu")

    if usr == "quit":
        break

    if words[0] == "create_cell":
        if len(words) != 4:
            raise Exception("create_cell takes 3 arguments: name content_type add_content")
        name = words[1]
        content_type = words[2]
        content = ""
        if words[3] == "y":
            ti = TextInput()
            content = ti.text_input().strip()
        graph.add_cell(Cell(name=name, graph=graph, content_type=content_type, content=content))

    if words[0] == "link":
        if len(words) != 3:
            raise Exception("link takes 2 arguments: cell_1 cell_2")
        name_1 = graph.name_to_idx(words[1])
        name_2 = graph.name_to_idx(words[2])
        graph.connect_cells(name_1, name_2)

    if words[0] == "execute":
        graph.execute_linear_graph()
