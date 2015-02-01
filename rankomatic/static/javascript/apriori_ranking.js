(function(window, document, undefined) {
    var table_template = Handlebars.compile($("#apriori_table_template").html());
    var old_constraints = $("#tableaux_header").html();

    function show_apriori_table() {
        var new_constraints = $("#tableaux_header").html();
        if (need_to_redraw_table(new_constraints, old_constraints)) {
            redraw_table();
        }
        old_constraints = new_constraints;
    }

    function need_to_redraw_table(new_cons, old_cons) {
        return !($("#apriori_table_container").html().length && old_cons === new_const)
    }

    function redraw_table() {
        var constraints = get_constraints();
        $("#apriori_table_container").html(table_template(
            {'constraints': constraints_grid()}
        ));
        $("#header_label").attr('colspan', constraints.length);
        var ranking_table = new RankingTable($("#apriori_table"), $("#apriori_ranking"));
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
