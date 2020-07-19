function newName() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

//Make initial panel draggable
$(function () {
    $("#draggable").draggable({ snap: "#draggable", grid: [ 30, 30 ] });
});

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

var right_clicked_cell;

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
});

var clicked_textarea = "";
var renaming = false;
var currentVal = null;
var ta_class = "";
var started_ta_edit = false;

var attempting_to_link = false;

$(document).on("click", "textarea", (function(){
    if($(this).attr("class") == "transparent_text"){
        clicked_textarea = $(this).val();
        renaming = true;
    }
    else{
        renaming = false;
    }
    started_ta_edit = true;
}));

$(document).on("click", "#draggable", (function(){
    if(attempting_to_link){
        attempting_to_link = false;
        $("textarea").removeAttr("disabled");
        clicked_textarea = $(this).attr("class").substring(0, $(this).attr("class").indexOf("ui-draggable") - 1);

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

$(document).on("input propertychange", 'textarea', function() {
    currentVal = $(this).val();

    ta_class = $(this).attr("class").substring(9);

    if(renaming){
        has_changed = true;
        $.ajax({
            type : "POST",
            url : '/rename_cell/',
            dataType: "json",
            data: JSON.stringify({'old_name': clicked_textarea,
                'new_name': currentVal}),
            contentType: "application/json",
            success: function (success) {
                if(success == "false"){
                    alert("Couldn't rename cell " + right_clicked_cell);
                }
                else{
                    clicked_textarea = currentVal;
                }
            }
        });
    }
    else{
        $.ajax({
            type : "POST",
            url : '/edit_cell/',
            dataType: "json",
            data: JSON.stringify({'name': ta_class,
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
    }

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
                    $("#scene").append('<div id="draggable" class="'.concat(data, '"><textarea class="transparent_text" rows=1 spellcheck="false" maxlength=25\n' +
                        '            style="border: none;\n' +
                        '                    background-color: transparent;\n' +
                        '                    border-color: Transparent;\n' +
                        '                    resize: none;\n' +
                        '                    outline: none;\n' +
                        '\n' +
                        '                    color:white;">' + data + '</textarea><div class="draggable"><div class="highlightBlue"></div><textarea class="textarea_' + data + '" spellcheck="false"></textarea></div></div>'))

                    $(".".concat(data)).css("top", (Math.ceil(event.pageY / 30 )*30)-4 );
                    $(".".concat(data)).css("left", (Math.ceil(event.pageX / 30 )*30)-4 );

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