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

      it('should set name and constraints based on first two arguments, '+
         'input_groups based on length of second', function() {
        var dset = new Dataset('NAME', ['C1', 'C2', 'C3', 'C4']);
        expect(dset.name).toBe('NAME');
        expect(dset.constraints).toEqual(['C1', 'C2', 'C3', 'C4']);
        expect(dset.input_groups).toEqual([{input: '', init: 4}]);
      });

      it('should set input_groups by calling InputGroup on each element in '+
         'input_groups arg', function() {
        var dset = new Dataset('name', ['A', 'B', 'C'], [1, 2, 3]);
        expect(dset.name).toBe('name');
        expect(dset.constraints).toEqual(['A', 'B', 'C']);
        expect(dset.input_groups).toEqual([
          {input: '', init: 1},
          {input: '', init: 2},
          {input: '', init: 3},
        ]);
      });

      describe('http methods --', function() {
        var $httpBackend, $rootScope;

        beforeEach(inject(function(_$httpBackend_, _$rootScope_) {
          $httpBackend = _$httpBackend_;
          $rootScope = _$rootScope_;
        }));

        describe('get', function() {
          beforeEach(function() {
            $httpBackend.whenGET('/dset.json')
            .respond({
              name: 'dset',
              constraints: ['A', 'B', 'C'],
              input_groups: [1, 2, 3],
              apriori_ranking: '[["A", "B"]]'
            });
          });

          it('should hit server and return the asked-for dataset when called ' +
             'with the name of a dataset', function() {
            var dset;
            $httpBackend.expectGET('/dset.json');
            Dataset.get('dset').then(function(data) {
              dset = data;
            });
            $httpBackend.flush();
            expect(dset).toEqual(new Dataset('dset',
                                             ['A', 'B', 'C'],
                                             [1,2,3],
                                             [['A', 'B']]
                                            ));
          });
        });

        describe('save', function() {
          beforeEach(function() {
            $httpBackend.whenPOST('/save_dset/')
              .respond(function(method, url, data) {
                return [200, data, {}];
              });
          });

          it('should hit server and respond that resource was successfully saved', function() {
            var dset = new Dataset('dset', ['A', 'B', 'C'],
                                   [1, 2, 3], [['A', 'B']]);
            $httpBackend.expectPOST('/save_dset/');
            dset.save().then(function(data) {
              expect(data.status).toBe(200);
            });
            $httpBackend.flush();
          });
        });

        describe('delete', function() {
          beforeEach(function() {
            $httpBackend.whenGET('/delete/dset')
              .respond(function(method, url, data) {
                return [200, 'dset deleted ok', {}];
              });
          });

          it('should hit delete url with dset name', function() {
            var dset = new Dataset('dset', ['a', 'b', 'c'], [1, 2, 3]);
            $httpBackend.expectGET('/delete/dset');
            dset.del().then(function(data) {
              expect(data.status).toBe(200);
            });
            $httpBackend.flush();
          });
        });
      });
    });
  });
})();
