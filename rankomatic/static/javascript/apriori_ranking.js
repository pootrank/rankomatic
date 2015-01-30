(function(window, document, undefined) {
    var table_template = Handlebars.compile($("#apriori_table_template").html());
    var old_constraints = $("#tableaux_header").html();

    function show_apriori_table() {
        var new_constraints = $("#tableaux_header").html();
        if (!$("#apriori_table_container").html() ||
            old_constraints !== new_constraints) {
            var constraints = get_constraints();
            $("#apriori_table_container").html(table_template(
                {'constraints': constraints_grid(constraints)}
            ));
            $("#header_label").attr('colspan', constraints.length);
            $("#ranking_required_alert").hide();
            var ranking_table = new RankingTable($("#apriori_table"));
        }
        old_constraints = $("#tableaux_header").html();
    }

    function get_constraints() {
        return $("#tableaux_header th.constraint").map(function() {
            return $(this).find("input").val();
        }).get();
    }

    function constraints_grid(constraints) {
        var grid = [];
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
