(function() {
  'use strict';

  angular
    .module('app.editor.apriori')
    .factory('TransitiveSet', transitive_set);

  function transitive_set() {

    TransitiveSet.prototype.forEach = forEach;
    TransitiveSet.prototype.to_array = to_array;
    TransitiveSet.prototype.contains = contains;
    TransitiveSet.prototype.add = add;
    TransitiveSet.prototype.remove = remove;
    TransitiveSet.prototype.cannot_add = cannot_add;

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
    function forEach(callback) {
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
    function to_array() {
        var arr = [];
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
        var to_add = [];
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
    function contains(a, b) {
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
        } else if (this.cannot_add(a, b)) {
          return false;
        } else if (!this.keyExists(a)) {
            this.relations[a] = {};
        }
        this.relations[a][b] = true;
        return true;
    }

    /* Method: cannot_add
     * Usage: if (tset.cannot_add('a', 'b')) // do stuff
     * =================================================
     * Return true if the given relation cannot be added to the set.
     */
    function cannot_add(a, b) {
      return a === b || this.contains(b, a);
    }

    /* Method: add
     * Usage: tset.add('a', 'b')
     * =========================
     * Add a relation to the transitive set.
     *
     * This adds the relation aRb to the order defined by this set. It also
     * adds any relations xRb or aRy that are necessitated to maintain
     * transitivity (e.g. if xRa is in the set, it adds xRb). If the relation
     * was successfully added, it returns true, otherwise it returns false.
     * It will return false if a === b or if (b, a) is already in the set.
     * This prevents any cycles from being added.
     */
    function add(a, b) {
        var successfully_added = this._add(a, b);
        this.closeUnderTransitivity();
        return successfully_added;
    }

    /* Method: remove
     * Usage: tset.remove('a', 'b')
     * ============================
     * Remove a relation from the transitive set.
     *
     * If the relation is in the set and can be removed, removes it and
     * returns true, otherwise it returns false.
     */
    function remove(a, b) {
        if (this.contains(a, b)) {
            delete this.relations[a][b];
            this.closeUnderTransitivity();
            if (!this.contains(a, b)) {
              return true;
            }
        }
        return false;
    }

    return TransitiveSet;
  }
})();
