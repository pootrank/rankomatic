(function() {
  'use strict';

  describe('module: models', function() {

    beforeEach(module('app.models'));
    beforeEach(function() {
      module(function($provide) {
        $provide.value('InputGroup', function(init) {
          return {input: '', init: init};
        });
      });
    });

    describe('factory: Dataset', function() {
      var Dataset;

      beforeEach(inject(function(_Dataset_) {
        Dataset = _Dataset_;
      }));

      it('should be able to inject Dataset', function() {
        expect(Dataset).toBeDefined();
      });

      it('should create blank Dataset when called with no arguments', function() {
        var dset = new Dataset();
        expect(dset.name).toBe('');
        expect(dset.constraints).toEqual(['', '', '']);
        expect(dset.input_groups).toEqual([{input: '', init: 3}]);
      });

      it('should set name and constraints based on first two arguments, input_groups based on length of second', function() {
        var dset = new Dataset('NAME', ['C1', 'C2', 'C3', 'C4']);
        expect(dset.name).toBe('NAME');
        expect(dset.constraints).toEqual(['C1', 'C2', 'C3', 'C4']);
        expect(dset.input_groups).toEqual([{input: '', init: 4}]);
      });

      it('should set input_groups by calling InputGroup on each element in input_groups arg', function() {
        var dset = new Dataset('name', ['A', 'B', 'C'], [1, 2, 3]);
        expect(dset.name).toBe('name');
        expect(dset.constraints).toEqual(['A', 'B', 'C']);
        expect(dset.input_groups).toEqual([
          {input: '', init: 1},
          {input: '', init: 2},
          {input: '', init: 3},
        ]);
      });

      describe('class method: get_from_url', function() {
        var $httpBackend, $rootScope;

        beforeEach(inject(function(_$httpBackend_, _$rootScope_) {
          $httpBackend = _$httpBackend_;
          $rootScope = _$rootScope_;
        }));

        it('should return a blank dataset, without hitting server, when called with /calculator/ url', function() {
          var dset;
          Dataset.get_from_url('/calculator/')
            .then(function(response) {
              dset = response.data;
            });
          $rootScope.$digest();  // make sure promise is resolved
          expect(dset).toEqual(new Dataset());
        });

        it('should hit server and return the asked-for dataset when called with the edit url', function() {
          var dset;
          $httpBackend.expectGET('/dset.json').respond({
            name: 'dset',
            constraints: ['A', 'B', 'C'],
            input_groups: [1, 2, 3]
          });
          Dataset.get_from_url('/dset/edit/').then(function(response) {
            dset = response.data;
          });
          $httpBackend.flush();
          expect(dset).toEqual(new Dataset('dset', ['A', 'B', 'C'], [1,2,3]));
        });
      });
    });
  });
})();
