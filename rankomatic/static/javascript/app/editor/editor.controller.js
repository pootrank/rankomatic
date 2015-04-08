(function() {
  'use strict';

  angular
    .module('app.editor')
    .controller('EditorController', [
      '$location',
      '$rootScope',
      'Dataset',
      '$timeout',
      EditorController
    ]);

  function EditorController($location, $rootScope, Dataset, $timeout) {
    var vm = this;
    vm.errors = [];
    vm.messages = [];
    vm.grammar_url = grammar_url;
    vm.save_dset = save_dset;
    vm.remove_error = remove_error;
    vm.remove_message = remove_message;
    vm.delete_dset = delete_dset;
    get_dataset();

    function get_dataset() {
      var url = $location.absUrl();  // we need stuff before the hash
      var edit_match = url.match(/\/([^\/]*?)\/edit/);
      var blank_match = url.match(/calculator/);

      if (edit_match) {
        Dataset.get(edit_match[1]).then(set_dset);
      } else if (blank_match) {
        $timeout(function() {
          set_dset(new Dataset());
        }, 0);
      }
    }

    function grammar_url() {
      var url;
      if (typeof vm.dset !== "undefined") {
        url = '/' + vm.dset.name + '/grammars/0'
      } else {
        url = "#"
      }
      return url;
    }

    function set_dset(data) {
      vm.dset = data;
      $rootScope.$broadcast('dset_loaded');
    }

    function save_dset() {
      vm.dset.save()
        .success(successful_save)
        .error(error_save)
    }

    function successful_save() {
      vm.messages.add_unique(vm.dset.name + ' was successfully saved!');
    }

    function error_save() {
      vm.errors.add_unique('There was an error saving ' + vm.dset_name);
    }

    function remove_error(err) {
      vm.errors.remove_elem(err);
    }

    function remove_message(msg) {
      vm.messages.remove_elem(msg);
    }

    Array.prototype.add_unique = function(elem) {
      var index = this.indexOf(elem);
      if (index === -1) {
        this.push(elem);
      }
    }

    Array.prototype.remove_elem = function(elem) {
      var index = this.indexOf(elem);
      this.splice(index, 1);
    }

    function delete_dset() {
      vm.dset.del()
        .success(successful_delete)
        .error(error_delete)
    }

    function successful_delete() {
      vm.messages.push(vm.dset.name + ' was successfully deleted');
    }

    function error_delete() {
      vm.errors.push('Error deleteing ' + vm.dset.name);
    }
  }
})();
