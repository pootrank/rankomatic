'use strict';
//QUnit.module("TestBasic");

//QUnit.test("true is true", function(assert) {
    //assert.ok(true, "true is still true");
//})

describe("a passing suite", function() {
    it('contains a spec with a single expectation', function() {
        expect(true).toBe(true);
    });
});
