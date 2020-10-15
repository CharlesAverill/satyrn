# Contributing

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
### Quick Flask/Ajax Intro
Flask and Ajax can be weird to get into, but a lot of Satyrn depends on it. Here's a quick rundown of how [Flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/) works with [Ajax](https://api.jquery.com/jquery.ajax/). In our [JavaScript backend](https://github.com/CharlesAverill/satyrn/blob/master/satyrn_python/static/js/satyrn_backend.js), there are lots of tasks that require communication between the frontend and backend. On the JavaScript side, this is accomplished by sending an **Ajax Request** to the Python backend. It's not too complicated, just follow the template below to make an Ajax request:
```JavaScript
$.ajax({
    type : "" // Either "GET" or "POST". "GET" means you're just retrieving information from the backend, usually not changing any data. "POST" means you're sending and receiving data, and probably changing data too.
    url : "/", // This should be a url that accurately describes what the request is for
    dataType: "json", // Usually leave this alone
    contentType: "application/json", // This too
    data: JSON.stringify({"some_field": data1, // This is the data you'll send to the backend in the form of a dictionary. Give each data field a name and assign its value.
                                    "another_field": data2,
                                    "etc": data3}),
    complete: function (output) { // This is a function that is run when a response is received from the backend. "output" is a response dictionary. Usually what you're receiving is a string, so to get your desired output, use `output["responseText"]`.
        // Code to run when complete
    }
});
```
And that's a quick Ajax runthrough! Now let's do Flask. Most of the Flask groundwork is already laid out, so this part is really easy. All Flask code should be contained within [app.py](https://github.com/CharlesAverill/satyrn/blob/master/satyrn_python/app.py).
```python
@app.route("/same_url_from_ajax_request/", methods=["GET, "POST"]) # Necessary header
def run_when_ajax_received(): # This method's code will be run when an Ajax request is received
    data = request.get_json() # This receives the "data" variable from the request as a dictionary.
    some = data['some_field'].strip() # Get a part of the data
    another = data['another_field'].strip() # Get another part

    return interpreter.do_something(some, another) # Usually return a string. You can call interpreter logic in these methods, and usually it's necessary.
```
And that's the Flask review! Check out their docs (linked above) if you need more info, or feel free to make an issue asking for help!

## How do I contribute?
1. Find an issue you'd like to work on from our [issues page](https://github.com/CharlesAverill/satyrn/issues)
2. Fork the repository to your local GitHub organization. This means that you will have a copy of the repository under 
**github-username/satyrn**.
3. Clone the repository to your local machine using `git clone https://github.com/github-username/satyrn.git`.
4. Create a new branch for your fix using `git checkout -b your-descriptive-branch-name`.
5. Make the appropriate changes for the issue you are trying to address or the feature that you want to add.
6. Use `git add insert-paths-of-changed-files-here` to add the file contents of the changed files to the "snapshot" git uses to manage the state of the project, also known as the index.
7. Use `git commit -m "Insert a short message of the changes made here"` to store the contents of the index with a descriptive message.
8. Push the changes to the remote repository using `git push origin branch-name-here`.
9. Submit a [pull request](https://github.com/CharlesAverill/satyrn/pulls) to the satyrn repository.
10. Title the pull request with a short description of the changes made and the issue or bug number associated with your change. For example, you can title an issue like so "Added more log outputting to resolve #4352".
11. In the description of the pull request, explain the changes that you made, any issues you think exist with the pull request you made, and any questions you have for the maintainer. It's OK if your pull request is not perfect (no pull request is), the reviewer will be able to help you fix any problems and improve it!
12. Wait for the pull request to be reviewed by a maintainer.
13. Make changes to the pull request if the reviewing maintainer recommends them.
14. Celebrate your success after your pull request is merged!

## What if I need help?
Feel free to contact me at charlesaverill20@gmail.com, or join the [dev Discord](https://discord.gg/AEZtttJ)! Commenting on issues is also a great way to
ask for help from maintainers.
