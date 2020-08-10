import os
import random
import string
from contextlib import redirect_stdout
from io import StringIO

from flask import Flask, render_template, request
from .interpreter import Interpreter, Cell

interpreter = Interpreter()


def new_name():
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(5)))
    return result_str


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.root_path = os.path.dirname(os.path.abspath(__file__)[:-6])
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    interpreter.create_cell(["create_cell", "root", "python", "n"])

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/canvas.html")
    def canvas():
        return render_template("canvas.html")

    @app.route("/static/<string:static_file>")
    def static_handling(static_file):
        return render_template(static_file)

    @app.route("/create_cell/", methods=["GET"])
    def create_cell():
        name = new_name()
        interpreter.create_cell(["create_cell", name, "python", "n"])
        return name

    @app.route("/destroy_cell/", methods=["POST"])
    def destroy_cell():
        cell_name = request.get_json().strip()

        cell = interpreter.graph.get_cell(cell_name)

        initial_length = len(interpreter.graph.graph.nodes())

        interpreter.remove_cell(["remove", cell_name])

        success = "false"
        if not initial_length == len(interpreter.graph.graph.nodes()):
            success = "true"

        return {'success': success,
                'name': cell.name,
                'content': cell.content,
                'content_type': cell.content_type}

    @app.route("/edit_cell/", methods=["POST"])
    def edit_cell():
        data = request.get_json()
        cell_name = data['name'].strip()
        content = data['content'].strip()

        interpreter.set_cell_contents(['edit_cell', cell_name, content])

        return "true"

    @app.route("/rename_cell/", methods=["POST"])
    def rename_cell():
        data = request.get_json()
        old = data['old_name'].strip()
        new = data['new_name'].strip()

        if new in interpreter.graph.get_all_cells_edges()[0]:
            return "false"

        interpreter.rename_cell(['edit_cell', old, new])

        return "true"

    @app.route("/recursion_check/", methods=["POST"])
    def recursion_check():
        data = request.get_json()
        cell_name = data['cell_name'].strip()

        nodes, _, edge_names = interpreter.graph.get_all_cells_edges()

        for e in edge_names:
            if e[0] == cell_name:
                return "warning"

        return "safe"

    @app.route("/root_has_outputs/", methods=["POST"])
    def root_output_check():
        c = 0

        nodes, _, edge_names = interpreter.graph.get_all_cells_edges()
        root_cell_name = interpreter.graph.get_cell("", 0).name

        for e in edge_names:
            if e[0] == root_cell_name:
                c += 1

        if c > 0:
            return "safe"

        return "warning"

    @app.route("/link_cells/", methods=["POST"])
    def link_cells():
        data = request.get_json()
        first = data['first'].strip()
        second = data['second'].strip()

        if first == second:
            return "false"

        interpreter.link(['link', first, second])

        return "true"

    @app.route("/bfs_execute/", methods=["POST"])
    def bfs_execute():
        interpreter.std_capture = StringIO()
        with redirect_stdout(interpreter.std_capture):
            interpreter.execute(["execute"])
        return "true"

    @app.route("/shutdown/", methods=["POST"])
    def shutdown():
        raise KeyboardInterrupt

    @app.route("/get_satx_text/", methods=["POST"])
    def get_satx_text():
        satx_txt = interpreter.graph.get_satx_as_txt()
        return satx_txt

    @app.route("/reset_runtime/", methods=["POST"])
    def reset_runtime():
        interpreter.reset_runtime()
        return "done"

    @app.route("/dupe_cell/", methods=["POST"])
    def dupe_cell():
        data = request.get_json()
        cell_name = data['cell_name'].strip()

        og_cell = interpreter.graph.get_cell(cell_name)

        new_cell = Cell(og_cell.name + "-copy", og_cell.content_type, og_cell.content, og_cell.stdout)
        interpreter.graph.add_cell(new_cell)

        return {'cell_name': new_cell.name,
                'content': new_cell.content,
                'content_type': new_cell.content_type}

    @app.route("/graph_has_name/", methods=["POST"])
    def check_for_graph_has_name():
        cell_name = request.get_json().strip()

        if cell_name in interpreter.graph.get_all_cells_edges()[0]:
            return "true"
        return "false"

    @app.route("/dynamic_cell_output/", methods=["GET"])
    def get_dynamic_cell_output():
        if interpreter.graph.executing:
            return interpreter.std_capture.getvalue()
        return "<!--SATYRN_DONE_EXECUTING-->" + interpreter.std_capture.getvalue() + (
            "<execution complete>" if len(interpreter.std_capture.getvalue()) > 0 else "")

    @app.route("/load_graph/", methods=["POST"])
    def load_graph():
        if request.get_json()['load_from_file']:
            interpreter.reset_graph(False)
            raw = request.get_json()['file_contents']
            content = raw.split("\n")
            interpreter.run_string(content)

        cell_names = interpreter.graph.get_all_cells_edges()[0]
        links = interpreter.graph.get_all_cells_edges()[1]

        names = []
        contents = []
        content_types = []
        outputs = []
        lefts = []
        tops = []

        for cn in cell_names:
            cell = interpreter.graph.get_cell(cn)
            names.append(cn)
            contents.append(cell.content)
            content_types.append(cell.content_type)
            outputs.append(cell.output)
            lefts.append(cell.left)
            tops.append(cell.top)

        return {'names': names,
                'contents': contents,
                'content_types': content_types,
                'links': links,
                'lefts': lefts,
                'tops': tops}

    @app.route("/set_as_md/", methods=["POST"])
    def set_as_md():
        cell_name = request.get_json()['cell_name']
        interpreter.graph.get_cell(cell_name).content_type = "markdown"

        return "true"

    @app.route("/set_as_py/", methods=["POST"])
    def set_as_py():
        cell_name = request.get_json()['cell_name']
        interpreter.graph.get_cell(cell_name).content_type = "python"

        return "true"

    @app.route("/reset_graph/", methods=["POST"])
    def reset_graph():
        interpreter.reset_graph(False)
        interpreter.create_cell(["create_cell", "root", "python", "n"])
        return "true"

    @app.route("/child_cell/", methods=["POST"])
    def add_child():
        parent_name = request.get_json()['parent_name'].strip()
        child_name = new_name()

        interpreter.create_cell(["create_cell", child_name, "python", "n"])
        interpreter.link(['link', parent_name, child_name])

        return child_name

    @app.route("/individual_execute/", methods=["POST"])
    def individual_execute():
        cell_name = request.get_json()['cell_name'].strip()
        with redirect_stdout(interpreter.std_capture):
            interpreter.execute(["execute", cell_name])

        return "true"

    @app.route("/clear_output/", methods=["POST"])
    def clear_dco():
        interpreter.std_capture = StringIO()

        return "true"

    @app.route("/get_py_text/", methods=["POST"])
    def get_py_text():
        py_txt = interpreter.graph.get_py_file()
        return py_txt

    return app
