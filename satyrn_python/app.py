import os
import random
import string
import networkx as nx

from contextlib import redirect_stdout
from io import StringIO

from flask import Flask, render_template, request, send_file

language = ""


def new_name():
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(5)))
    return result_str


def create_app(interpreter, lang):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.root_path = os.path.dirname(os.path.abspath(__file__)[:-6])

    global language
    language = lang

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
        if str(static_file).endswith(".png"):
            return send_file("static/" + static_file, mimetype="img/png")
        return render_template(static_file)

    @app.route("/get_language/", methods=["GET"])
    def get_language():
        return language

    @app.route("/set_language/", methods=["POST"])
    def set_language():
        global language
        language = request.get_json().strip()

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

        return "200"

    @app.route("/rename_cell/", methods=["POST"])
    def rename_cell():
        data = request.get_json()
        old = data['old_name'].strip()
        new = data['new_name'].strip()

        if new in interpreter.graph.get_all_cells_edges()[0]:
            return "500"

        interpreter.rename_cell(['edit_cell', old, new])

        return "200"

    @app.route("/recursion_check/", methods=["POST"])
    def recursion_check():
        data = request.get_json()
        first = data['first'].strip()
        second = data['second'].strip()

        nodes, _, edge_names = interpreter.graph.get_all_cells_edges()

        if interpreter.graph.name_to_idx(second) == 0:
            return "Can't link to root cell"

        if interpreter.graph.name_to_idx(second) in \
                nx.ancestors(interpreter.graph.graph, interpreter.graph.name_to_idx(first)):
            return "Cycles are not allowed"

        return "200"

    @app.route("/root_has_outputs/", methods=["POST"])
    def root_output_check():
        c = 0

        nodes, _, edge_names = interpreter.graph.get_all_cells_edges()
        root_cell_name = interpreter.graph.get_cell("", 0).name

        for e in edge_names:
            if e[0] == root_cell_name:
                c += 1

        if c > 0:
            return "200"

        return "500"

    @app.route("/link_cells/", methods=["POST"])
    def link_cells():
        data = request.get_json()
        first = data['first'].strip()
        second = data['second'].strip()

        if first == second:
            return "500"

        return interpreter.link(['link', first, second])

    @app.route("/bfs_execute/", methods=["POST"])
    def bfs_execute():
        interpreter.std_capture = StringIO()
        with redirect_stdout(interpreter.std_capture):
            interpreter.execute(["execute"])
        return "200"

    @app.route("/shutdown/", methods=["POST"])
    def shutdown():
        exit(0)

    @app.route("/get_satx_text/", methods=["POST"])
    def get_satx_text():
        data = request.get_json()
        names = data['names']
        lefts = data['lefts']
        tops = data['tops']

        satx_text = interpreter.graph.get_satx_as_txt()
        satx_text += "\n<!--SATYRN_POSITIONING_START-->"

        for i, _ in enumerate(names):
            if len(names[i]) > 0:
                satx_text += "\n" + names[i] + lefts[i] + " " + tops[i]

        satx_text += "\n<!--SATYRN_POSITIONING_END-->"

        return satx_text

    @app.route("/reset_runtime/", methods=["POST"])
    def reset_runtime():
        interpreter.reset_runtime()
        return "200"

    @app.route("/dupe_cell/", methods=["POST"])
    def dupe_cell():
        data = request.get_json()
        cell_name = data['cell_name'].strip()

        og_cell = interpreter.graph.get_cell(cell_name)

        interpreter.create_cell(['cell', og_cell.name + "-copy", og_cell.content_type, "n"])
        interpreter.graph.get_cell(og_cell.name + "-copy").content = og_cell.content
        interpreter.graph.get_cell(og_cell.name + "-copy").stdout = og_cell.stdout

        return {'cell_name': og_cell.name + "-copy",
                'content': og_cell.content,
                'content_type': og_cell.content_type}

    @app.route("/graph_has_name/", methods=["POST"])
    def check_for_graph_has_name():
        cell_name = request.get_json().strip()

        if cell_name in interpreter.graph.get_all_cells_edges()[0]:
            return "200"
        return "500"

    @app.route("/dynamic_cell_output/", methods=["GET"])
    def get_dynamic_cell_output():
        if interpreter.graph.executing:
            a = interpreter.std_capture.getvalue()
            return a
        return "<!--SATYRN_DONE_EXECUTING-->" + interpreter.std_capture.getvalue()

    @app.route("/load_graph/", methods=["POST"])
    def load_graph():
        if request.get_json()['load_from_file']:
            interpreter.reset_graph(False)
            raw = request.get_json()['file_contents']
            content = raw.split("\n")
            interpreter.filename = request.get_json()['filename']
            interpreter.run_string(content)

        cell_names = interpreter.graph.get_all_cells_edges()[0]
        links = interpreter.graph.get_all_cells_edges()[1]

        names = []
        contents = []
        content_types = []
        outputs = []
        lefts = []
        tops = []

        with interpreter.lock:
            for cn in cell_names:
                cell = interpreter.graph.get_cell(cn)
                names.append(cn)
                contents.append(cell.content)
                content_types.append(cell.content_type)
                outputs.append(cell.output)
                lefts.append(cell.left)
                tops.append(cell.top)

        return {'graph_fn': interpreter.filename,
                'names': names,
                'contents': contents,
                'content_types': content_types,
                'links': links,
                'lefts': lefts,
                'tops': tops}

    @app.route("/set_as_md/", methods=["POST"])
    def set_as_md():
        cell_name = request.get_json()['cell_name']
        with interpreter.lock:
            interpreter.graph.get_cell(cell_name).content_type = "markdown"

        return "200"

    @app.route("/set_as_py/", methods=["POST"])
    def set_as_py():
        cell_name = request.get_json()['cell_name']
        with interpreter.lock:
            interpreter.graph.get_cell(cell_name).content_type = "python"

        return "200"

    @app.route("/reset_graph/", methods=["POST"])
    def reset_graph():
        interpreter.reset_graph(False)
        interpreter.filename = "Untitled.SATX"
        interpreter.create_cell(["create_cell", "root", "python", "n"])
        return "200"

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

        return "200"

    @app.route("/clear_output/", methods=["POST"])
    def clear_dco():
        interpreter.std_capture = StringIO()

        return "200"

    @app.route("/get_py_text/", methods=["POST"])
    def get_py_text():
        py_txt = interpreter.graph.get_py_file()
        return py_txt

    @app.route("/set_filename/", methods=["POST"])
    def set_fn():
        print("bruh?")
        interpreter.filename = request.get_json()['filename']

    @app.route("/get_filename/", methods=["GET"])
    def get_fn():
        return interpreter.filename

    @app.route("/update_position/", methods=["POST"])
    def update_position():
        data = request.get_json()
        name = data['cell_name'].strip()
        top = data['top']
        left = data['left']

        with interpreter.lock:
            cell = interpreter.graph.get_cell(name)
            if not cell:
                return "201"
            cell.top = top
            cell.left = left

        return "200"

    @app.route("/get_layer/", methods=["POST"])
    def get_layer():
        cell_name = request.get_json()['cell_name']

        out = interpreter.get_layer(cell_name)

        return str(out) if out > 0 else " "

    return app
