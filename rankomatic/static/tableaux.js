/*
* File: tableaux.js
* Author: Cameron Jeffers
* Email: cwjeffers18@gmail.com
*
* This file defines an ExpandoTableaux class that takes the IDs of the table and
* of the add and delete buttons, then attaches functions to those buttons that add
* or delete constraints and input/output pairs to the table.
*/

var FIRST_CONSTRAINT_IND = 3;
var MIN_TABLEAUX_IND = 5;
var MAX_TABLEAUX_IND = 9;
var num_rows_added = 0;

// slight extension for jQuery
$.fn.exists = function() {
    return this.length !== 0;
}

/*** Helper functions ****** Helper functions ****** Helper functions ***/
/*
* Function: update_input
* ======================
* Given an input name, index, value, and a row to search in, updates the input.
* Args:
*   $row -- the jQuery row to search in
*   name -- a string with the unique suffix for the input
*   ind -- the candidate index of the row
*   val -- the value to set the input as, if null will remain the same
*/
function update_input($row, name, val) {
    var name_str = 'candidates-' + num_rows_added + '-' + name;
    var input = $row.find('input[name$="' + name + '"]');
    input.attr({id: name_str, name: name_str})
    if (val != null) {
        input.val(val);
    }
}

/*
* Function update_row_values
* ==========================
* Wrapper function for update_input, calls update_input on all the relevant
* input elements.
*
* Args:
*     candidate_ind -- the index of the candidate row
*     $row -- a jQuery object corresponding to the row to update
*     output_row -- a boolean that is true if the row is an output only row
*/
function update_row_values($row, candidate_ind) {
    update_input($row, 'csrf_token', null);
    update_input($row, 'inp',  "I" + (candidate_ind + 1));
    update_input($row, 'outp', "O" + ($('#tableaux tr.candidate').size() + 1));
    update_input($row, 'optimal', "");
    for (var i = 0; i < $row.children('td').size() - FIRST_CONSTRAINT_IND; ++i) {
        update_input($row, 'vvector-' + i, "");
    }
}

/*
* Function: outer_html
* ====================
* Takes a jQuery object and returns the entire html of the element it
* represents, including the tags that make up the element itself.
*/
function outer_html($elem) {
    // the call to .wrapAll() allows the outer html to be accessed
    var ret = $elem.wrapAll('<div>').parent().html();
    $elem.unwrap();
    return ret
}
/*****************************************************************************/

/*** Column add/delete ****** Column add/delete ****** Column add/delete ***/
/*
* Function: add_constraint_column
* ===============================
* Click handler for the #add_constraint button. Inserts a new cell in every
* row, cloning the appropriate template cell and updating the values
* accordingly.
*/
function add_constraint_column(e) {
    // check that there are less than the max number of constraints
    if (($('#tableaux th:last-child').index()) < MAX_TABLEAUX_IND) {

        // clone the first constraint cell from each row, insert it
        $('#tableaux').find('tr').each(function() {
            var html_str = outer_html($(this).find('td, th').eq(FIRST_CONSTRAINT_IND));
            $(html_str).insertBefore($(this).find('td:last-child, th:last-child'));
        });

        // update the new header constraint
        var header = $('#tableaux th:nth-last-child(2)');
        var constraint_ind = header.index() - FIRST_CONSTRAINT_IND;
        var name_str = 'constraints-' + constraint_ind;
        header.find('input').attr({id: name_str,
                                   name: name_str,
                                   value: 'C' + (constraint_ind + 1)});

        // update all the violation vectors in the table
        $('#tableaux td:nth-last-child(2)').each(function(){
            to_match = $(this).parent().find('input[name$=outp]').attr('name')
            candidate_ind = (to_match.match(/candidates-(.*)-/)[1]);
            var name_str = 'candidates-' + candidate_ind +
                           '-vvector-' + constraint_ind;
            $(this).find('input').attr({id: name_str,
                                        name: name_str,
                                        value: ''});
        });
    }
}

/*
* Function: delete_constraint_column
* ==================================
* Click handler for the #delete_constraint button. Deletes the second to last
* cell from each column, assuming there are enough columns left in the table.
*/
function delete_constraint_column(e) {
    // check that the table isn't too small
    if ($('#tableaux th:last-child').index() > MIN_TABLEAUX_IND) {
        $('#tableaux th:nth-last-child(2),' +
          ' #tableaux td:nth-last-child(2)').remove();
    }
}
/*****************************************************************************/


/****** Input group add/delete ****** Input group add/delete ******/
/*
* Function: update_output_rows
* ============================
* Change handler for the input row input-fields which update all the output
* rows to match th input row.
*/
function update_output_rows(e) {
    var input_group = $(this).closest('tbody.input-group');
    new_val = this.value;
    input_group.find('input[name$="inp"]').each(function() {
        obj = $(this);
        obj.val(new_val);
        obj.attr('value', new_val);
    });
}
/*
* Function: add_input_group
* =========================
* Event handler for adding an input group to the table. Clones the first
* candidate row, wraps it in a div, and sticks at the end of the table.
*/
function add_input_group(e) {
    var row_str = outer_html($('#tableaux tr.candidate').eq(0));
    var to_append = $(row_str).wrapAll('<tbody>').parent();
    to_append.addClass('input-group');

    var candidate_ind = $('#tableaux tbody.input-group').size(); // haven't inserted yet
    var row = to_append.find('tr.candidate:eq(0)');
    num_rows_added++;
    update_row_values(row, candidate_ind);
    to_append.insertAfter($('#tableaux tbody.input-group:last-child'));

    row.find('.add_output').click(add_output_row);
    row.find('.delete_output').click(delete_output_row);
    row.find('input[name$="inp"]').change(update_output_rows);
}

/*
* Function: delete_input_group
* ============================
* Removes the last tbody from the table, assuming there is at least one.
*/
function delete_input_group(e) {
    if ($('#tableaux tbody.input-group').size() > 1) {
        $('#tableaux tbody.input-group:last-child').remove();
    }
}
/*****************************************************************************/


/****** Output row add/delete ****** Output row add/delete ******/
/*
* Function: add_output_row
* ========================
* Click handler for the .add_output buttons. Clones an output row, inserts it
* at the end of the tbody.input-group, and sets the class appropriately.
*/
function add_output_row(e) {
    var input_group = $(this).closest('tbody.input-group');
    var input_value = input_group.find('tr.input-header input[name$="inp"]').val()
    var to_append = $(outer_html(input_group.find('tr.input-header')));
    to_append.removeClass('input-header').addClass('output-only');
    num_rows_added++;
    update_row_values(to_append, $('#tableaux tr.candidate').size());
    input_field = to_append.find('input[name$="inp"]');
    input_field.attr('value', input_value);
    input_field.val(input_value);
    input_group.append(to_append);
}

/*
* Function: delete_output_row
* ===========================
* Click handler for .delete_output buttons. Deletes the bottom-most candidate
* row in their input group.
*/
function delete_output_row(e) {
    var input_group = $(this).closest('tbody.input-group');
    if (input_group.find('tr.candidate').size() > 1) {
        input_group.find('tr.candidate:last-child').remove();
    }
}
/*****************************************************************************/


$(document).ready(function() {
    // Add the click handlers when the DOM is ready.
    $('#tableaux input[name$="inp"]').change(update_output_rows);
    $('#add_input_group').click(add_input_group);
    $('#delete_input_group').click(delete_input_group);
    $('#add_constraint').click(add_constraint_column);
    $('#delete_constraint').click(delete_constraint_column);
    $('#tableaux .add_output').click(add_output_row);
    $('#tableaux .delete_output').click(delete_output_row);
});
