(function() {
  'use strict';

  angular
    .module('app.editor')
    .controller('EditorController', [
      '$location',
      '$rootScope',
      'Dataset',
      '$scope',
      '$q',
      EditorController
    ]);

  function EditorController($location, $rootScope, Dataset, $scope, $q) {
    var vm = this;
    get_dataset();

    function get_dataset() {
      var url = $location.absUrl();  // we need stuff before the hash
      var edit_match = url.match(/\/([^\/]*?)\/edit/);
      var blank_match = url.match(/calculator/);

      if (edit_match) {
        Dataset.get(edit_match[1]).then(set_dset);
      } else if (blank_match) {
        set_dset(new Dataset());
      }
    }

    function set_dset(data) {
      vm.dset = data;
      $rootScope.$broadcast('dset_loaded');
    }
  }
})();
