(function() {
  'use strict';

  angular
    .module('app.models')
    .factory('Dataset', ['InputGroup', '$http', dataset]);

  function dataset(InputGroup, $http) {
    Dataset.get = get;
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

    function get(dset_name) {
      return $http.get('/' + dset_name + '.json')
        .then(dataset_found);
    }

    function dataset_found(response) {
      var data = response.data;
      var dset = new Dataset(data.name, data.constraints, data.input_groups);
      return dset;
    };
  }
})();
