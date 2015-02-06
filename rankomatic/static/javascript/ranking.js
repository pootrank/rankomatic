/* constructor: Ranking
 * usage: var ranking = new Ranking();
 * ===================================
 * A wrapper for TransitiveSet which has knowledge of Relations.
 *
 * Wrap the generic TransitiveSet with something that can use Relation
 * objects instead of passing around strings. Add, remove, and check for
 * membership, as well as call Relation's check and deactivate methods
 * during drawing.
 */
function Ranking(ranking) {
    this.set = new TransitiveSet(ranking);
}

/* function: add
 * =============
 * Add the relation to the ranking. This may add more than one ranking,
 * as it is closed under transitivity.
 */
Ranking.prototype.add = function(relation) {
    this.set.add(relation.sup, relation.inf);
}

/* function: contains
 * ==================
 * Return a boolean indicating whether the ranking contains the relation.
 */
Ranking.prototype.contains = function(relation) {
    return this.set.contains(relation.sup, relation.inf);
}

/* function: remove
 * ================
 * Attempt removal of the relation.
 *
 * Returns a length-two Array of the relation if the relation can be
 * removed. If the given relation can't be returned because it is
 * transitively recquired, returns false.
 */
Ranking.prototype.remove = function(relation) {
    return this.set.remove(relation.sup, relation.inf);
}

/* function: check_appropriate_cells
 * =================================
 * Call the check method for every relation in the set, and deactivate the
 * inverse of every member in the set.
 */
Ranking.prototype.check_appropriate_cells = function() {
    this.set.forEach(function(a, b) {
        var relation = new Relation({sup: a, inf: b});
        var inverse = new Relation({sup: b, inf: a});
        relation.check();
        inverse.deactivate();
    });
}

/* function: string
 * ================
 * Return a string representation of the ranking.
 *
 * The string is formatted as a JSON array of length-two arrays.
 */
Ranking.prototype.string = function() {
    return JSON.stringify(this.set.to_array());
}

/* constructor: Relation
 * usage: var rel = new Relation($("td.reln"));
 * usage: var rel = new Relation({sup: 'a', inf: 'b'});
 * ====================================================
 * Represents one ordered-pair relation for ranking purposes.
 *
 * The constructor can be called with either a jQuery object of the
 * cell that represents this particular relation, or a bare object with
 * 'sup' and 'inf' keys, whose values are the superior and inferior
 * members of the relation, respectively. Provides a back-and-forth
 * interface between the TransitiveSet ranking and the DOM representation,
 * and can be used to check/uncheck and activate/deactivate the
 * corresponding table cell, along with check if the table cell is
 * activated or not.
 */
function Relation(obj) {
    if (obj instanceof jQuery) {
        this.cell = obj;
        this.sup = obj.closest("tr").attr('id').slice(4);
        this.inf = obj.attr('name');
    } else {
        this.sup = obj.sup;
        this.inf = obj.inf;
        this.cell = this._get_cell();
    }
}

/* function: _get_cell
 * ===================
 * Return a jQuery object corresponding to this relation's table cell.
 */
Relation.prototype._get_cell = function() {
    var row = Util.escape_selector(this.sup);  // these are user-provided
    var col = Util.escape_selector(this.inf);
    var row_selector = "tr#row_" + row;
    var cell_selector = "td[name=" + col + "]";
    var $row = $(row_selector);
    return $row.find(cell_selector);
}

/* function: is_active
 * ===================
 * Return a boolean indicating whether the relation's cell is activated or not.
 */
Relation.prototype.is_active = function() {
    return !this.cell.hasClass("deactivated");
}

/* function: deactivate
 * ====================
 * Deactivate the relation's table cell so the user cannot interact with it.
 */
Relation.prototype.deactivate = function() {
    this.cell.removeClass("checked unchecked");
    this.cell.addClass("deactivated");
}

/* function: activate
 * ==================
 * Activate the relation's table cell so the user can interact with it.
 */
Relation.prototype.activate = function() {
    this.cell.removeClass("checked unchecked deactivated");
}

/* function: uncheck
 * =================
 * Uncheck the relation's tabe cell, indicating it is not in the ranking.
 */
Relation.prototype.uncheck = function() {
    this.cell.removeClass("checked");
    this.cell.addClass("unchecked");
    this.cell.html("");
}

/* function: check
 * ===============
 * Check the relation's table cell, indicating it is in the ranking.
 */
Relation.prototype.check = function() {
    this.cell.removeClass("unchecked");
    this.cell.addClass("checked");
    this.cell.html("&#10003;")
}
