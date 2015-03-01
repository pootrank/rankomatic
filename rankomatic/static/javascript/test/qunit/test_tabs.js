QUnit.module("TabList", {
    beforeEach: function() {
        load_html();
        this.tablist = new TabList($("#tab-list"));
    },
    afterEach: function() {
        remove_html();
    }
});

QUnit.test("constructor", function(assert) {
    assert.ok(this.tablist, "constructor makes something");
});

QUnit.test("before_click", function(assert) {
    assert.ok(is_active("tab-first"), "first tab is active");
    assert.ok(is_hidden("tab-second"), "second tab is hidden");
    assert.ok(is_hidden("tab-third"), "third tab is hidden");
});

QUnit.test("click", function(assert) {
    $('#tab-second').trigger('click');
    assert.ok(is_hidden("tab-first"), "first tab is hidden");
    assert.ok(is_active("tab-second"), "second tab is active");
    assert.ok(is_hidden("tab-third"), "third tab is hidden");
});

QUnit.test("click twice", function(assert) {
    $('#tab-second').trigger('click');
    $('#tab-third').trigger('click');
    assert.ok(is_hidden("tab-first"), "first tab is hidden");
    assert.ok(is_hidden("tab-second"), "second tab is hidden");
    assert.ok(is_active("tab-third"), "third tab is active");
})

function get_tab_selectors(tabname) {
    return {
        tab: "#" + tabname,
        content: "." + tabname + "-content"
    }
}
function is_active(tabname) {
    sels = get_tab_selectors(tabname);
    return ($(sels.tab).hasClass("active") &&
            $(sels.content).is(":visible"))
}

function is_hidden(tabname) {
    sels = get_tab_selectors(tabname);
    return (!$(sels.tab).hasClass("active") &&
            $(sels.content).is(":hidden"))
}
