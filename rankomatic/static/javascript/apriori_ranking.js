(function(window, document, undefined) {
    var table_template = Handlebars.compile($("#apriori_table_template").html());
    var apriori_ranking = new TransitiveSet();

    function switch_tabs_to_this(target) {
        $("#edit_tabs li").each(function() {
            $(this).removeClass("active");
        });
        $(target).addClass("active");
    }

    $("#edit_tab").click(function() {
        switch_tabs_to_this(this);
        $("#apriori_page").hide();
        $("#dataset").show();
    });

    $("#apriori_tab").click(function() {
        switch_tabs_to_this(this);
        $("#dataset").hide();
        show_apriori_table();
        $("#apriori_page").show();
    });

    function escape_selector(str) {
        if (str) {
            return str.replace(/([ !"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~`'"])/g,
                       '\\$&');
        }
        return str;
    }

    function show_apriori_table() {
        var constraints = $("#tableaux_header th.constraint").map(function() {
                return $(this).find("input").val();
            }).get();
        var grid = []
        for (i = 0; i < constraints.length; i++) {
            grid.push({
                'constraint': constraints[i],
                'dominates': constraints
            });
        }
        $("#apriori_table_container").html(table_template(
            {'constraints': grid}
        ));
        $("#header_label").attr('colspan', constraints.length);
        deactivate_diagonal();
        set_apriori_listeners();
        $("#ranking_required_alert").hide();
    }

    function deactivate_diagonal() {
        $("#apriori_table td.checkbox_container").each(function() {
            coords = get_coordinates($(this))
            if (coords.row === coords.col) {
                deactivate_cell($(this));
            }
        });
    }

    function get_coordinates($target) {
        var col = $target.attr('name');
        var row = $target.closest("tr").attr('id').slice(4);
        return {'row': row, 'col': col}
    }

    function get_cell(row, col) {
        console.log(row, col);
        row = escape_selector(row);
        col = escape_selector(col);
        var row_selector = "tr#" + "row_" + row;
        var cell_selector = "td[name=" + col + "]";
        console.log(row_selector, cell_selector);
        var $row = $(row_selector);
        var $cell = $row.find(cell_selector);
        return $cell;
    }

    function deactivate_cell($to_deactivate) {
        $to_deactivate.removeClass("checked unchecked");
        $to_deactivate.addClass("deactivated");
    }

    function reactivate_cell($cell) {
        $cell.removeClass("deactivated")
    }

    function set_apriori_listeners() {
        $("#apriori_table").click(function(event) {
            var $target = $(event.target);
            if ($target.is('td.checkbox_container')) {
                if (!$target.hasClass("deactivated")) {
                    $("#ranking_required_alert").hide();
                    modify_ranking($target);
                    redraw_ranking();
                }
            }
        });
    }

    function modify_ranking($cell) {
        if ($cell.hasClass("checked")) {
            remove_relation($cell);
        } else {
            add_relation($cell);
        }
    }

    function add_relation($cell) {
        coordinates = get_coordinates($cell);
        apriori_ranking.add(coordinates.row, coordinates.col);
    }

    function remove_relation($cell) {
        coords = get_coordinates($cell);
        var removable = apriori_ranking.remove(coords.row, coords.col);
        if (!removable && apriori_ranking.contains(coords.row, coords.col)) {
            $("#ranking_required_alert").show();
        }
    }

    function redraw_ranking() {
        $("td.checkbox_container").each(function() {
            uncheck_cell($(this));
        });
        deactivate_diagonal();
        apriori_ranking.forEach(function(a, b) {
            check_cell(get_cell(a, b));
            deactivate_cell(get_cell(b, a));
        });
    }

    function uncheck_cell($cell) {
        reactivate_cell($cell);
        $cell.removeClass("checked");
        $cell.addClass("unchecked");
        $cell.html("");
    }

    function check_cell($cell) {
        $cell.removeClass("unchecked");
        $cell.addClass("checked");
        $cell.html("&#10003;")
    }
})(this, this.document)
