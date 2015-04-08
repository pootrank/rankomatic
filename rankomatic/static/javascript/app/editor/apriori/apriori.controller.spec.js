(function() {
  'use strict';

  describe('module: app.editor.apriori', function() {

    beforeEach(module('app.editor.apriori'));
    //beforeEach(function() {
      //module(function($provide) {
        ////$provide.factory('TransitiveSet', function() {
          ////return jasmine.createSpy('TransitiveSet').and.callFake(function() {
            ////return {
              ////contains: jasmine.createSpy('TransitiveSet.contains'),
              ////remove: jasmine.createSpy('TransitiveSet.remove'),
              ////add: jasmine.createSpy('TransitiveSet.add')
            ////}
          ////});
        //});
      //});
    //});

    describe('-- controller: AprioriController', function() {
      var $controller, $rootScope;

      beforeEach(inject(function(_$controller_, _$rootScope_) {
        $controller = _$controller_;
        $rootScope = _$rootScope_;
        $rootScope.editor = {
          dset: {
            constraints: ['a', 'b', 'c'],
            apriori_ranking: []
          }
        }
      }));

      it('should be defined after being loaded', function() {
        var ctrl = $controller('AprioriController', {$scope: $rootScope.$new()});
        expect(ctrl).toBeDefined();
        expect(ctrl.dset).toBeDefined();
        expect(ctrl.ranking).toBeDefined();
      });

      it('should load the new dset when dset_loaded is fired', function() {
        var ctrl = $controller('AprioriController',
                               {$scope: $rootScope.$new()});
        expect(ctrl.dset.apriori_ranking).toEqual([]);
        var new_ranking = [['a', 'b']];
        $rootScope.editor.dset.apriori_ranking = new_ranking;
        $rootScope.$broadcast('dset_loaded');
        $rootScope.$digest();
        expect(ctrl.dset.apriori_ranking).toEqual(new_ranking);
      });

      describe('-- methods', function() {

        beforeEach(function() {
          this.ctrl = $controller('AprioriController',
                                  {$scope: $rootScope.$new()});

          this.check_ranking = function(reln, contains, arr, trans) {
            expect(this.ctrl.ranking.contains(reln[0], reln[1])).toBe(contains);
            expect(this.ctrl.dset.apriori_ranking).toEqual(arr);
            expect(this.ctrl.transitively_required).toBe(trans);
          }
        });

        describe('-- add_or_remove', function() {

          it("should add a new relation if it doesn't exist yet", function() {
            this.ctrl.add_or_remove('a', 'b');
            this.check_ranking(['a', 'b'], true, [['a', 'b']], false);
          });

          it('should not be able to add the inverse of a relation', function() {
            this.ctrl.add_or_remove('a', 'b');
            this.ctrl.add_or_remove('b', 'a');
            this.check_ranking(['b', 'a'], false, [['a', 'b']], true);
          });

          it('should remove a relation that is in the ranking', function() {
            this.ctrl.add_or_remove('a', 'b');
            expect(this.ctrl.ranking.contains('a', 'b')).toBe(true);
            this.ctrl.add_or_remove('a', 'b');
            this.check_ranking(['a', 'b'], false, [], false);
          });

          it('should not remove a ranking that is transitively required', function() {
            this.ctrl.add_or_remove('a', 'b');
            this.ctrl.add_or_remove('b', 'c');
            expect(this.ctrl.ranking.contains('a', 'c')).toBe(true);
            this.ctrl.add_or_remove('a', 'c');
            this.check_ranking(['a', 'c'], true,
                               [['a', 'b'], ['a', 'c'], ['b', 'c']], true);
          });
        });

        describe('-- clear_ranking', function() {

          it('should make the ranking blank', function() {
            this.ctrl.add_or_remove('a', 'b');
            this.ctrl.add_or_remove('b', 'c');
            this.check_ranking(['a', 'c'], true,
                               [['a', 'b'], ['a', 'c'], ['b', 'c']], false);
            this.ctrl.clear_ranking();
            expect(this.ctrl.ranking.to_array()).toEqual([]);
            expect(this.ctrl.dset.apriori_ranking).toEqual([]);
            expect(this.ctrl.transitively_required).toBe(false);
          });
        });
      });
    });
  });
})();
