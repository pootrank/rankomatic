QUnit.module("TransitiveSet", {
    beforeEach: function() {
        this.tset = new TransitiveSet();
    }
});

QUnit.test('constructor', function(assert) {
    assert.ok(this.tset, "constructor makes something");
    assert.deepEqual(this.tset.relations, {},
                     "bare constructor should make no relations");
});

QUnit.test('keyExists', function(assert) {
    assert.ok(!this.tset.keyExists("a"), "no keys yet");
    this.tset.relations['b'] = {'a': true};
    assert.ok(this.tset.keyExists('b'), "b should be there now");
});

QUnit.test('contains', function(assert) {
    assert.ok(!this.tset.contains("a", "b'"));
    this.tset.relations['a'] = {'b': true};
    assert.ok(this.tset.contains('a', 'b'));
});

QUnit.test('forEach', function(assert) {
    objs = [];
    this.tset.forEach(function(a, b) {
        objs.push(a);
        objs.push(b);
    });
    assert.deepEqual(objs, []);
    this.tset.relations = {
        a: {b: true, c: true},
        b: {c: true}
    };
    this.tset.forEach(function(a, b) {
        objs.push(a);
        objs.push(b);
    });
    assert.deepEqual(objs.sort(), ['a', 'a', 'b', 'b', 'c', 'c']);
});

QUnit.test('to_array', function(assert) {
    assert.deepEqual(this.tset.to_array(), [], "should be nothing here");
    this.tset.relations = {
        a: {b: true, c: true},
        b: {c: true}
    };
    assert.deepEqual(this.tset.to_array(),
                     [['a', 'b'], ['a', 'c'], ['b', 'c']],
                    "basic list/set representations");
});

QUnit.test('add', function(assert) {
    this.tset.add('a', 'b');
    assert.ok(this.tset.contains('a', 'b'), "one member")
    this.tset.add('a', 'd');
    assert.ok(this.tset.contains('a', 'd'),
              'two members');
    this.tset.add('b', 'c');
    assert.deepEqual(this.tset.to_array(),
                     [['a', 'b'], ['a', 'd'], ['a', 'c'], ['b', 'c']],
                     "closed under transitivity");
    assert.throws(function() {this.tset.add("a") },
                  /must have two arguments/,
                 "only one argument throws error");
});

QUnit.test('remove', function(assert) {
    assert.equal(this.tset.remove('a', 'b'), false,
                 "removing nothing gives false");
    this.tset.add('a', 'b');
    this.tset.add('b', 'c');
    this.tset.add('a', 'd');
    assert.deepEqual(this.tset.remove('a', 'd'), ['a', 'd'],
                    "removing returns the relation returned");
    assert.ok(!this.tset.contains('a', 'd'), "shouldn't have removed relation");
    assert.ok(!this.tset.remove('a', 'c'),
                     "cannot remove transitiviely surrounded relation");
    assert.ok(this.tset.contains('a', 'c'),
              "transitively surrounded relation remains")
});
