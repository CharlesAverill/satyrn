# Contributing Standards

## What should I work on?
We have lots of issues that need work! All issues marked with 
[help wanted](https://github.com/CharlesAverill/satyrn/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) are open for anyone to work on.
Other issues are available as well, but please contact me before you start work on them, these are issues that I want a certain solution for, or I'd
like to integrate myself.
### JupyterCon Attendees
Issues with the [jupytercon](https://github.com/CharlesAverill/satyrn/issues?q=is%3Aissue+is%3Aopen+label%3Ajupytercon) label are typically simpler than
the other `help wanted` issues.

## What do I need to know to help?
Satyrn is written in 3 languages: Python, JavaScript, and HTML/CSS. 
### Frontend
Requires JavaScript experience. HTML and Ajax required for some problems.
### Backend
Requires Python, Flask experience. Knowledge of directed graphs and graph traversal are required for some issues.

## What files do I need to work with?
- [interpreter.py](https://github.com/CharlesAverill/satyrn/blob/master/satyrn_python/interpreter.py) - This contains all graph/cell logic. The CLI is native
to this file, although the frontend does not directly interact with it.
- [app.py](https://github.com/CharlesAverill/satyrn/blob/master/satyrn_python/app.py) - This contains all of the Flask method definitions. This file receives
Ajax requests from the frontend and calls methods from `interpreter.py` to make changes and retrieve data from the graph.
- [entry_point.py](https://github.com/CharlesAverill/satyrn/blob/master/satyrn_python/entry_point.py) - This is what handles startup. Whenever a user starts
the CLI or UI, this file will parse the provided arguments and start up the CLI or UI.
- [satyrn_backend.js](https://github.com/CharlesAverill/satyrn/blob/master/satyrn_python/static/js/satyrn_backend.js) - This handles all frontend logic. It's
very dense right now, and needs to be split into multiple files, but for the time being it is all of the JavaScript in this project.
- [languages.json](https://github.com/CharlesAverill/satyrn/blob/master/satyrn_python/static/js/languages.json) - This file contains all of the translation
text. To add a new language, copy and paste the template, and fill the original with the new language text. 
- [index.html, canvas.html](https://github.com/CharlesAverill/satyrn/tree/master/satyrn_python/templates) - These are the HTML pages for the UI. The canvas
is the area of the UI where cells are moved and edited, and it is rendered inside of an `<iframe>` inside of the index page. 
