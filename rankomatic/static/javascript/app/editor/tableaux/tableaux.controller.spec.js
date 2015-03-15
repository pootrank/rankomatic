(function() {
  'use strict';

  describe('module: app.editor.tableaux', function() {

    beforeEach(module('app.editor.tableaux'));
    beforeEach(function() {
      module(function($provide) {
        $provide.factory('Dataset', function() {
          return jasmine.createSpy('Dataset').and.callFake(function() {
            return {
              name: 'name',
              constraints: ['a', 'b', 'c'],
              input_groups: [
                {
                  candidates: [
                    {
                      violation_vector: [1, 2, 3]
                    },
                    {
                      violation_vector: [1, 2, 3]
                    },
                  ]
                },
                {
                  candidates: [
                    {
                      violation_vector: [1, 2, 3]
                    },
                    {
                      violation_vector: [1, 2, 3]
                    },
                  ]
                }
              ]
            };
          });
        });
        $provide.factory('InputGroup', function() {
          return jasmine.createSpy('InputGroup').and.callFake(function() {
            return {
              candidates: [
                {
                  violation_vector: [0,0,0]
                }
              ]
            };
          });
        });
      });
    });

    describe('controller: TableauxController', function() {
      var $controller, $location, $rootScope, Dataset, url;

      beforeEach(inject(function(_$controller_, _$location_, _$rootScope_,
                                _Dataset_, $q) {
        $location = _$location_;
        $controller = _$controller_;
        $rootScope = _$rootScope_;
        Dataset = _Dataset_;
        spyOn($rootScope, '$broadcast').and.returnValue({});
        var promise = $q(function(resolve) {
          resolve('dataset');
        });
        Dataset.get = jasmine.createSpy('Dataset.get')
          .and.returnValue(promise);
      }));

      it('should be defined when loaded', function() {
        var ctrl = $controller('TableauxController');
        expect(ctrl).toBeDefined();
      });

      it('should set blank dset for url /calculator/', function() {
        spyOn($location, 'absUrl').and.returnValue('/calculator/');
        var ctrl = $controller('TableauxController');
        expect(Dataset).toHaveBeenCalled();
        expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
      });

      it('should call get for url /dset_name/edit/', function() {
        spyOn($location, 'absUrl').and.returnValue('/dset_name/edit/');
        var ctrl = $controller('TableauxController');
        $rootScope.$digest();
        expect(Dataset.get).toHaveBeenCalledWith('dset_name');
        expect(ctrl.dset).toBe('dataset');
        expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
      })

      describe('methods', function() {
        var ctrl, vvec;


        beforeEach(function() {
          spyOn($location, 'absUrl').and.returnValue('/calculator/');
          ctrl = $controller('TableauxController');
          this.vvec = function() {
            return ctrl.dset.input_groups[0].candidates[0].violation_vector;
          }
          this.correctly_add_constraint = function(index, old_len) {
            var vvec = this.vvec();
            expect(ctrl.dset.constraints.length).toBe(old_len + 1);
            expect(ctrl.dset.constraints[index]).toBe("");
            expect(vvec.length).toBe(ctrl.dset.constraints.length);
            expect(vvec[index]).toBe('');
          }
        });

        describe('input_class', function() {
          it('should return first-input if the given candidate is the first '+
             'element in the given input group, and not-first-input otherwise',
             function() {
            var ig = {candidates: [1, 2, 3, 4]};
            expect(ctrl.input_class(ig, 1)).toBe('first-input');
            expect(ctrl.input_class(ig, 2)).toBe('not-first-input');
            expect(ctrl.input_class(ig, 3)).toBe('not-first-input');
            expect(ctrl.input_class(ig, 4)).toBe('not-first-input');
          });
        });

        describe('add_constraint_left', function() {
          it('should add a constraint to the left of the given index', function() {
            var old_num_constraints = ctrl.dset.constraints.length;
            var vvec = this.vvec();
            expect(vvec.length).toBe(old_num_constraints);

            ctrl.add_constraint_left(0);
            this.correctly_add_constraint(0, old_num_constraints);
            ctrl.add_constraint_left(3);
            this.correctly_add_constraint(3, old_num_constraints + 1);
          });

          it('should not add more than the max number of constraints', function() {
            for (var num = this.vvec().length; num <= ctrl.MAX_NUM_CONSTRAINTS; ++num) {
              ctrl.add_constraint_left(0);
            }
            expect(ctrl.dset.constraints.length).toBe(ctrl.MAX_NUM_CONSTRAINTS);
            ctrl.add_constraint_left(0);
            expect(ctrl.dset.constraints.length).toBe(ctrl.MAX_NUM_CONSTRAINTS);
          });
        });

        describe('add_constraint_right', function() {
          it('should add a constraint to the right of the given index', function() {
            var old_num_constraints = ctrl.dset.constraints.length;
            var vvec = this.vvec();
            expect(vvec.length).toBe(old_num_constraints);

            ctrl.add_constraint_right(0);
            this.correctly_add_constraint(1, old_num_constraints);
            ctrl.add_constraint_right(2);
            this.correctly_add_constraint(3, old_num_constraints + 1);
          });

          it('should not add more than the max number of constraints', function() {
            for (var num = this.vvec().length; num <= ctrl.MAX_NUM_CONSTRAINTS; ++num) {
              ctrl.add_constraint_right(0);
            }
            expect(this.vvec().length).toBe(ctrl.MAX_NUM_CONSTRAINTS);
            ctrl.add_constraint_right(0);
            expect(this.vvec().length).toBe(ctrl.MAX_NUM_CONSTRAINTS);
          });
        });

        describe('delete_constraint', function() {
          it('should delete the constraint at the given index', function() {
            var old_num_constraints = ctrl.dset.constraints.length;
            var vvec = this.vvec();

            ctrl.delete_constraint(0);
            expect(vvec.length).toBe(old_num_constraints - 1);
            expect(ctrl.dset.constraints.length).toBe(vvec.length);
            expect(ctrl.dset.constraints[0]).toBe('b');

            ctrl.delete_constraint(1);
            expect(vvec.length).toBe(old_num_constraints - 2);
            expect(ctrl.dset.constraints.length).toBe(vvec.length);
            expect(ctrl.dset.constraints[0]).toBe('b');
          });

          it('should not delete more than the min number of constraints', function() {
            var vvec = this.vvec();
            for (var i = vvec.length; i >= ctrl.MIN_NUM_CONSTRAINTS; --i) {
              ctrl.delete_constraint(0);
            }
            expect(vvec.length).toBe(ctrl.MIN_NUM_CONSTRAINTS);
            expect(ctrl.dset.constraints.length).toBe(vvec.length);

            ctrl.delete_constraint(0);
            expect(vvec.length).toBe(ctrl.MIN_NUM_CONSTRAINTS);
            expect(ctrl.dset.constraints.length).toBe(vvec.length);
          });
        });

        describe('add_input_group_above', function() {

          it('should add an input group above the given index', function() {
            expect(true).toBe(false);
          });
        });
      });
    });
  });
})();
