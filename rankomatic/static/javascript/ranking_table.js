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
function RankingTable($table) {
    this.table = $table;
    this.ranking = new Ranking();
    this.transitive_alert = $("#ranking_required_alert");
    this.table.click($.proxy(this.check_or_uncheck, this));
    $("#clear").click($.proxy(this.clear, this));
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
}

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


RankingTable.prototype.modify_ranking = function(relation) {
    if (this.ranking.contains(relation)) {
        this.try_removal(relation);  // wrap with transitivity alert
    } else {
        this.ranking.add(relation);
    }
}

RankingTable.prototype.try_removal = function(relation) {
    removable = this.ranking.remove(relation);
    if (!removable) {
        this.transitive_alert.show();
    }
}

function Ranking() {
    this.set = new TransitiveSet();
}

Ranking.prototype.add = function(relation) {
    this.set.add(relation.sup, relation.inf);
}

Ranking.prototype.contains = function(relation) {
    return this.set.contains(relation.sup, relation.inf);
}

Ranking.prototype.remove = function(relation) {
    return this.set.remove(relation.sup, relation.inf);
}

Ranking.prototype.check_appropriate_cells = function() {
    this.set.forEach(function(a, b) {
        var relation = new Relation({sup: a, inf: b});
        var inverse = new Relation({sup: b, inf: a});
        relation.check();
        inverse.deactivate();
     });
}

function Relation(obj) {
    if (obj instanceof jQuery) {
        this.cell = obj;
        this.sup = obj.closest("tr").attr('id').slice(4);
        this.inf = obj.attr('name');
    } else {
        this.sup = obj.sup;
        this.inf = obj.inf;
        this.cell = this._get_cell(this.sup, this.inf);
    }
}

Relation.prototype._get_cell = function(row, col) {
    row = Util.escape_selector(row);
    col = Util.escape_selector(col);
    var row_selector = "tr#" + "row_" + row;
    var cell_selector = "td[name=" + col + "]";
    var $row = $(row_selector);
    return $row.find(cell_selector);
}

Relation.prototype.is_active = function() {
    return !this.cell.hasClass("deactivated");
}

Relation.prototype.deactivate = function() {
    this.cell.removeClass("checked unchecked");
    this.cell.addClass("deactivated");
}

Relation.prototype.activate = function() {
    this.cell.removeClass("checked unchecked deactivated");
}

Relation.prototype.uncheck = function() {
    this.cell.removeClass("checked");
    this.cell.addClass("unchecked");
    this.cell.html("");
}

Relation.prototype.check = function() {
    this.cell.removeClass("unchecked");
    this.cell.addClass("checked");
    this.cell.html("&#10003;")
}
