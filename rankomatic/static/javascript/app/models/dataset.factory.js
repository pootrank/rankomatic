(function() {
  'use strict';

  angular
    .module('app.models')
    .factory('Dataset', ['InputGroup', dataset]);

  function dataset(InputGroup) {
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
      input_groups = input_groups || [new InputGroup(constraints.length)];
      this.name = name;
      this.constraints = constraints;
      this.input_groups = input_groups;
    }
  }
})();
