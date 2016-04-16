(function(undefined) {
  'use strict';

  angular
    .module('app.editor.apriori')
    .controller('AprioriController', [
      '$scope',
      '$rootScope',
      'TransitiveSet',
      AprioriController
    ]);

    function AprioriController($scope, $rootScope, TransitiveSet) {
      var vm = this;
      vm.transitively_required = false;

      vm.add_or_remove = add_or_remove;
      vm.clear_ranking = clear_ranking;

      get_dataset();
      $rootScope.$on('dset_loaded', get_dataset);
      $rootScope.$on('constraint_deleted', clear_ranking);

      function dset_is_defined() {
        return typeof vm.dset !== 'undefined';
      }

      function get_dataset() {
        vm.dset = $scope.editor.dset;
        var ranking = dset_is_defined() ? vm.dset.apriori_ranking : undefined;
        vm.ranking = new TransitiveSet(ranking);
      }

      function add_or_remove(constraint_0, constraint_1) {
        var successfully_modifed = modify_ranking(constraint_0, constraint_1);
        propagate_ranking_changes(successfully_modifed);
      }

      function modify_ranking(cons_0, cons_1) {
        if (vm.ranking.contains(cons_0, cons_1)) {
          var successfully_removed = vm.ranking.remove(cons_0, cons_1);
        } else {
          var successfully_added = vm.ranking.add(cons_0, cons_1);
        }
        return Boolean(successfully_added || successfully_removed)
      }

      function propagate_ranking_changes(successfully_modified) {
        if (successfully_modified) {
          vm.transitively_required = false;
          update_ranking_model();
        } else {
          vm.transitively_required = true;
        }
      }

      function update_ranking_model() {
        if (dset_is_defined()) {
          vm.dset.apriori_ranking = vm.ranking.to_array();
        }
      }

      function clear_ranking() {
        vm.ranking = new TransitiveSet();
        update_ranking_model();
      }
    }
})();
