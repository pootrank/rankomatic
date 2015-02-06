/* constructor: TransitiveSet
 * ==========================
 * creates a set which represents a transitive ranking. Adding and subtracting
 * elmeents is always closed under transitivity.
 */
function TransitiveSet(ranking) {
    this.relations = {}
    var trans_set = this;
    if (ranking) {
        ranking.forEach(function(val) {
            trans_set.add(val[0], val[1]);
        });
    }
}

/* Method: forEach
 * Usage: tset.forEach(function(a, b) { // do stuff });
 * ====================================================
 * Submit a callback to be executed on every relation in the set.
 *
 * The callback needs to take two functions, the first and second elements
 * in the relation. It will be executed on evey pair in the order.
 */
TransitiveSet.prototype.forEach = function(callback) {
    var obj = this;
    for (var key in obj.relations) {
        for (var val in obj.relations[key]) {
            callback(key, val);
        }
    }
}

/* Method: to_array
 * Usage: var arr = tset.to_array()
 * ===============================
 * Get an Array version of the transitive set.
 *
 * Returns an Array of all the relations, where each relation in the order is
 * an ordered pair (Array r of length two).
 */
TransitiveSet.prototype.to_array = function() {
    arr = [];
    this.forEach(function(a, b) {
        arr.push([a, b]);
    });
    return arr;
}

/* Method: closeUnderTransitivity
 * Usage: tset.closeUnderTransitivity()
 * ======================================
 * Ensure that the transitive set is actually transitive.
 */
TransitiveSet.prototype.closeUnderTransitivity = function() {
    var obj = this;
    to_add = [];
    obj.forEach(function(a, b) {
        obj.forEach(function(x, y) {
            if (b === x) {
                to_add.push([a, y]);
            }
        });
    });
    to_add.forEach(function(elem) {
        obj._add(elem[0], elem[1]);
    });
}

/* Method: keyExists
 * Usage: if (tset.keyExists('a')) { // do stuff with 'a' };
 * =========================================================
 * Determine whether or not a key exists in the transitive set.
 */
TransitiveSet.prototype.keyExists = function(key) {
    if (typeof this.relations[key] === "undefined" || this.relations[key] === null) {
        return false
    }
    return true
}

/* Method: contains
 * Usage: if (tset.contains('a', 'b'))) { // do stuff };
 * =====================================================
 * Returns true if the relation specified is in the order, false otherwise.
 */
TransitiveSet.prototype.contains = function(a, b) {
    if (this.keyExists(a) && this.relations[a][b]) {
        return true;
    }
    return false;
}

/* Helper method: _add
 * ===================
 * Adds a relation without guaranteeing transitivity. For internal use.
 */
TransitiveSet.prototype._add = function(a, b) {
    if (typeof b === "undefined" || b === null) {
        throw new Error("must have two arguments");
    }
    if (!this.keyExists(a)) {
        this.relations[a] = {};
        this.relations[a][b] = true;
    } else {
        this.relations[a][b] = true;
    }
}

/* Method: add
 * Usage: tset.add('a', 'b')
 * =========================
 * Add a relation to the transitive set.
 *
 * This adds the relation aRb to the order defined by this set. It also
 * adds any relations xRb or aRy that are necessitated to maintain
 * transitivity (e.g. if xRa is in the set, it adds xRb).
 */
TransitiveSet.prototype.add = function(a, b) {
    this._add(a, b);
    this.closeUnderTransitivity();
}

/* Method: remove
 * Usage: tset.remove('a', 'b')
 * ============================
 * Remove a relation from the transitive set.
 *
 * If the relation is in the set and can be removed, returns an array of
 * length two containing the relation, otherwise it returns false.
 */
TransitiveSet.prototype.remove = function(a, b) {
    if (this.contains(a, b)) {
        delete this.relations[a][b];
        this.closeUnderTransitivity();
        if (!this.contains(a, b)) {
            return [a, b];
        }
    }
    return false
}
