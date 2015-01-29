(function(window, document, undefined) {
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
    var MAX_NUM_CONSTRAINTS = 6;
    var MIN_NUM_CONSTRAINTS = 2;
    var MAX_POOT_CONSTRAINTS = 6
    var MAX_POOT_IND = FIRST_CONSTRAINT_IND + MAX_POOT_CONSTRAINTS
    var MIN_TABLEAUX_IND = MIN_NUM_CONSTRAINTS + FIRST_CONSTRAINT_IND;
    var MAX_TABLEAUX_IND = MAX_NUM_CONSTRAINTS + FIRST_CONSTRAINT_IND;
    var INPUT_HORIZONTAL_PADDING_MARGIN = 20;
    var num_rows_added = 0;

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
    function update_input($row, name, val, ig_ind, cand_ind) {
        var name_str = 'input_groups-' + ig_ind;
        name_str += '-candidates-' + cand_ind + '-' + name;
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
    *     $row -- a jQuery object corresponding to the row to update
    */
    function update_row_values($row) {
        var ig = $row.closest('tbody.input-group');
        var ig_ind = ig.index('tbody.input-group');
        var cand_ind = ig.find('tr.candidate').index($row);
        update_input($row, 'csrf_token', null, ig_ind, cand_ind)
        update_input($row, 'inp',  "I" + (ig_ind + 1), ig_ind, cand_ind);
        update_input($row, 'outp', "O" + (num_rows_added + 1), ig_ind, cand_ind);
        update_input($row, 'optimal', "", ig_ind, cand_ind);
        for (var i = 0; i < $row.children('td').size() - FIRST_CONSTRAINT_IND; ++i) {
            update_input($row, 'vvector-' + i, "", ig_ind, cand_ind);
        }
    }

    /**
     * Function set_calculate_all_availability
     * =======================================
     * Check the number of constraints, and enable or disable the calculate_all button
     * appropriately. Also display or hide corresponding alert message.
     */
    function set_calculate_all_availability() {
        var last_index = $('#head_table th:last-child').index();
        if (last_index > MAX_POOT_IND) {
            $("#calculate_all").prop('disabled', true);
            $("#classical_only_alert").show();
        }
        if (last_index <= MAX_POOT_IND) {
            $("#calculate_all").prop('disabled', false);
            $("#classical_only_alert").hide();
        }

    }

    /*
    * Function: outer_html
    * ====================
    * Takes a jQuery object and returns the entire html of the element it
    * represents, including the tags that make up the element itself.
    */
    function outer_html($elem) {
        // the call to .wrap() allows the outer html to be accessed
        var ret = $elem.wrap('<div>').parent().html();
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
        var last_index = $('#tableaux_header th:last-child').index()
        if (last_index < MAX_TABLEAUX_IND) {

            // clone the first constraint cell from each row, insert it
            $('#tableaux, #head_table').find('tr').each(function() {
                var html_str = outer_html($(this).find('td, th').eq(FIRST_CONSTRAINT_IND));
                $(html_str).insertBefore($(this).find('td:last-child, th:last-child'));
            });


            // update the new header constraint
            var header = $('#head_table th:nth-last-child(2)');
            var constraint_ind = header.index() - FIRST_CONSTRAINT_IND;
            var name_str = 'constraints-' + constraint_ind;
            header.find('input').attr({id: name_str,
                                       name: name_str,
                                       value: 'C' + (constraint_ind + 1)});

            // update all the violation vectors in the table
            $('#tableaux td:nth-last-child(2)').each(function(){
                var ig = $(this).closest('tbody.input-group');
                var ig_ind = ig.index('tbody.input-group');
                var cand_ind = ig.find('tr.candidate').index($(this).closest('tr.candidate'));
                var name_str = 'input_groups-' + ig_ind +
                               '-candidates-' + cand_ind +
                               '-vvector-' + constraint_ind;
                $(this).find('input').attr({id: name_str,
                                            name: name_str,
                                            value: ''});
            });
        }
        equalize_column_widths();
        set_calculate_all_availability()
    }

    /*
    * Function: delete_constraint_column
    * ==================================
    * Click handler for the #delete_constraint button. Deletes the second to last
    * cell from each column, assuming there are enough columns left in the table.
    */
    function delete_constraint_column(e) {
        // check that the table isn't too small
        var last_index = $('#head_table th:last-child').index();
        if (last_index > MIN_TABLEAUX_IND) {
            var width_of_removed = $('#head_table th:nth-last-child(2)').width();
            $('#head_table th:nth-last-child(2), #tableaux td:nth-last-child(2)').remove();
            $("#head_table").width($("#head_table").width() - width_of_removed);
            resize_tableaux();
        }
        equalize_column_widths();
        set_calculate_all_availability();
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
    * Function: add_csrf_field
    *  ========================
    *  Helper function to add a csrf field to the given input group (ig).
    */
    function add_csrf_field(ig) {
        var ig_ind = ig.index('tbody.input-group');
        var csrf_name_str = 'input_groups-' + ig_ind + '-csrf_token';
        var csrf_input = $(outer_html($('#input_groups-0-csrf_token')));
        csrf_input.attr({id: csrf_name_str, name: csrf_name_str});
        csrf_input.prependTo(ig);
    }

    /*
    * Function: add_input_group
    * =========================
    * Event handler for adding an input group to the table. Clones the first
    * candidate row, wraps it in a div, and sticks at the end of the table.
    */
    function add_input_group(e) {
        var row_str = outer_html($('#tableaux tr.candidate').eq(0));
        var to_append = $(row_str).wrap('<tbody>').parent();
        to_append.addClass('input-group');

        var row = to_append.find('tr.candidate');
        to_append.insertAfter($('#tableaux tbody.input-group:last-child'));
        num_rows_added++;
        update_row_values(row);
        add_csrf_field(to_append);

        row.find('.add_output').click(add_output_row);
        row.find('.delete_output').click(delete_output_row);
        row.find('input[name$="inp"]').change(update_output_rows);

        $('.has-tooltip').tooltip();
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
        input_group.append(to_append);
        update_row_values(to_append);
        input_field = to_append.find('input[name$="inp"]');
        input_field.attr('value', input_value);
        input_field.val(input_value);
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

    function resize_tableaux() {
        $("#tableaux, .scrollable").width($("#head_table").width());
    }

    function get_column(ind) {
        return $('#tableaux tr').map(function() {
            return $(this).find("td:eq("+ind+")");
        });
    }

    function get_column_width(ind) {
        var column = get_column(ind);
        var max_input_width = 0;
        column.each(function() {
            var width = $(this).find(" :first-child").width();
            max_input_width = Math.max(width, max_input_width);
        });
        return max_input_width + INPUT_HORIZONTAL_PADDING_MARGIN;
    }

    function equalize_column_widths() {
        $('#head_table th').each(function() {
            var $header = $(this);
            var ind = $header.index();
            var col_width = get_column_width(ind);
            var th_width = $header.width();
            var header_input_width = $header.find("input").width() + INPUT_HORIZONTAL_PADDING_MARGIN;
            var header_width = Math.min(th_width, header_input_width);
            var before_col_width = $("#tableaux td:eq("+ind+")").width()
            var new_width = Math.max(header_width, col_width);


            if (th_width < new_width) {
                var diff = new_width - $header.width();
                $("#head_table").width($("#head_table").width() + diff);
            }

            $header.width(new_width);
            resize_tableaux();
            get_column(ind).each(function() {
                $(this).width(new_width);
            });


            var after_col_width = $("#tableaux td:eq("+ind+")").width()
            //console.log("ind:"+ind+", col_width:"+col_width+", th_width:"+
            //th_width+", header_input_width:"+header_input_width+
            //", before_col_width:"+before_col_width+", after_col_width:"+
            //after_col_width+", new_width:"+new_width);
            if (after_col_width < before_col_width) {
                var diff = before_col_width - after_col_width;
                $("#head_table").width($("#head_table").width() - diff);
                resize_tableaux();
            }
        });
        resize_tableaux();
    }

    function resize_input_to_value(input, c) {
        var $input = $(input)
        $span = $("<span style='display:none'></span>");
        $span.insertAfter($input);
        $span.text("l" + $input.val() + c + "O"); // the hidden span takes the value of the input
        var new_width = $span.width();
        $input.width(new_width); // apply width of the span to the input
    }

    $("fieldset").keydown(function(e) {
        if (e.target.nodeName === "INPUT") {
            var c = String.fromCharCode(e.keyCode|e.charCode);
            resize_input_to_value(e.target, c);
        }
        equalize_column_widths();
    });


    // Add the click handlers when the DOM is ready.
    $('#tableaux input[name$="inp"]').change(update_output_rows);
    $('#add_input_group').click(add_input_group);
    $('#delete_input_group').click(delete_input_group);
    $('#add_constraint').click(add_constraint_column);
    $('#delete_constraint').click(delete_constraint_column);
    $('#tableaux .add_output').click(add_output_row);
    $('#tableaux .delete_output').click(delete_output_row);
    set_calculate_all_availability();
    $("fieldset input[type='text']").each(function() {
        resize_input_to_value(this, "");
    });
    equalize_column_widths();
    $('.has-popover').popover();
    $('.has-tooltip').tooltip();
})(this, this.document);
