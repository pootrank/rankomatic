/*
* File: tableaux.js
* Author: Cameron Jeffers
* Email: cwjeffers18@gmail.com
*
* This file defines an ExpandoTableaux class that takes the IDs of the table and
* of the add and delete buttons, then attaches functions to those buttons that add
* or delete constraints and input/output pairs to the table.
*/

var MIN_TABLEAUX_IND = 3;
var MAX_TABLEAUX_IND = 8;

/*
* Constructor for ExpandoTableaux class. Registers appropriate methods with
* add and subtract buttons whose IDs are passed in.
*/
ExpandoTableaux = function( tableaux_id,
                            add_col_btn_id,
                            del_col_btn_id,
                            add_row_btn_id,
                            del_row_btn_id )
{

    // Prepend a "#" to each of the arguments, for use with jQuery
    for (var i = 0; i < arguments.length; ++i) {
        arguments[i] = "#" + arguments[i];
    }

    /*
    * Event handler for deleting a column from the tableaux. Deletes the last
    * cell from each row.
    */
    $(del_col_btn_id).click(function(e) {
        if ($(tableaux_id + " th:last-child").index() > MIN_TABLEAUX_IND) {
            $(tableaux_id + " th:last-child, " + tableaux_id +
              " td:last-child").remove();
        }
    });


    /*
    * Event handler for adding a column to the tableaux. Adds a constraint
    * cell to each row.
    */
    $(add_col_btn_id).click(function(e) {
        // check that there are less than the max number of constraints
        if ($(tableaux_id + " th:last-child").index() < MAX_TABLEAUX_IND) {

            // clone the first constraint cell from each row
            $(tableaux_id).find('tr').each(function() {
                var to_clone = $(this).find("td, th").eq(MIN_TABLEAUX_IND);

                // the call to .wrapAll() allows the outer html to be used
                var html_str = to_clone.wrapAll("<div></div>").parent().html();
                $(this).append(html_str);
                to_clone.unwrap(); // remove the wrapper div
            });

            // update the new header constraint
            var header = $(tableaux_id + " th:last-child");
            var constraint_ind = header.index() - MIN_TABLEAUX_IND;
            var name_str = "constraints-" + constraint_ind;
            header.find("input").attr({id: name_str,
                                       name: name_str,
                                       value: "C" + (constraint_ind + 1)});

            // update all the violation vectors in the table
            $(tableaux_id + " td:last-child").each(function(){
                candidate_ind = $(this).parent().index();
                var name_str = "candidates-" + candidate_ind +
                               "-vvector-" + constraint_ind;
                $(this).find("input").attr({id: name_str,
                                            name: name_str,
                                            value: ""});
            });
        }
    });


    /*
    * Helper function which updates the various inputs in the row.
    *
    * Args:
    *   $row -- the jQuery row to search in
    *   name -- a string with the unique suffix for the input
    *   ind -- the candidate index of the row
    *   val -- the value to set the input as, if null will remain the same
    */
    function update_input($row, name, ind, val)
    {
        var name_str = 'candidates-' + ind + '-' + name;
        var input = $row.find('input[name$="' + name + '"]');
        input.attr({id: name_str, name: name_str})
        if (val != null) {
            input.attr('value', val);
        }
    }

    /*
    * Event handler for adding a row to the table. Clones the row above and
    * updates the HTML attributes as necessary.
    */
    $(add_row_btn_id).click(function(e) {
        var to_clone = $(tableaux_id + " tr.candidate:last-child");
        // wrap it in a div, move up to that div, and get the inner html
        var html_str = to_clone.wrap("<div></div>").parent().html();
        to_clone.unwrap(); // delete the dummy div
        $(tableaux_id).append(html_str);

        var candidate_ind = to_clone.index() + 1;
        var row = $(tableaux_id + " tr.candidate:last-child");

        update_input(row, 'csrf_token', candidate_ind, null);
        update_input(row, 'inp', candidate_ind, "I" + (candidate_ind + 1));
        update_input(row, 'outp', candidate_ind, "O" + (candidate_ind + 1));
        update_input(row, 'optimal', candidate_ind, "");
        for (var i = 0; i < row.children('td').size() - MIN_TABLEAUX_IND; ++i) {
            update_input(row, 'vvector-' + i, candidate_ind, "")
        }
    });


    /*
    * Event handler for deleting a row from the table. Will leave at least one.
    */
    $(del_row_btn_id).click(function(e) {
        var last_row = $(tableaux_id + ' tr.candidate:last-child');
        if (last_row.index() > 0) {
            last_row.remove();
        }
    });
}



/*
* Call the constructor when the DOM is ready. Change the arguments to reuse.
*/
$(document).ready(function() {
    ExpandoTableaux("tableaux", "add_constraint", "delete_constraint",
                    "add_candidate", "delete_candidate");
});
