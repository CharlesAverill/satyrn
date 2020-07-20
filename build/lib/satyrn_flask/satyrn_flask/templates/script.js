//Make initial panel draggable
$(function () {
    $("#draggable").draggable({ snap: "#draggable", grid: [ 30, 30 ] });
});

// Hide navbar items when clicked
$(document).on("click", "a", function(){
    var cl = $(this).attr("class");
    if(typeof cl == 'undefined'){
        $(".button-dropdown .dropdown-menu").hide();
    }
})

//panzoom scene
var element = document.querySelector('#scene');

/*
panzoom(element, {
    beforeMouseDown: function (e) {
        var shouldIgnore = !e.altKey;
        return shouldIgnore;
    }
});
*/

//Navbar stuff
$(document).on("click", "a", function(){
    var attr = $(this).attr("action");
    switch(attr){
        case "shutdown":
            if(confirm("This will close the connection. Are you sure?")){
                $.ajax({
                    type : "POST",
                    url : '/shutdown/',
                    complete: function (s) {
                        alert("Connection has been closed");
                    }
                });
            }
            break;
        case "run_all":
            $.ajax({
                type : "POST",
                url : '/root_has_outputs/',
                complete: function (s) {
                    if(s['responseText'] == "warning"){
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
            var satx_text = "";
            $.ajax({
                type : "POST",
                url : '/get_satx_text/',
                dataType: "json",
                data: JSON.stringify({'text': ""}),
                contentType: "application/json",
                complete: function (s) {
                    satx_text = s['responseText'];
                    console.log(satx_text);

                    var dwnld_ele = document.createElement('a');
                    dwnld_ele.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURI(satx_text));
                    dwnld_ele.setAttribute('download', 'Untitled.satx');

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
                        $("#scene").append('<div id="draggable" class="'.concat(data['cell_name'], '"><h6 class="label">' + data['cell_name'] + '</h6><div class="draggable"><div class="highlightBlue"></div><textarea class="textarea_' + data['content'] + '" spellcheck="false"></textarea></div></div>'))

                        $(".".concat(data['cell_name'])).css("top", (Math.ceil(pageY / 30 )*30)-4 );
                        $(".".concat(data['cell_name'])).css("left", (Math.ceil(pageX / 30 )*30)-4 );

                        //Grid system
                        $(".".concat(data['cell_name'])).draggable({ snap: ".".concat(data['cell_name']), grid: [ 30, 30 ] });
                    }
                });
            }
            break;
    }
})

//store class of last right-clicked cell
var right_clicked_cell;

var pageX;
var pageY;

//context menu
// Trigger action when the contexmenu is about to be shown
$("#scene").on("contextmenu", "#draggable",function (event) {
    // Avoid the real one

    if(attempting_to_link){
        attempting_to_link = false;
        $("textarea").removeAttr("disabled");
    }

    event.preventDefault();

    var $this = $(this);
    var cl = $this.attr("class")

    right_clicked_cell = cl.substring(0, cl.indexOf("ui-draggable") - 1);

    // Show contextmenu
    $(".custom-menu").finish().toggle(100).

    // In the right position (the mouse)

    css({
        top: event.pageY + "px",
        left: event.pageX + "px"
    });

    pageX = event.pageX;
    pageY = event.pageY;
});

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

//when a textarea is clicked
$(document).on("click", "textarea", (function(){
    started_ta_edit = true;
    clicked_textarea = $(this).attr("class").substring(9);
}));

//linking logic
$(document).on("click", "#draggable", (function(event){
    clicked_textarea = $(this).attr("class").substring(0, $(this).attr("class").indexOf("ui-draggable") - 1);

    pageX = event.pageX;
    pageY = event.pageY;

    if(attempting_to_link){
        attempting_to_link = false;
        $("textarea").removeAttr("disabled");

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
                console.log(s['responseText']);
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

$(document).bind("mousedown", function (e) {
    // If the clicked element is not the menu
    if (!attempting_to_link && started_ta_edit && currentVal != null && !$(e.target).parents(".transparent_text").length > 0 && !$(e.target).parents(".draggable").length > 0) {
        // Hide it

        started_ta_edit = false;
    }
});

$(document).on("click", "h6", function(){
    var old_name = $(this).text();
    console.log(old_name);
    var new_name = prompt("Rename cell: ");
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
                        if(success == "false"){
                            alert("Couldn't rename cell " + right_clicked_cell);
                        }
                        else{
                            h6.html(new_name);
                            $("." + old_name).attr('class', new_name + " " + $("." + old_name).attr('class').replace(old_name, ""));
                            $(".textarea_" + old_name).addClass("textarea_" + new_name).removeClass("textarea_" + old_name);
                        }
                    }
                });
                clicked_textarea = new_name;
            }
        }
    });
})

$(document).on("input propertychange", 'textarea', function() {
    currentVal = $(this).val();
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
            else{
                var succ = true;
            }
        }
    });

    started_ta_edit = false;
});

// If the document is clicked somewhere
$(document).bind("mousedown", function (e) {

    // If the clicked element is not the menu
    if (!$(e.target).parents(".custom-menu").length > 0) {

        // Hide it
        $(".custom-menu").hide(100);
    }
});

var cells = [];

// If the menu element is clicked
$(".custom-menu li").click(function (event) {

    // This is the triggered action name
    switch ($(this).attr("data-action")) {

        // A case for each action. Your actions here

        case "new_cell":
            $.ajax({
                type : "GET",
                url : '/create_cell/',
                dataType: "text",
                success: function (data) {
                    $("#scene").append('<div id="draggable" class="'.concat(data, '"><h6 class="label">' + data + '</h6><div class="draggable"><div class="highlightBlue"></div><textarea class="textarea_' + data + '" spellcheck="false"></textarea></div></div>'))

                    $(".".concat(data)).css("top", (Math.ceil(pageY / 30 )*30)-4 );
                    $(".".concat(data)).css("left", (Math.ceil(pageX / 30 )*30)-4 );

                    //Grid system
                    $(".".concat(data)).draggable({ snap: ".".concat(data), grid: [ 30, 30 ] });
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
                success: function (success) {
                    if(success == "false"){
                        alert("Couldn't remove cell " + right_clicked_cell);
                    }
                    else{
                        $("div").remove("." + right_clicked_cell);
                    }
                }
            });
            break;
        case "bfs_execute":
            $.ajax({
                type : "POST",
                url : '/root_has_outputs/',
                complete: function (s) {
                    if(s['responseText'] == "warning"){
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
            $("textarea").attr("disabled","disabled");
            break;
    }

    // Hide it AFTER the action was triggered
    $(".custom-menu").hide(100);
});

function bfs_execute(){
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