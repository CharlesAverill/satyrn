import platform, os, webbrowser, time, multiprocessing


def run():
    try:
        import flask
    except ImportError as e:
        os.system("python3 -m pip install --upgrade flask")

    try:
        import networkx
    except ImportError as e:
        os.system("python3 -m pip install --upgrade networkx")

    try:
        import matplotlib
    except ImportError as e:
        os.system("python3 -m pip install --upgrade matplotlib")

    os.environ["FLASK_APP"] = "satyrn_flask.satyrn_flask"
    os.environ["FLASK_ENV"] = "development"

    p = multiprocessing.Process(target=os.system, args=("flask run", ))
    p.start()
    time.sleep(2)

    webbrowser.open("http://127.0.0.1:5000/")


if __name__ == "__main__":
    run()