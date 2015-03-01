QUnit.module("Relation", {
    beforeEach: function() {
        load_html();
        this.cell = $("#relation");
        this.rel = new Relation(this.cell);
        this.assert_relation = function(reln, str) {
            this.assert.equal(reln.sup, 'a', str + "superior constraint ok");
            this.assert.equal(reln.inf, 'b', str + "inferior constraint ok");
            this.assert.ok(this.cell.is(reln.cell), str + "jQuery cell ok");
        }
    },
    afterEach: function() {
        remove_html();
    }
 });

QUnit.test('constructor', function(assert) {
    var jquery_relation = new Relation(this.cell);
    this.assert = assert;
    this.assert_relation(jquery_relation, "jQuery: ");
    var obj_relation = new Relation({sup: 'a', inf: 'b'});
    this.assert_relation(obj_relation, "bare object: ");
});

QUnit.test('is_active', function(assert) {
    assert.ok(this.rel.is_active(), "is active before nothing happens");
    $("#relation").addClass("deactivated");
    assert.ok(!this.rel.is_active(), "not active when has 'deactivated' class");
});

QUnit.test('deactivate', function(assert) {
    assert.ok(this.rel.is_active(), "active to start with");
    this.rel.deactivate();
    assert.ok(!this.rel.is_active(), "inactive after deactivating");
});

QUnit.test('activate', function(assert) {
    this.rel.deactivate();
    assert.ok(!this.rel.is_active(), "begin inactive");
    this.rel.activate();
    assert.ok(this.rel.is_active(), "active after using 'activate'");
});

QUnit.test('check', function(assert) {
    this.rel.check();
    assert.ok(!this.rel.cell.hasClass("unchecked"), "no unchecked class");
    assert.ok(this.rel.cell.hasClass("checked"), "has checked class");
    assert.equal(this.rel.cell.html().length, 1, "has checkmark in HTML");
});

QUnit.test('uncheck', function(assert) {
    this.rel.check();
    this.rel.uncheck();
    assert.ok(this.rel.cell.hasClass("unchecked"), "has unchecked class");
    assert.ok(!this.rel.cell.hasClass("chekced"), "no checked class");
    assert.equal(this.rel.cell.html(), "", "nothing in HTML")
});
