var filename = "Untitled.SATX";
var num_cells = 1;
var is_executing = false;
var just_finished = false;

setup_keyboard_shortcuts(document);

var last_deleted_cell = {'name': '',
                         'content': '',
                         'content_type': ''
};

$(window).load(function () {
    $.ajax({
        type : "POST",
        url : "/load_graph/",
        dataType: "json",
        data: JSON.stringify({'file_contents': '',
            'load_from_file': false}),
        contentType: "application/json",
        success: function (data) {
            var names = data['names'];
            var contents = data['contents'];
            var content_types = data['content_types'];
            var links = data['links'];
            var tops = data['tops'];
            var lefts = data['lefts'];
            var graph_fn = data['graph_fn']

            if(names.length != contents.length){
                alert("Loading error: names and contents are not congruent")
            }
            else{
                if(names.length == 0){
                    return;
                }
                removeDraggables();
                for(var i = 0; i < names.length; i++){
                    create_cell($("iframe").contents(), names[i], contents[i], content_types[i], tops[i], lefts[i]);
                }

                $.ajax({
                    type : "GET",
                    url : "/dynamic_cell_output/",
                    success: function (data) {
                        if(data.includes("<!--SATYRN_DONE_EXECUTING-->")){
                            is_executing = false;
                            just_finished = true;
                            data = data.substring(28);
                        }
                        updateDCO(data);
                    }
                });

                $("#graph_name_p").text(graph_fn);
                filename = graph_fn;

                if(!window.location.hash) {
                    window.location = window.location + '#loaded';
                    window.location.reload();
                }
            }
        }
    });

    $.ajax({
        type : "GET",
        url : "/get_filename/",
        success: function (data) {
            graph_fn = data['responseText'];
            $("#graph_name_p").text(graph_fn);
            filename = graph_fn;
        }
    });
});

$("#file-input").change(function(e){
    filename = e.target.files[0].name;

    var file_contents = "";

    var reader = new FileReader();

    reader.readAsText(e.target.files[0], "UTF-8");
    reader.onload = function(evt){
        file_contents = evt.target.result;
        $("#graph_name_p").text(filename);

        $.ajax({
            type : "POST",
            url : "/load_graph/",
            dataType: "json",
            data: JSON.stringify({'file_contents': file_contents,
                                    'load_from_file': true,
                                    'filename': filename}),
            contentType: "application/json",
            success: function (data) {
                var names = data['names'];
                var contents = data['contents'];
                var content_types = data['content_types'];
                var links = data['links'];
                var graph_fn = data['graph_fn']

                if(names.length != contents.length){
                    alert("Loading error: names and contents are not congruent")
                }
                else{
                    removeDraggables();
                    for(var i = 0; i < names.length; i++){
                        create_cell($("iframe").contents(), names[i], contents[i], content_types[i]);
                    }

                    $("#file-input").val(null);

                    $.ajax({
                        type : "GET",
                        url : "/dynamic_cell_output/",
                        success: function (data) {
                            if(data.includes("<!--SATYRN_DONE_EXECUTING-->")){
                                data = data.substring(28);
                            }
                            if(data.includes("<execution complete>")){
                                data = data.substring(0, data.lastIndexOf("<execution complete>"));
                            }
                            updateDCO(data);
                        }
                    });

                    $("#graph_name_p").text(graph_fn);
                    filename = graph_fn;

                    if(!window.location.hash){
                        window.location = window.location + '#loaded';
                    }
                    window.location.reload();
                }
            }
        });
    }
    reader.onerror = function(evt){
        alert("There was an issue reading " + filename);
    }
})

$("#graph_name_p").on("click", function(){
    var new_name = prompt("New Graph name: ");
    if(new_name === null){
        return;
    }
    if(new_name.length > 0){
        filename = new_name + ".SATX";
        $(this).text(new_name + ".SATX");

        $.ajax({
            type : "GET",
            url : '/set_filename/',
            data : json.stringify({'filename': filename}),
            dataType: "text"
        });
    }
    else{
        alert("Please choose a longer Graph name");
    }
});

$("iframe").load(function(){
    var doc = $(this).contents();

    setup_keyboard_shortcuts(doc);

    $("#draggable").draggable({
        start: function(){
            console.log("start\n" + clicked_textarea);
        },
        stop: function() {
            console.log("stop\n" + clicked_textarea);
        }
    });

    $(doc).delegate('textarea', 'keydown', function(e) {
        var keyCode = e.keyCode || e.which;

        if (keyCode == 9) {
            e.preventDefault();
            var start = this.selectionStart;
            var end = this.selectionEnd;

            // set textarea value to: text before caret + tab + text after caret
            $(this).val($(this).val().substring(0, start)
                + "\t"
                + $(this).val().substring(end));

            // put caret at right position again
            this.selectionStart =
                this.selectionEnd = start + 1;
        }
    });

    //panzoom scene
    /*
    var pz_element;
    document.querySelectorAll('iframe').forEach( item =>
        pz_element = item.contentWindow.document.body.querySelectorAll('#a')
    )


    panzoom(pz_element, {
        beforeMouseDown: function (e) {
            var shouldIgnore = !e.altKey;
            return shouldIgnore;
        }
    });
     */

    //Make initial panel draggable
    $(function () {
        doc.find("#draggable").draggable({ snap: "#draggable", grid: [ 30, 30 ] });
    });

    //context menu
    // Trigger action when the contexmenu is about to be shown
    doc.on("contextmenu", "#draggable",function (event) {
        // Avoid the real one
        event.preventDefault();

        if(attempting_to_link){
            attempting_to_link = false;
            $("textarea").removeAttr("disabled");
        }

        var cl = $(this).attr("class");

        right_clicked_cell = cl.substring(0, cl.indexOf("ui-draggable") - 1);
        console.log(right_clicked_cell);
        console.log(cl);

        // Show contextmenu
        doc.find(".custom-menu").finish().toggle(100).

            // In the right position (the mouse)

            css({
                top: event.pageY + "px",
                left: event.pageX + "px"
            });

        pageX = event.pageX;
        pageY = event.pageY;
    });

    // If the menu element is clicked
    doc.on("click", ".custom-menu li", function(){
        // This is the triggered action name
        switch ($(this).attr("data-action")) {

            // A case for each action. Your actions here

            case "new_cell":
                $.ajax({
                    type : "GET",
                    url : '/create_cell/',
                    dataType: "text",
                    success: function (data) {
                        create_cell(doc, data, "", "python");
                    }
                });
                break;
            case "destroy_cell":
                $.ajax({
                    type : "POST",
                    url : '/destroy_cell/',
                    dataType: "json",
                    data: JSON.stringify(right_clicked_cell),
                    contentType: "application/json",
                    complete: function (o) {
                        var output = o.responseJSON;

                        var success = output['success']
                        if(success == "false"){
                            alert("Couldn't remove cell " + right_clicked_cell);
                        }
                        else{
                            last_deleted_cell['name'] = output['name'];
                            last_deleted_cell['content'] = output['content'];
                            last_deleted_cell['content_type'] = output['content_type'];
                            doc.find("div").remove("." + right_clicked_cell);
                        }
                    }
                });
                break;
            case "bfs_execute":
                $.ajax({
                    type : "POST",
                    url : '/root_has_outputs/',
                    complete: function (s) {
                        if(s['responseText'] == "warning" && num_cells > 1){
                            if(confirm("The root node has no outward links. Code execution starts at root, so this may result in unintended consequences. Continue?")){
                                bfs_execute();
                            }
                        }
                        else{
                            bfs_execute();
                        }
                    }
                });
                break;
            case "link_cell":
                attempting_to_link = true;
                doc.find("textarea").attr("disabled","disabled");
                break;
            case "dupe_cell":
                $.ajax({
                    type : "POST",
                    url : '/dupe_cell/',
                    dataType: "json",
                    data: JSON.stringify({'cell_name': right_clicked_cell,
                        'content': '',
                        'content_type': ''}),
                    contentType: "application/json",
                    success: function (data) {
                        create_cell(doc, data['cell_name'], data['content'], data['content_type']);
                    }
                });
                break;
            case "child_cell":
                $.ajax({
                    type : "POST",
                    url : '/child_cell/',
                    dataType: "json",
                    data: JSON.stringify({'parent_name': right_clicked_cell}),
                    contentType: "application/json",
                    complete: function(data){
                        create_cell(doc, data['responseText'], "", "python");
                    }
                });
                break;
            case "individual_execute":
                $.ajax({
                    type : "POST",
                    url : '/individual_execute/',
                    dataType: "json",
                    data: JSON.stringify({'cell_name': right_clicked_cell}),
                    contentType: "application/json",
                    complete: function(){
                        is_executing = true;
                        just_finished = false;
                    }
                });
                break;
        }

        // Hide it AFTER the action was triggered
        doc.find(".custom-menu").hide(100);
    })

    // If the document is clicked somewhere
    doc.bind("mousedown", function (e) {

        // If the clicked element is not the menu
        if (!doc.find(e.target).parents(".custom-menu").length > 0) {

            // Hide it
            doc.find(".custom-menu").hide(100);

            clicked_textarea = "";
        }
    });

    //when a textarea is clicked
    doc.on("click", "textarea", (function(){
        started_ta_edit = true;
        clicked_textarea = $(this).attr("id").substring(9);
    }));

    //linking logic
    doc.on("click", "#draggable", (function(event){
        clicked_textarea = $(this).attr("class").substring(0, $(this).attr("class").indexOf("ui-draggable") - 1);

        pageX = event.pageX;
        pageY = event.pageY;

        if(attempting_to_link){
            attempting_to_link = false;
            doc.find("textarea").removeAttr("disabled");

            var continue_with_link = true;

            if(clicked_textarea == right_clicked_cell){
                return;
            }

            $.ajax({
                type : "POST",
                url : '/recursion_check/',
                dataType: "json",
                data: JSON.stringify({'cell_name': clicked_textarea}),
                contentType: "application/json",
                complete: function (s) {
                    if(s['responseText'] == "warning"){
                        if(!confirm("Linking to a cell with output links can cause undesired recursion. Are you sure?")){
                            continue_with_link = false;
                        }
                    }
                }
            });
            if(continue_with_link) {
                $.ajax({
                    type : "POST",
                    url : '/link_cells/',
                    dataType: "json",
                    data: JSON.stringify({'first': right_clicked_cell,
                        'second': clicked_textarea}),
                    contentType: "application/json",
                    success: function (success) {
                        if(success == "false"){
                            alert("Couldn't link cells " + right_clicked_cell + " and " + clicked_textarea);
                        }
                    }
                });
            }
        }
    }));

    doc.bind("mousedown", function (e) {
        // If the clicked element is not the menu
        if (!attempting_to_link && started_ta_edit && currentVal != null && !$(e.target).parents(".transparent_text").length > 0 && !$(e.target).parents(".draggable").length > 0) {
            // Hide it

            started_ta_edit = false;
        }
    });

    doc.on("click", "h6", function(){
        var old_name = $(this).text();
        var new_name = prompt("Rename cell: ");
        if(new_name == null){
            return;
        }
        if(new_name.length < 1){
            alert("Please use a longer cell name");
            return;
        }
        has_changed = true;

        var h6 = $(this);

        $.ajax({
            type : "POST",
            url : '/graph_has_name/',
            dataType: "json",
            data: JSON.stringify(new_name),
            contentType: "application/json",
            success: function (success) {
                if(success == "true"){
                    alert("Another cell already has this name. Please choose another.");
                }
                else{
                    $.ajax({
                        type : "POST",
                        url : '/rename_cell/',
                        dataType: "json",
                        data: JSON.stringify({'old_name': old_name,
                            'new_name': new_name}),
                        contentType: "application/json",
                        success: function (success) {
                            if(!success){
                                alert("Couldn't rename cell \"" + old_name + "\" to \"" + new_name + "\", another cell already has this name");
                            }
                            else{
                                h6.html(new_name);
                                doc.find("." + old_name).attr('class', new_name + " " + doc.find("." + old_name).attr('class').replace(old_name, ""));
                                doc.find("#textarea_" + old_name).attr("id", "textarea_" + new_name);
                            }
                        }
                    });
                    clicked_textarea = new_name;
                }
            }
        });
    })
});

$(document).on("click", ".shutdown", function(){
    shutdown();
})

//Navbar stuff
$(document).on("click", "a, li", function(){
    var attr = "";
    var child = $(this).children()[0];
    if(child === 'undefined'){
        attr = $(this).attr("action");
    }
    else{
        attr = $(child).attr("action");
    }

    switch(attr){
        case "shutdown":
            shutdown();
            break;
        case "run_all":
            $.ajax({
                type : "POST",
                url : '/root_has_outputs/',
                complete: function (s) {
                    if(s['responseText'] == "warning" && num_cells > 1){
                        if(confirm("The root node has no outward links. Code execution starts at root, so this may result in unintended consequences. Continue?")){
                            bfs_execute();
                        }
                    }
                    else{
                        bfs_execute();
                    }
                }
            });
            break;
        case "save_graph_as":
            var dict = {'names': [], 'tops': [], 'lefts': []};
            var doc = $("iframe").contents();

            $(doc).find(".ui-draggable").each( function(){
                var cell_name = $(this).attr("class").substring(0, $(this).attr("class").indexOf("ui-draggable"));
                var top = $(this).css("top");
                var left = $(this).css("left");
                dict['names'].push(cell_name);
                dict['tops'].push(top);
                dict['lefts'].push(left);
            });

            var satx_text = "";
            $.ajax({
                type : "POST",
                url : '/get_satx_text/',
                dataType: "json",
                data: JSON.stringify(dict),
                contentType: "application/json",
                complete: function (s) {
                    filename = $("#graph_name_p").text()

                    satx_text = s['responseText'];

                    var dwnld_ele = document.createElement('a');
                    dwnld_ele.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURI(satx_text));
                    dwnld_ele.setAttribute('download', filename);

                    dwnld_ele.style.display = 'none';
                    document.body.appendChild(dwnld_ele);
                    dwnld_ele.click();
                    document.body.removeChild(dwnld_ele);
                }
            });
            break;
        case "reset_runtime":
            if(confirm("Resetting the runtime will destroy all variables. Are you sure?")){
                $.ajax({
                    type : "POST",
                    url : '/reset_runtime/',
                    complete: function (s) {
                        alert("Runtime has been reset")
                    }
                });
            }
            break;
        case "dupe_cell":
            if(clicked_textarea != ""){
                $.ajax({
                    type : "POST",
                    url : '/dupe_cell/',
                    dataType: "json",
                    data: JSON.stringify({'cell_name': clicked_textarea,
                        'content': '',
                        'content_type': ''}),
                    contentType: "application/json",
                    success: function (data) {
                        create_cell($("iframe").contents(), data['cell_name'], data['content'], data['content_type']);
                    }
                });
            }
            break;
        case "load_graph":
            $('#file-input').trigger('click');
            break;
        case "set_as_md":
            if(clicked_textarea != ""){
                $.ajax({
                    type : "POST",
                    url : '/set_as_md/',
                    dataType: "json",
                    data: JSON.stringify({'cell_name': clicked_textarea}),
                    contentType: "application/json",
                    success: function (data) {
                        var ele = $("iframe").contents().find("#textarea_" + clicked_textarea);
                        ele.removeClass().addClass("highlightGreen");

                        for(var i = 0; i < codemirrors.length; i++){
                            var dict = codemirrors[i];
                            var n = dict['name'];
                            if(n != clicked_textarea){
                                continue;
                            }
                            var cm = dict['codemirror'];
                            cm.setOption("mode", "markdown");
                        }

                        console.log(codemirrors);
                    }
                });
            }
            break;
        case "set_as_py":
            if(clicked_textarea != ""){
                $.ajax({
                    type : "POST",
                    url : '/set_as_py/',
                    dataType: "json",
                    data: JSON.stringify({'cell_name': clicked_textarea}),
                    contentType: "application/json",
                    success: function (data) {
                        var ele = $("iframe").contents().find("#textarea_" + clicked_textarea);
                        ele.removeClass().addClass("highlightBlue");

                        for(var i = 0; i < codemirrors.length; i++){
                            var dict = codemirrors[i];
                            var n = dict['name'];
                            if(n != clicked_textarea){
                                continue;
                            }
                            var cm = dict['codemirror'];
                            cm.setOption("mode", "python");
                        }
                    }
                });
            }
            break;
        case "reset_graph":
            if(confirm("Resetting the graph will destroy all cells and variables. Are you sure?")){
                $.ajax({
                    type : "POST",
                    url : '/reset_graph/',
                    complete: function (s) {
                        alert("Graph has been reset. Tab will now reload.");
                        location.reload();
                    }
                });
            }
            break;
        case "reset_run_all":
            if(confirm("Resetting the runtime will destroy all variables. Are you sure?")){
                $.ajax({
                    type : "POST",
                    url : '/reset_runtime/',
                    complete: function (s) {
                        $.ajax({
                            type : "POST",
                            url : '/root_has_outputs/',
                            complete: function (s) {
                                if(s['responseText'] == "warning" && num_cells > 1){
                                    if(confirm("The root node has no outward links. Code execution starts at root, so this may result in unintended consequences. Continue?")){
                                        bfs_execute();
                                    }
                                }
                                else{
                                    bfs_execute();
                                }
                            }
                        });
                    }
                });
            }
            break;
        case "clear_dco":
            $.ajax({
                type : "POST",
                url : '/clear_output/',
                complete: function () {
                    updateDCO("");
                }
            });
            break;
        case "run_cell":
            if(clicked_textarea === ""){
                return;
            }
            $.ajax({
                type : "POST",
                url : '/individual_execute/',
                dataType: "json",
                data: JSON.stringify({'cell_name': clicked_textarea}),
                contentType: "application/json",
                complete: function(){
                    is_executing = true;
                    just_finished = false;
                }
            });
            break;
        case "create_cell":
            $.ajax({
                type : "GET",
                url : '/create_cell/',
                dataType: "text",
                success: function (data) {
                    create_cell($("iframe").contents(), data, "", "python");
                }
            });
            break;
        case "save_as_py":
            var satx_text = "";
            $.ajax({
                type : "POST",
                url : '/get_py_text/',
                dataType: "json",
                data: JSON.stringify({'text': ""}),
                contentType: "application/json",
                complete: function (s) {
                    satx_text = s['responseText'];

                    var dwnld_ele = document.createElement('a');
                    dwnld_ele.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURI(satx_text));
                    dwnld_ele.setAttribute('download', filename.substring(0, filename.length - 4) + "py");

                    dwnld_ele.style.display = 'none';
                    document.body.appendChild(dwnld_ele);
                    dwnld_ele.click();
                    document.body.removeChild(dwnld_ele);
                }
            });
            break;
    }
})

//store class of last right-clicked cell
var right_clicked_cell;

var pageX;
var pageY;

//store class of left-clicked textarea
var clicked_textarea = "";
//bool for if renaming cell or not
var renaming = false;
//store cell's current contents/name
var currentVal = null;
//I forget the difference between this and clicked_textarea but it works so don't mess with it
var ta_class = "";
//bool for if user has started to edit textarea
var started_ta_edit = false;
//bool for if user is linking one cell to another
var attempting_to_link = false;

function bfs_execute(){
    is_executing = true;
    just_finished = false;
    $.ajax({
        type : "POST",
        url : '/bfs_execute/',
        success: function (success) {
            if(success == "false"){
                alert("There was an error with the execution");
            }
        }
    });
}

var codemirrors = [];

function create_cell(doc, name, content="", contentType, top=(Math.ceil(pageY / 30 )*30)+10, left=(Math.ceil(pageX / 30 )*30)+10){
    if(num_cells == 0){
        pageX = 0;
        pageY = 0;
    }

    var colorClass = contentType == "python" ? "Blue" : "Green";

    doc.find("#scene").append('<div id="draggable" class="'.concat(name, '">' +
        '<div style="display: inline-block; margin-right: 10px;">' +
            '<h6 class="label" id="running_' + name + '" style="width: auto">[ ]</h6>' +
        '</div>' +
        '<div style="display: inline-block;">' +
            '<h6 class="label">' + name + '</h6>' +
        '</div>' +
        '<div class="draggable" style="border-radius: 5px;">' +
            '<div id="textarea_' + name + '" class="highlight' + colorClass + '" style="border-radius: 5px;"></div>' +
        '</div></div>'))

    doc.find(".".concat(name)).css("top", top );
    doc.find(".".concat(name)).css("left", left );

    //Grid system
    doc.find(".".concat(name)).draggable({ snap: ".".concat(name), grid: [ 30, 30 ] });

    //Codemirror
    var cm = add_codemirror_editor(document.getElementById("canvas").contentWindow.document,"#textarea_" +  name, content, contentType);
    $('.CodeMirror').resizable({
        resize: function() {
            cm.setSize($(this).width(), $(this).height());
        }
    });
    doc.find(".CodeMirror").css("margin-top", "11px");

    var dict = {'name': name, codemirror: cm};

    codemirrors.push(dict);

    num_cells += 1;
}

function shutdown(){
    if(confirm("This will close the connection. Are you sure?")){
        $.ajax({
            type : "POST",
            url : '/shutdown/',
            complete: function (s) {
                alert("Connection has been closed");
                $("#connected_p").text("Disconnected");
            }
        });
    }
}

function removeDraggables(){
    for(var i = 0; i < num_cells; i++){
        $("iframe").contents().find("#draggable").remove();
    }
    num_cells = 0;
}

function updateDCO(appended_string){
    var textarea = $("#dynamic_code_output")
    textarea.val(appended_string);
    if(textarea.length)
       textarea.scrollTop(textarea[0].scrollHeight - textarea.height());
}

const throttle = (callback, delay) => {
    let throttleTimeout = null;
    let storedEvent = null;

    const throttledEventHandler = event => {
        storedEvent = event;

        const shouldHandleEvent = !throttleTimeout;

        if (shouldHandleEvent) {
            callback(storedEvent);

            storedEvent = null;

            throttleTimeout = setTimeout(() => {
                throttleTimeout = null;

                if (storedEvent) {
                    throttledEventHandler(storedEvent);
                }
            }, delay);
        }
    };

    return throttledEventHandler;
};

const debounce = (func, wait) => {
    let timeout;

    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };

        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

var throttle_func = throttle(function() {
    if(is_executing){
        $.ajax({
            type : "GET",
            url : "/dynamic_cell_output/",
            success: function (data) {
                if(data.includes("<!--SATYRN_DONE_EXECUTING-->")){
                    is_executing = false;
                    just_finished = true;
                    data = data.substring(28);
                }
                updateDCO(data);
            }
        });
    }
    else if(just_finished){
        $.ajax({
            type : "GET",
            url : "/dynamic_cell_output/",
            success: function (data) {
                if(data.includes("<!--SATYRN_DONE_EXECUTING-->")){
                    data = data.substring(28);
                }
                updateDCO(data);
            }
        });
        just_finished = false;
        is_executing = false;
    }
}, 2000);

var debounce_func = debounce(function(){
    if(is_executing){
        $.ajax({
            type : "GET",
            url : "/dynamic_cell_output/",
            success: function (data) {
                if(data.includes("<!--SATYRN_DONE_EXECUTING-->")){
                    is_executing = false;
                    just_finished = true;
                    data = data.substring(28);
                }
                updateDCO(data);
            }
        });
    }
    else if(just_finished){
        $.ajax({
            type : "GET",
            url : "/dynamic_cell_output/",
            success: function (data) {
                if(data.includes("<!--SATYRN_DONE_EXECUTING-->")){
                    data = data.substring(28);
                }
                updateDCO(data);
            }
        });
        just_finished = false;
        is_executing = false;
    }
}, 100);

window.setInterval(function(){
    debounce_func();
}, 200);

function add_codemirror_editor(doc, ta_id, value='\n\n', contentType){
    var cm = CodeMirror(doc.querySelector(ta_id), {
        lineNumbers: true,
        tabSize: 4,
        indentUnit: 4,
        value: value,
        mode: contentType,
        theme: 'rubyblue'
    });
    cm.on("change", function(){
        currentVal = cm.getValue();
        $.ajax({
            type : "POST",
            url : '/edit_cell/',
            dataType: "json",
            data: JSON.stringify({'name': clicked_textarea,
                'content': currentVal}),
            contentType: "application/json",
            success: function (success) {
                if(success == "false"){
                    alert("Couldn't edit cell " + right_clicked_cell);
                }
            },
            statusCode: {
                500: function() {
                    if(confirm("It seems there was a disconnect. Do you want to reconnect?")){
                        location.reload();
                    }
                }
            }
        });

        started_ta_edit = false;
    });

    return cm;
}

function setup_keyboard_shortcuts(doc){
    $(doc).bind('keyup', 'Ctrl+return', function(){
        if(clicked_textarea == ""){
            return;
        }
        $.ajax({
            type : "POST",
            url : '/individual_execute/',
            dataType: "json",
            data: JSON.stringify({'cell_name': clicked_textarea}),
            contentType: "application/json",
            complete: function(){
                is_executing = true;
                just_finished = false;
            }
        });
    });
    $(doc).bind('keyup', 'Ctrl+r', function(){
        bfs_execute();
    });
    $(doc).bind('keyup', 'Ctrl+s', function(){
        var satx_text = "";
        $.ajax({
            type : "POST",
            url : '/get_satx_text/',
            dataType: "json",
            data: JSON.stringify({'text': ""}),
            contentType: "application/json",
            complete: function (s) {
                satx_text = s['responseText'];

                var dwnld_ele = document.createElement('a');
                dwnld_ele.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURI(satx_text));
                dwnld_ele.setAttribute('download', filename);

                dwnld_ele.style.display = 'none';
                document.body.appendChild(dwnld_ele);
                dwnld_ele.click();
                document.body.removeChild(dwnld_ele);
            }
        });
    });
    $(doc).bind('keyup', 'Ctrl+c', function(){
        console.log("Interrupt");
    });
    $(doc).bind('keyup', 'Ctrl+d', function(){
        $.ajax({
            type : "POST",
            url : '/dupe_cell/',
            dataType: "json",
            data: JSON.stringify({'cell_name': clicked_textarea,
                'content': '',
                'content_type': ''}),
            contentType: "application/json",
            success: function (data) {
                create_cell(doc, data['cell_name'], data['content'], data['content_type']);
            }
        });
    });
    $(doc).bind('keyup', 'Ctrl+backspace', function(){
        if(clicked_textarea == ""){
            return;
        }
        $.ajax({
            type : "POST",
            url : '/destroy_cell/',
            dataType: "json",
            data: JSON.stringify(clicked_textarea),
            contentType: "application/json",
            complete: function (o) {
                var output = o.responseJSON;
                var success = output['success']
                console.log(output);
                if(success == "false"){
                    alert("Couldn't remove cell " + clicked_textarea);
                }
                else{
                    last_deleted_cell['name'] = output['name'];
                    last_deleted_cell['content'] = output['content'];
                    last_deleted_cell['content_type'] = output['content_type'];
                    doc.find("div").remove("." + clicked_textarea);
                }
            }
        });
    });
}