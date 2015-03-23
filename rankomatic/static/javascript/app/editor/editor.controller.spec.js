(function() {
  'use strict';

  describe('module: app.editor', function() {

    beforeEach(module('app.editor'));
    beforeEach(function() {
      module(function($provide) {
        $provide.factory('Dataset', function() {
          return jasmine.createSpy('Dataset');
        });
      });
    });

    describe('controller: EditorController', function() {
      var $controller, $location, $rootScope, Dataset;

      beforeEach(inject(
        function(_$controller_, _$location_, _$rootScope_, _Dataset_, $q) {
        $controller = _$controller_;
        $location = _$location_;
        $rootScope = _$rootScope_;
        Dataset = _Dataset_;
        this.scope = $rootScope.$new();

        var promise = $q(function(resolve) {
          resolve('dataset');
        });
        Dataset.get = jasmine.createSpy('Dataset.get').and.returnValue(promise);

        spyOn($rootScope, '$broadcast').and.returnValue({});
      }));

      it('should be defined after being loaded', function() {
        var ctrl = $controller('EditorController', {$scope: this.scope});
        expect(ctrl).toBeDefined();
      });

      it('should set blank dset for url /calculator/', function() {
        spyOn($location, 'absUrl').and.returnValue('/calculator/');
        var ctrl = $controller('EditorController', {$scope: this.scope});
        expect(Dataset).toHaveBeenCalled();
        expect($rootScope.$broadcast).toHaveBeenCalledWith('dset_loaded');
      });

      it('should call get for url /dset_name/edit/', function() {
        spyOn($location, 'absUrl').and.returnValue('/dset_name/edit/');
        var ctrl = $controller('EditorController', {$scope: this.scope});
        $rootScope.$digest();
        expect(Dataset.get).toHaveBeenCalledWith('dset_name');
        expect(ctrl.dset).toBe('dataset');
        expect($rootScope.$broadcast).toHaveBeenCalledWith('dset_loaded');
      });
    });
  });
})();
