var show_apriori_table;
(function(window, document, undefined) {
    var table_template = Handlebars.compile($("#apriori_table_template").html());
    var old_constraints = get_constraints();

    show_apriori_table = function() {
        var new_constraints = get_constraints();
        if (!arrays_equal(old_constraints, new_constraints)) {
            $("apriori_ranking").val("[]");
            redraw_table();
        } else if (!$("#apriori_table_container").html()) {
            redraw_table();
        }
        old_constraints = new_constraints;
    }

    function arrays_equal(arr1, arr2) {
        return $(arr1).not(arr2).length == 0 && $(arr2).not(arr1).length == 0
    }

    function redraw_table() {
        var constraints = get_constraints();
        $("#apriori_table_container").html(table_template(
            {'constraints': constraints_grid()}
        ));
        $("#header_label").attr('colspan', constraints.length);
        var ranking_table = new RankingTable($("#apriori_table"),
                                             $("#apriori_ranking"));
    }

    function get_constraints() {
        return $("#tableaux_header th.constraint").map(function() {
            return $(this).find("input").val();
        }).get();
    }

    function constraints_grid() {
        var grid = [];
        var constraints = get_constraints();
        for (i = 0; i < constraints.length; i++) {
            grid.push({
                'constraint': constraints[i],
                'dominates': constraints
            });
        }
        return grid;
    }
    $("#apriori-tab").click(show_apriori_table);
})(this, this.document)
