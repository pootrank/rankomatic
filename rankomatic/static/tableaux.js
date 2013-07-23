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

// slight extension for jQuery
$.fn.exists = function() {
    return this.length !== 0;
}

/*
* Function: outer_html
* ====================
* Takes a jQuery object and returns the entire html of the element it
* represents, including the tags that make up the element itself.
*/
function outer_html($elem) {
    // the call to .wrapAll() allows the outer html to be accessed
    var ret = $elem.wrapAll("<div></div>").parent().html();
    $elem.unwrap();
    return ret
}


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
            candidate_ind = $(this).parent().index();
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
    if ($('#tableaux th:last-child').index() > MIN_TABLEAUX_IND) {
        $('#tableaux th:nth-last-child(2),' +
          ' #tableaux td:nth-last-child(2)').remove();
    }
}




/*
* Add the click handlers when the DOM is ready.
*/
$(document).ready(function() {
    $('#add_input_group').click(add_input_group);
    $('#delete_input_group').click(delete_input_group);
    $('#add_constraint').click(add_constraint_column);
    $('#delete_constraint').click(delete_constraint_column);
    $('.add_output_row').click(add_output_row);
    $('.delete_output_row').click(delete_output_row);
});
