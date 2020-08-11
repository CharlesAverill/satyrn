import multiprocessing
import os
import time
import webbrowser

from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher

from .app import create_app
from .interpreter import Interpreter

interpreter = Interpreter()
client_instance = 0


def delayed_browser_open():
    time.sleep(3)

    webbrowser.open("http://localhost:20787/#loaded")


def run_frontend():
    with open(os.path.abspath(__file__)[:-16] + "/asciiart.txt") as asciiart:
        print("".join(asciiart.readlines()))

    print("Thank you for using Satyrn! For issues and updates visit https://GitHub.com/CharlesAverill/satyrn\n")

    print("Initializing CherryPy server...")

    os.environ["FLASK_APP"] = "satyrnUI.satyrnUI"
    os.environ["FLASK_ENV"] = "production"

    d = PathInfoDispatcher({'/': create_app(interpreter, client_instance)})
    server = WSGIServer(('0.0.0.0', 20787), d)

    try:
        p = multiprocessing.Process(target=delayed_browser_open)
        p.start()

        print("Hosting at http://localhost:20787/#loaded")

        server.start()
    except KeyboardInterrupt:
        print("Stopping CherryPy server...")
        server.stop()
        print("Stopped")


if __name__ == "__main__":
    run_frontend()
