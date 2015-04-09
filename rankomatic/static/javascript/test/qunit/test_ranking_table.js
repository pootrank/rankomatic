(function(window, document, undefined) {
QUnit.module('RankingTable', {
    beforeEach: function() {
        load_html();
    },
    afterEach: function() {
        remove_html();
    }
});

QUnit.test('constructor', function(assert) {
    var $table = $('#ranking');
    var $input = $("#ranking-string")
    var rank_table = new RankingTable($table, $input);
    assert.ok(rank_table, 'constructor makes something');
    assert.ok(table_is_blank(), 'table initialized in correct state');
});

QUnit.test('check_or_uncheck', function(assert) {
    var $table = $("#ranking");
    var $trans_alert = $("#ranking_required_alert");
    var $input = $("#ranking-string")

    var rank_table = new RankingTable($table, $input);

    var reln_a_a = new Relation({sup: 'a', inf: 'a'});
    var reln_a_b = new Relation({sup: 'a', inf: 'b'});
    var reln_b_c = new Relation({sup: 'b', inf: 'c'});
    var reln_a_c = new Relation({sup: 'a', inf: 'c'});
    var reln_b_a = new Relation({sup: 'b', inf: 'a'});

    assert.equal($input.val(), "[]", "string empty to begin");
    assert.ok(!reln_a_a.is_active(), 'diagonal inactive before click');
    reln_a_a.cell.click();
    assert.equal($input.val(), "[]", "string empty after click");
    assert.ok(!reln_a_a.is_active(), 'diagonal remains inactive after click');

    assert.ok(reln_a_b.cell.hasClass('unchecked'), 'blank unchecked before click');
    assert.ok(reln_b_a.is_active(), 'inverse active before click');

    reln_a_b.cell.click();
    assert.ok(is_checked(reln_a_b), 'checked after click');
    assert.ok(!reln_b_a.is_active(), 'inverse is deactivated after click');
    assert.equal($input.val(), '[["a","b"]]', "string has one element after click");

    reln_a_b.cell.click();
    assert.ok(is_unchecked(reln_a_b),  'unchecked after two clicks');
    assert.ok(reln_b_a.is_active(), 'inverse active after two clicks');
    assert.equal($input.val(), '[]', 'string empty after two clicks');

    reln_a_b.cell.click();
    reln_b_c.cell.click();
    assert.ok(is_checked(reln_a_c), 'transitive cell checked after required');
    assert.equal($input.val(), '[["a","b"],["a","c"],["b","c"]]',
                 "string has all three relations");

    assert.ok($trans_alert.is(":hidden"), 'transitive alert hidden first');
    reln_a_c.cell.click();
    assert.ok(is_checked(reln_a_c), 'transitive cell remains checked');
    assert.ok($trans_alert.is(":visible"), 'transitive alert displays after attempt to' +
                                           'remove transitively required relation');
    assert.equal($input.val(), '[["a","b"],["a","c"],["b","c"]]',
                 "string has all three relations after trying to remove tranitive");

    assert.ok(!table_is_blank(), 'table not cleared after lots of manipulation');
    $("#clear").click();
    assert.ok(table_is_blank(), 'table cleared when clicking clear button');
    assert.equal($input.val(), "[]", "string empty after table cleared");
});

function table_is_blank() {
    var blank = true;
    $('td.checkbox_container').each(function() {
        var reln = new Relation($(this));
        if (!reln.is_active() && reln.sup != reln.inf) {
            blank = false;
        } else if (reln.is_active() && reln.cell.hasClass('checked')) {
            blank = false;
        }
    });
    return blank;
}

function is_checked(reln) {
    return has_first_and_not_second(reln.cell, 'checked', 'unchecked');
}

function is_unchecked(reln) {
    return has_first_and_not_second(reln.cell, 'unchecked', 'checked');
}

function has_first_and_not_second($elem, first, second) {
    return ($elem.hasClass(first) && !$elem.hasClass('second'));
}
})(this, this.document);
