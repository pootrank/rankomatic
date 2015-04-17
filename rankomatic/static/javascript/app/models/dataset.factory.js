(function() {
  'use strict';

  angular
    .module('app.models')
    .factory('Dataset', ['InputGroup', '$http', dataset]);

  function dataset(InputGroup, $http) {
    Dataset.get = get;
    Dataset.prototype.save = save;
    Dataset.prototype.del = del;
    return Dataset;

    function Dataset(name, constraints, input_groups, apriori_ranking) {
      name = name || '';
      constraints = constraints || ['', '', ''];
      if (!(input_groups && input_groups.length)) {
        input_groups = [new InputGroup(constraints.length)];
      } else {
        for (var i = 0; i < input_groups.length; ++i) {
          input_groups[i] = new InputGroup(input_groups[i]);
        }
      }
      if (typeof apriori_ranking === 'undefined' || !apriori_ranking) {
        apriori_ranking = [];
      }
      this.name = name;
      this.constraints = constraints;
      this.input_groups = input_groups;
      this.apriori_ranking = apriori_ranking;
    }

    function get(dset_name) {
      return $http.get('/' + encodeURI(dset_name) + '.json')
        .then(dataset_found);
    }

    function dataset_found(response) {
      var data = response.data;
      var dset = new Dataset(
        data.name, data.constraints,
        data.input_groups, JSON.parse(data.apriori_ranking)
      );
      return dset;
    };

    function save() {
      this.input_groups.forEach(function(ig) {
        ig.candidates.forEach(function(cand) {
          cand.violation_vector.forEach(function(v, index) {
            cand.violation_vector[index] = cand.violation_vector[index] || 0;
          });
        });
      });
      return $http.post('/save_dset/', {
        name: this.name,
        constraints: this.constraints,
        input_groups: this.input_groups,
        apriori_ranking: this.apriori_ranking
      });
    }

    function del() {
      return $http.get('/delete/' + encodeURI(this.name));
    }
  }
})();
