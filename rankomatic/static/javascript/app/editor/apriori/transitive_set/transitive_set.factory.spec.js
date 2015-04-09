(function() {
  'use strict';

  describe('module: app.editor.apriori', function() {

    beforeEach(module('app.editor.apriori'));
    describe(', factory: TransitiveSet', function() {
      var TransitiveSet;

      beforeEach(inject(function(_TransitiveSet_) {
        TransitiveSet = _TransitiveSet_;
      }));

      it('should be able to load TransitiveSet', function() {
        expect(TransitiveSet).toBeDefined();
      });

      describe('-- constructor', function() {

        it('should create an empty set when called with no args', function() {
          var tset = new TransitiveSet();
          expect(tset.to_array()).toEqual([]);
        });

        it('should put all the relations in a given ranking', function() {
          var orig = [['a', 'b'], ['a', 'c']];
          var tset = new TransitiveSet(orig);
          expect(tset.to_array()).toEqual(orig);
        });

        it('should be closed under transitivity', function() {
          var orig = [['a', 'b'], ['b', 'c']];
          var tset = new TransitiveSet(orig);
          expect(tset.to_array()).toEqual([['a', 'b'], ['a', 'c'], ['b', 'c']])
        });
      });

      describe('-- forEach', function() {

        it('should call the callback on every relation in the set', function() {
          var tset = new TransitiveSet([['a', 'b'], ['a', 'c'], ['b', 'c']]);
          var fun = jasmine.createSpy();
          tset.forEach(fun);
          expect(fun).toHaveBeenCalledWith('a', 'b');
          expect(fun).toHaveBeenCalledWith('a', 'c');
          expect(fun).toHaveBeenCalledWith('b', 'c');
        });
      });

      describe('-- to_array', function() {

        it('should return an array of length two arrays with the relations', function() {
          var orig = [['a', 'b'], ['a', 'c'], ['b', 'c']];
          var tset = new TransitiveSet(orig);
          expect(tset.to_array()).toEqual(orig);
        });
      });

      describe('-- contains', function() {

        beforeEach(function() {
          this.orig = [['a', 'b'], ['a', 'c'], ['b', 'c']];
          this.tset = new TransitiveSet(this.orig);
        });

        it('should return true if the given relation is in the set', function() {
          var tset = this.tset;
          this.orig.forEach(function(elem) {
            expect(tset.contains(elem[0], elem[1])).toBe(true);
          });
        });

        it('should return false if the given relation is not in the set', function() {
          var not_in = [['b', 'a'], ['c', 'a'], ['d', 'x']];
          var tset = this.tset;
          not_in.forEach(function(elem) {
            expect(tset.contains(elem[0], elem[1])).toBe(false);
          });
        });
      });

      describe('-- add', function() {

        beforeEach(function() {
          this.tset = new TransitiveSet();
        });

        it('should successfully add a relation to the set', function() {
          expect(this.tset.contains('a', 'b')).toBe(false);
          var success = this.tset.add('a', 'b');
          expect(this.tset.contains('a', 'b')).toBe(true);
          expect(success).toBe(true);
        });

        it('should add a relation and close it under transitivity', function() {
          this.tset.add('a', 'b');
          expect(this.tset.contains('a', 'c')).toBe(false);
          var success = this.tset.add('b', 'c');
          expect(this.tset.contains('a', 'c')).toBe(true);
          expect(success).toBe(true);
        });

        it('should not add a relation that is itself', function() {
          var success = this.tset.add('a', 'a');
          expect(this.tset.contains('a', 'a')).toBe(false);
          expect(success).toBe(false);
        });
      });

      describe('-- remove', function() {

        beforeEach(function() {
          this.tset = new TransitiveSet([['a', 'b'], ['a', 'c'], ['b', 'c']]);
        });

        it('should remove a non-trasitively required relation', function() {
          expect(this.tset.contains('a', 'b')).toBe(true);
          var successfully_removed = this.tset.remove('a', 'b');
          expect(this.tset.contains('a', 'b')).toBe(false);
          expect(successfully_removed).toBe(true);
        });

        it('should not remove a transitively required relation', function() {
          expect(this.tset.contains('a', 'c')).toBe(true);
          var successfully_removed = this.tset.remove('a', 'c');
          expect(this.tset.contains('a', 'c')).toBe(true);
          expect(successfully_removed).toBe(false);
        });
      });

      describe('-- cannot_add', function() {

        beforeEach(function() {
          this.tset = new TransitiveSet([['a', 'b'], ['a', 'c'], ['b', 'c']]);
        });

        it('should return true if the elements are the same', function() {
          expect(this.tset.cannot_add('a', 'a')).toBe(true);
        });

        it('should return true if the inverse is contained', function() {
          expect(this.tset.cannot_add('b', 'a')).toBe(true);
        });

        it('should return false if the relation can be added', function() {
          expect(this.tset.cannot_add('b', 'd')).toBe(false);
        })
      });
    });
  });
})();
