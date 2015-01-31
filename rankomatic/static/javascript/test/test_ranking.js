QUnit.module('Ranking', {
    beforeEach: function() {
        this.ranking = new Ranking();
        this.reln = new Relation({sup: 'a', inf: 'b'});
        this.ranking.add(this.reln);
        this.not_contained = new Relation({sup: "b", inf: "a"});
        this.trans_reln = new Relation({sup: 'b', inf: 'c'});
        this.transitively_required = new Relation({sup: 'a', inf: 'c'});

        this.assert_checked = function(reln) {
            var str = reln.sup + " >> " + reln.inf;
            this.assert.ok(reln.cell.hasClass('checked'), str + " is checked");
            this.assert.ok(!reln.cell.hasClass('unchecked'),
                           str + " is not unchecked");
            this.assert.ok(reln.is_active(), str + " is active");

            var inverse = new Relation({sup: reln.inf, inf: reln.sup});
            this.assert.ok(!inverse.is_active(), str + " inverse deactivated");
        }
    }
});

QUnit.test('constructor', function(assert) {
    assert.ok(this.ranking, "constructor makes something");
});

QUnit.test('contains', function(assert) {
    assert.ok(!this.ranking.contains(this.not_contained),
              "doesn't have something not added");
    assert.ok(this.ranking.contains(this.reln), "has already added relation");
});

QUnit.test('add', function(assert) {
    assert.ok(this.ranking.set.contains('a', 'b'),
              "adding a relation adds it to the TSet");
    this.ranking.add(this.trans_reln);
    assert.ok(this.ranking.contains(this.transitively_required),
              "is closed under transitivity");
});

QUnit.test('remove', function(assert) {
    assert.ok(!this.ranking.remove(this.not_contained),
              "can't remove something not contained");
    assert.deepEqual(this.ranking.remove(this.reln), ['a', 'b'],
                    "removing a relation gives you that relation");
});

QUnit.test('remove transitively required', function(assert) {
    this.ranking.add(this.trans_reln);
    assert.ok(this.ranking.contains(this.transitively_required),
             "transitively required relation was added also");
    assert.ok(!this.ranking.remove(this.transitively_required),
              "can't remove transitively required relation");
});

QUnit.test('check_appropriate_cells', function(assert) {
    this.ranking.add(this.trans_reln);
    this.ranking.check_appropriate_cells();

    this.assert = assert;
    this.assert_checked(this.reln);
    this.assert_checked(this.trans_reln);
    this.assert_checked(this.transitively_required);
});
