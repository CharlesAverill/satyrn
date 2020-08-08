import multiprocessing
import os
import time
import webbrowser

from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher

from .app import create_app


def delayed_browser_open():
    time.sleep(3)

    webbrowser.open("http://localhost:20787/")


def run_frontend():
    print("Initiating CherryPy server...")

    os.environ["FLASK_APP"] = "satyrnUI.satyrnUI"
    os.environ["FLASK_ENV"] = "production"

    d = PathInfoDispatcher({'/': create_app()})
    server = WSGIServer(('0.0.0.0', 20787), d)

    try:
        p = multiprocessing.Process(target=delayed_browser_open)
        p.start()

        print("Hosting at http://localhost:20787/")

        server.start()
        webbrowser.open("http://localhost:20787/")
    except KeyboardInterrupt:
        print("Stopping CherryPy server...")
        server.stop()
        print("Stopped")


if __name__ == "__main__":
    run()
