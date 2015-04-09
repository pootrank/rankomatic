'use strict';

var load_html = function() {
    var f = jasmine.getFixtures();
    f.fixturesPath = 'base/test/qunit';
    f.load('test.html');
}

var remove_html = function() {
    var f = jasmine.getFixtures();
    f.cleanUp();
    f.clearCache();
}
