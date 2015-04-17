(function() {
  'use strict';

  angular
    .module('app.editor.tableaux')
    .controller('TableauxController', [
      '$rootScope',
      '$scope',
      'InputGroup',
      TableauxController
    ]);

  function TableauxController($rootScope, $scope, InputGroup) {
    var vm = this;

    vm.MAX_NUM_CONSTRAINTS = 6;
    vm.MIN_NUM_CONSTRAINTS = 1;
    vm.MIN_NUM_INPUT_GROUPS = 1;
    vm.MIN_NUM_CANDIDATES_PER_INPUT_GROUP = 1;

    vm.input_class = input_class;

    vm.add_constraint_left = add_constraint_left;
    vm.add_constraint_right = add_constraint_right;
    vm.delete_constraint = delete_constraint;

    vm.add_input_group_above = add_input_group_above;
    vm.add_input_group_below = add_input_group_below;
    vm.delete_input_group = delete_input_group;

    vm.add_candidate_above = add_candidate_above;
    vm.add_candidate_below = add_candidate_below;
    vm.delete_candidate = delete_candidate;

    get_dataset();
    $rootScope.$on('dset_loaded', get_dataset);

    function get_dataset() {
      vm.dset = $scope.editor.dset;
      $rootScope.$broadcast('table_width_changed');
    }

    function input_class(input_group, candidate) {
      if (input_group.candidates.indexOf(candidate) === 0) {
        return "first-input";
      } else {
        return "not-first-input";
      }
    }

    function add_constraint_left(index) {
      add_constraint(index);
    }

    function add_constraint_right(index) {
      add_constraint(index + 1);
    }

    function add_constraint(index) {
      if (vm.dset.constraints.length < vm.MAX_NUM_CONSTRAINTS) {
        apply_to_constraints_and_vvecs(function(arr) {
          arr.insert(index, "");
        });
        $rootScope.$broadcast('table_width_changed');
      }
    }

    function delete_constraint(index) {
      if (vm.dset.constraints.length > vm.MIN_NUM_CONSTRAINTS) {
        apply_to_constraints_and_vvecs(function(arr) {
          arr.remove(index);
        });
        $rootScope.$broadcast('table_width_changed');
      }
    }

    function apply_to_constraints_and_vvecs(fun) {
      fun(vm.dset.constraints)
      vm.dset.input_groups.forEach(function(ig) {
        ig.candidates.forEach(function(cand) {
          fun(cand.violation_vector);
        });
      });
    }

    function add_input_group_above(input_group) {
      var index = vm.dset.input_groups.indexOf(input_group);
      add_input_group(index);
    }

    function add_input_group_below(input_group) {
      var index = vm.dset.input_groups.indexOf(input_group);
      add_input_group(index + 1);
    }

    function add_input_group(index) {
      var ig =  new InputGroup(vm.dset.constraints.length);
      vm.dset.input_groups.insert(index, ig);
      $rootScope.$broadcast('table_width_changed');
    }

    function delete_input_group(input_group) {
      if (vm.dset.input_groups.length > vm.MIN_NUM_INPUT_GROUPS){
        var index = vm.dset.input_groups.indexOf(input_group);
        vm.dset.input_groups.remove(index);
        $rootScope.$broadcast('table_width_changed');
      }
    }

    function add_candidate_above(cand, input_group) {
      var index = input_group.candidates.indexOf(cand);
      add_candidate(index, input_group);
    }

    function add_candidate_below(cand, input_group) {
      var index = input_group.candidates.indexOf(cand);
      add_candidate(index + 1, input_group);
    }

    function add_candidate(index, input_group) {
      input_group.add_candidate(index, vm.dset.constraints.length);
      $rootScope.$broadcast('table_width_changed');
    }

    function delete_candidate(cand, input_group) {
      if (input_group.candidates.length > vm.MIN_NUM_CANDIDATES_PER_INPUT_GROUP) {
        var index = input_group.candidates.indexOf(cand);
        input_group.candidates.remove(index);
        $rootScope.$broadcast('table_width_changed');
      } else {
        vm.delete_input_group(input_group);
      }
    }

    Array.prototype.remove = function(index) {
      this.splice(index, 1);
    }

    Array.prototype.insert = function(index, val) {
      this.splice(index, 0, val);
    }
  }
})();
