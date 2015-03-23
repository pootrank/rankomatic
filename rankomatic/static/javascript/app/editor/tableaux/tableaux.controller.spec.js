(function() {
  'use strict';

  describe('module: app.editor.tableaux', function() {

    beforeEach(module('app.editor.tableaux'));
    beforeEach(function() {
      module(function($provide) {
        $provide.factory('InputGroup', function() {
          return jasmine.createSpy('InputGroup').and.callFake(function() {
            return {
              input: "",
              add_candidate: jasmine.createSpy('input_group.add_candidate'),
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
      var $controller, $location, $rootScope, url, InputGroup;

      beforeEach(inject(function(_$controller_, _$location_, _$rootScope_, $q) {
        $location = _$location_;
        $controller = _$controller_;
        $rootScope = _$rootScope_;
        spyOn($rootScope, '$broadcast').and.callThrough();
        var promise = $q(function(resolve) {
          resolve('dataset');
        });

        $rootScope.editor = {
          dset: {
            name: 'name',
            constraints: ['a', 'b', 'c'],
            input_groups: [
              {
              input: 'i1',
              add_candidate: jasmine.createSpy(),
              candidates: [
                {
                output: 'o1',
                violation_vector: [1, 2, 3]
              },
              {
                output: 'o2',
                violation_vector: [1, 2, 3]
              },
              ]
            },
            {
              input: 'i2',
              add_candidate: jasmine.createSpy(),
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
          }
        }
      }));

      it('should be defined when loaded', function() {
        var scope = $rootScope.$new();
        var ctrl = $controller('TableauxController', {$scope: scope});
        expect(ctrl).toBeDefined();
      });

      describe('methods', function() {
        var ctrl, vvec;

        beforeEach(function() {
          spyOn($location, 'absUrl').and.returnValue('/calculator/');
          ctrl = $controller('TableauxController', {$scope: $rootScope.$new()});
          $rootScope.$broadcast('dset_loaded');
          $rootScope.$digest();
          this.vvec = function() {
            return ctrl.dset.input_groups[0].candidates[0].violation_vector;
          }
          this.correctly_add_constraint = function(index, old_len) {
            var vvec = this.vvec();
            expect(ctrl.dset.constraints.length).toBe(old_len + 1);
            expect(ctrl.dset.constraints[index]).toBe("");
            expect(vvec.length).toBe(ctrl.dset.constraints.length);
            expect(vvec[index]).toBe('');
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          }

          this.correctly_add_input_group = function(index, old_len) {
            expect(ctrl.dset.input_groups.length).toBe(old_len + 1);
            expect(ctrl.dset.input_groups[index].input).toBe("");
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
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
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
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
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
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          });
        });

        describe('add_input_group_above', function() {

          it('should add an input group above the given input group', function() {
            var old_num_input_groups = ctrl.dset.input_groups.length;
            var ig = ctrl.dset.input_groups[0];
            ctrl.add_input_group_above(ig);
            this.correctly_add_input_group(0, old_num_input_groups);
            ctrl.add_input_group_above(ig);
            this.correctly_add_input_group(1, old_num_input_groups+1);
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          });
        });

        describe('add_input_group_below', function() {

          it('should add an input group below the given input group', function() {
            var old_num_input_groups = ctrl.dset.input_groups.length;
            var ig = ctrl.dset.input_groups[0];
            ctrl.add_input_group_below(ig);
            this.correctly_add_input_group(1, old_num_input_groups);
            ctrl.add_input_group_below(ig);
            this.correctly_add_input_group(1, old_num_input_groups+1);
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          });
        });

        describe('delete_input_group', function() {

          it('should delete the given input group', function() {
            var old_num_input_groups = ctrl.dset.input_groups.length;
            var ig = ctrl.dset.input_groups[0];
            var old_input = ig.input;
            ctrl.delete_input_group(ig);
            expect(ctrl.dset.input_groups.length).toBe(old_num_input_groups - 1);
            expect(ctrl.dset.input_groups[0].input).not.toBe(old_input);
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          });

          it('should delete no more than the minimum number of input groups', function() {
            var old_num_input_groups = ctrl.dset.input_groups.length;
            var min = ctrl.MIN_NUM_INPUT_GROUPS;
            for (var i = old_num_input_groups; i >= min; --i) {
              ctrl.delete_input_group(ctrl.dset.input_groups[0]);
            }
            expect(ctrl.dset.input_groups.length).toBe(min);
            ctrl.delete_input_group(ctrl.dset.input_groups[0]);
            expect(ctrl.dset.input_groups.length).toBe(min);
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          });
        });

        describe('add_candidate_above', function() {
          beforeEach(function() {
            this.ig = ctrl.dset.input_groups[0];
            this.num_constraints = ctrl.dset.constraints.length;
            this.cands = this.ig.candidates;
          });

          it('should add a new candidate to the given input group, above the given candidate', function() {
            ctrl.add_candidate_above(this.cands[0], this.ig);
            expect(this.ig.add_candidate).toHaveBeenCalledWith(0, this.num_constraints);
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          });

          it('should work on candidates beside the first one', function() {
            ctrl.add_candidate_above(this.cands[1], this.ig);
            expect(this.ig.add_candidate).toHaveBeenCalledWith(1, this.num_constraints);
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          });
        });

        describe('add_candidate_below', function() {
          beforeEach(function() {
            this.ig = ctrl.dset.input_groups[0];
            this.num_constraints = ctrl.dset.constraints.length;
            this.cands = this.ig.candidates;
          });

          it('should add a new candidate to the given input group, below the given candidate', function() {
            var index = 0;
            ctrl.add_candidate_below(this.cands[index], this.ig);
            expect(this.ig.add_candidate)
              .toHaveBeenCalledWith(index + 1, this.num_constraints);
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          });

          it('should work on candidates beside the first one', function() {
            var index = 1;
            ctrl.add_candidate_below(this.cands[index], this.ig);
            expect(this.ig.add_candidate)
              .toHaveBeenCalledWith(index + 1, this.num_constraints);
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          });
        });

        describe('delete_candidate', function() {
          beforeEach(function() {
            this.ig = ctrl.dset.input_groups[0];
            this.num_constraints = ctrl.dset.constraints.length;
            this.cands = this.ig.candidates;
            this.old_ig_len = this.cands.length;
          })

          it('should delete the given candidate from the given input group', function() {
            var index = 0;
            var cand = this.cands[index];
            var output = cand.output;
            ctrl.delete_candidate(cand, this.ig);
            expect(this.cands.length).toBe(this.old_ig_len - 1);
            expect(output).not.toBe(this.cands[index].output);
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
          });

          it('should delete the input group when the number of candidates drops below the min', function() {
            var min = ctrl.MIN_NUM_CANDIDATES_PER_INPUT_GROUP;
            var igs = ctrl.dset.input_groups;
            var old_num_igs = igs.length;
            for(var i = this.cands.length; i > min; --i) {
              ctrl.delete_candidate(this.cands[0], this.ig);
            }
            expect(igs.length).toBe(old_num_igs);
            ctrl.delete_candidate(this.cands[0], this.ig);
            expect(igs.length).toBe(old_num_igs - 1);
            expect($rootScope.$broadcast).toHaveBeenCalledWith('table_width_changed');
            expect(this.ig).not.toEqual(igs[0]);
          });
        });
      });
    });
  });
})();
