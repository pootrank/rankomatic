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
      var $controller, $location, $rootScope, Dataset, $timeout, http_success;

      beforeEach(inject(
        function(_$controller_, _$location_, _$rootScope_, _Dataset_, _$timeout_, $q) {
        $controller = _$controller_;
        $location = _$location_;
        $rootScope = _$rootScope_;
        $timeout = _$timeout_
        Dataset = _Dataset_;
        this.scope = $rootScope.$new();

        function http_promise(success) {
          var deferred = $q.defer();
          if (success) {
            deferred.resolve('success');
          } else {
            deferred.reject('error');
          }
          return deferred.promise;
        }

        this.init_response = function(success) {
          var promise = $q(function(resolve) {
            resolve({
              name: 'dset',
              save: jasmine.createSpy('dset.save')
                .and.returnValue(http_promise(success)),
              del: jasmine.createSpy('dset.del')
                .and.returnValue(http_promise(success)),
            });
          });
          Dataset.get = jasmine.createSpy('Dataset.get')
            .and.returnValue(promise);
        }

        this.init_response(true);
        spyOn($rootScope, '$broadcast').and.returnValue({});
      }));

      it('should be defined after being loaded', function() {
        var ctrl = $controller('EditorController', {$scope: this.scope});
        expect(ctrl).toBeDefined();
      });

      it('should set blank dset for url /calculator/', function() {
        spyOn($location, 'absUrl').and.returnValue('/calculator/');
        var ctrl = $controller('EditorController', {$scope: this.scope});
        $timeout.flush();
        expect(Dataset).toHaveBeenCalled();
        expect($rootScope.$broadcast).toHaveBeenCalledWith('dset_loaded');
      });

      it('should call get for url /dset_name/edit/', function() {
        spyOn($location, 'absUrl').and.returnValue('/dset_name/edit/');
        var ctrl = $controller('EditorController', {$scope: this.scope});
        $rootScope.$digest();
        expect(Dataset.get).toHaveBeenCalledWith('dset_name');
        expect(ctrl.dset.name).toBe('dset');
        expect($rootScope.$broadcast).toHaveBeenCalledWith('dset_loaded');
      });

      describe('-- methods --', function() {

        beforeEach(function() {
          spyOn($location, 'absUrl').and.returnValue('/dset/edit');
          this.init_successful_response = function() {
            this.init_response(true);
            this.ctrl = $controller('EditorController', {$scope: this.scope});
            $rootScope.$digest();
          }
          this.init_error_response = function() {
            this.init_response(false);
            this.ctrl = $controller('EditorController', {$scope: this.scope});
            $rootScope.$digest();
          }
          this.build_controller = function(success) {
            this.init_response(success);
            this.ctrl = $controller('EditorController', {$scope: this.scope});
            $rootScope.$digest();
          }
        });

        describe('save_dset', function() {

          it('should append a message to the messages list when successful', function() {
            this.build_controller(true);
            var len = this.ctrl.messages.length;
            this.ctrl.save_dset();
            $rootScope.$digest();
            expect(this.ctrl.messages.length).toBe(len + 1);
          });

          it('should only add one copy of the message', function() {
            this.build_controller(true);
            var len = this.ctrl.messages.length;
            this.ctrl.save_dset();
            $rootScope.$digest();
            this.ctrl.save_dset();
            $rootScope.$digest();
            expect(this.ctrl.messages.length).toBe(len + 1);
          });

          it('should append a message to the errors list when unsuccessful', function() {
            this.build_controller(false);
            var len = this.ctrl.errors.length;
            this.ctrl.save_dset();
            $rootScope.$digest();
            expect(this.ctrl.errors.length).toBe(len + 1);
          });

          it('should only add one message to the errors list', function() {
            this.build_controller(false);
            var len = this.ctrl.errors.length;
            this.ctrl.save_dset();
            $rootScope.$digest();
            this.ctrl.save_dset();
            $rootScope.$digest();
            expect(this.ctrl.errors.length).toBe(len + 1);
          });
        });

        describe('delete_dset', function() {

          it('should append a meessage to the messsages list when successful', function() {
            this.build_controller(true);
            var len = this.ctrl.messages.length;
            this.ctrl.delete_dset();
            $rootScope.$digest();
            expect(this.ctrl.messages.length).toBe(len + 1);
          });

          it('should append a message to the errors list when unsuccessful', function() {
            this.build_controller(false);
            var len = this.ctrl.errors.length;
            this.ctrl.delete_dset();
            $rootScope.$digest();
            expect(this.ctrl.errors.length).toBe(len + 1);
          });
        });

        describe('remove_error', function() {

          it('should remove the given error from the errors list', function() {
            var err = 'ERROR';
            var err2 = 'ANOTHER ERROR';
            this.build_controller(false);
            this.ctrl.errors.push(err, err2);
            expect(this.ctrl.errors.length).toBe(2);
            this.ctrl.remove_error(err);
            expect(this.ctrl.errors.length).toBe(1);
            expect(this.ctrl.errors).toEqual([err2]);
            this.ctrl.remove_error(err2);
            expect(this.ctrl.errors.length).toBe(0);
          });
        });

        describe('remove_message', function() {

          it('should remove the given error from the errors list', function() {
            var msg = 'MESSAGE';
            var msg2 = 'ANOTHER MESSAGE';
            this.build_controller(false);
            this.ctrl.messages.push(msg, msg2);
            expect(this.ctrl.messages.length).toBe(2);
            this.ctrl.remove_message(msg);
            expect(this.ctrl.messages.length).toBe(1);
            expect(this.ctrl.messages).toEqual([msg2]);
            this.ctrl.remove_message(msg2);
            expect(this.ctrl.messages.length).toBe(0);
          });
        });

        describe('grammar_url', function() {

          it('should return the correct url', function() {
            this.build_controller(true);
            expect(this.ctrl.grammar_url()).toBe('/dset/grammars/0');
          });
        });

        describe('entailment_url', function() {

          it('should return the correct url', function() {
            this.build_controller(true);
            expect(this.ctrl.entailment_url()).toBe('/dset/entailments');
          });
        });
      });
    });
  });
})();
