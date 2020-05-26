class Cell:

    def __init__(self, name, graph, content_type="code", content=""):
        self.name = name
        self.content_type = content_type
        self.content = content
        self.graph = graph

    def execute(self):
        exec(self.content, self.graph.exec_globals)

    def __str__(self):
        return self.name
