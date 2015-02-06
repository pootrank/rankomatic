/* constructor: RankingTable
 * usage: var rank_table = new RankingTable($("#rank-table"));
 * ===========================================================
 * Create a table that defines a transitive, asymmetric ranking.
 *
 * Pass in a JQuery object of the table that you want to use to define your
 * ranking. The TDs that will be the checkboxes need to have class
 * 'checkbox_container' and their name needs to match the constraint of their
 * column. Their parent TR needs to have id 'row_*', where * is the name of the
 * row constraint.
 */
function RankingTable($table, $input) {
    this.table = $table;
    this.input = $input;
    this.ranking = new Ranking(JSON.parse($input.val()));
    this.transitive_alert = $("#ranking_required_alert");
    this.table.click($.proxy(this.check_or_uncheck, this));
    $("#clear").click($.proxy(this.clear, this));
    this.transitive_alert.hide();
    this.draw();
}

RankingTable.prototype.check_or_uncheck = function(event) {
    var $target = $(event.target);
    if ($target.is('td.checkbox_container')) {
        var relation = new Relation($target);
        if (relation.is_active()) {
            this.transitive_alert.hide();
            this.modify_ranking(relation);
            this.draw();
        }
    }
}

/* function: clear
 * usage: ranking_table.clear();
 * =============================
 * Clear out all the relations held in the ranking table.
 *
 * Remove all relations, and redraw the table to reflect the empty state.
 */
RankingTable.prototype.clear = function() {
    this.transitive_alert.hide();
    this.ranking = new Ranking();
    this.draw();
}

/* function: draw
 * usage: ranking_table.draw();
 * ============================
 * Bring the HTML display into conformity with the internal ranking.
 *
 * For every relation in the ranking, check the box in the table. Deactivate
 * the inverse of that relation, since it has to be asymmetric. Make sure the
 * diagonal is blanked out, as no element can dominate itself.
 */
RankingTable.prototype.draw = function() {
    this.initialize_blank();
    this.ranking.check_appropriate_cells();
    this.input.val(this.ranking.string());
}

/* function: initialize_blank
 * ==========================
 * The first step of drawing the table is initializing it into a blank state.
 *
 * This deactivates the diagonal, activates and unchecks all non-diagonal cells.
 */
RankingTable.prototype.initialize_blank = function() {
    this.table.find("td.checkbox_container").each(function() {
        var relation = new Relation($(this));
        if (relation.sup === relation.inf) {  // deactivate diagonal
            relation.deactivate();
        } else {  // start with it blank
            relation.activate();
            relation.uncheck();
        }
    });
}

/* function: modify_ranking
 * usage: ranking_table.modify_ranking(relation);
 * ==============================================
 * Modify the ranking based on the given relation.
 *
 * If the ranking contains the relation, try to remove it, otherwise add it.
 */
RankingTable.prototype.modify_ranking = function(relation) {
    if (this.ranking.contains(relation)) {
        this.try_removal(relation);  // wrap with transitivity alert
    } else {
        this.ranking.add(relation);
    }
}

/* function: try_removal
 * =====================
 * Try to remove the given relation, otherwise show the transitivity alert.
 */
RankingTable.prototype.try_removal = function(relation) {
    removable = this.ranking.remove(relation);
    if (!removable) {
        this.transitive_alert.show();
    }
}
