(function(window, document, undefined) {
QUnit.module("A Priori Ranking", {
    beforeEach: function() {
        $("#apriori-tab").off('click').click(show_apriori_table);
    }
});

QUnit.test("Displays ranking empty on load", function(assert) {
    assert.ok(!$("#apriori_table_container").html(),
              "nothing in container before click");
    $("#apriori-tab").click();
    assert.ok($("#apriori_table_container").html(), "something in the container");
    assert.ok(table_is_blank(), 'table is blank after initial draw');
});

QUnit.test("Changing constraints changes table", function(assert) {
    function table_constraints() {
        return $("td.constraint").map(function() {
            return $(this).html();
        }).get();
    }

    function inArray(elem, arr) {
        return $.inArray(elem, arr) !== -1;
    }

    $("#apriori-tab").click();
    var cons = table_constraints();
    assert.ok(inArray('a', cons), "has 'a' before modification");
    assert.ok(inArray('b', cons), "has 'b' before modification");
    assert.ok(inArray('c', cons), "has 'c' before modification");

    $("th.constraint:eq(0)").find("input").val("d");
    $("#apriori-tab").click();

    cons = table_constraints();
    assert.ok(inArray('d', cons), "has 'd' after modification");
    assert.ok(inArray('b', cons), "has 'b' after modification");
    assert.ok(inArray('c', cons), "has 'c' after modification");
    assert.ok(table_is_blank(), 'table is blank after redraw');
});

QUnit.test("Loading page with a ranking", function(assert) {
    $("#apriori_ranking").val('[["a", "b"], ["a", "c"]]');
    $("#apriori-tab").click();
    assert.ok(is_checked('a', 'b'), "table has relation a >> b");
    assert.ok(is_checked('a', 'c'), "table has relation a >> c");
    assert.equal($("#apriori_table td.checked").length, 2,
                 "only two cells checked");
    assert.equal($("#apriori_table td.deactivated").length, 5,
                 "diagonal and inverse deactive");
});

function is_checked(row, col) {
    var $row = $("#apriori_table tr#row_" + row);
    var $cell = $row.find("td[name=" + col + "]");
    return $cell.hasClass('checked');
}

function table_is_blank() {
    var num_constraints = $("td.constraint").length;
    var num_deactivated = $("td.deactivated").length;
    var num_checked = $("td.checked").length;
    return (num_constraints / 2 === num_deactivated) && (num_checked == 0);
}
})(this, this.document);
