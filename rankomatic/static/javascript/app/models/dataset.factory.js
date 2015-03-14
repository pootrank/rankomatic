(function() {
  'use strict';

  angular
    .module('app.models')
    .factory('Dataset', ['InputGroup', '$http', '$q', dataset]);

  function dataset(InputGroup, $http, $q) {
    Dataset.get_from_url = get_from_url;
    return Dataset;

    function Dataset(name, constraints, input_groups) {
      name = name || '';
      constraints = constraints || ['', '', ''];
      if (!(input_groups && input_groups.length)) {
        input_groups = [new InputGroup(constraints.length)];
      } else {
        for (var i = 0; i < input_groups.length; ++i) {
          input_groups[i] = new InputGroup(input_groups[i]);
        }
      }
      this.name = name;
      this.constraints = constraints;
      this.input_groups = input_groups;
    }

    function get_from_url(url) {
      var edit_match = url.match(/\/([^\/]*?)\/edit/);
      var blank_match = url.match(/calculator/);

      if (edit_match) {
        return dataset_to_edit(edit_match);
      } else if (blank_match) {
        return blank_dataset();
      }
    }

    function dataset_to_edit(edit_match) {
      var dset_name = edit_match[1];
      return $http.get('/' + dset_name + '.json')
        .success(dataset_found);
    }

    function dataset_found(data) {
      var dset = new Dataset(data.name, data.constraints, data.input_groups);
      return dset;
    };

    function blank_dataset() {
      return $q(function(resolve) {
        resolve({data: new Dataset()});
      });
    }
  }
})();
