(function() {
  'use strict';

  angular
    .module('app.models')
    .factory('Candidate', candidate);

  function candidate() {
    Candidate.prototype.make_blank_candidate = make_blank_candidate;
    Candidate.prototype.make_blank_violation_vector = make_blank_violation_vector;
    Candidate.prototype.get_data_from = get_data_from;
    Candidate.is_already_built = is_already_built;

    return Candidate;

    function Candidate(init) {
      if (!init || typeof init === "number") {
        this.make_blank_candidate(init)
      } else if (is_already_built(init)) {
        this.get_data_from(init);
      } else {
        throw ('Error: Candidates must have input, output, '+
               'optimal, and violation_vector properties');
      }
    }

    function make_blank_candidate(num_constraints) {
      num_constraints = num_constraints || 3;
      this.input = ''
      this.output = ''
      this.optimal = false
      this.make_blank_violation_vector(num_constraints);
    }

    function make_blank_violation_vector(num_constraints) {
      this.violation_vector = [];
      for (var i = 0; i < num_constraints; ++i) {
        this.violation_vector.push(0);
      }
    }

    function is_already_built(to_check) {
      return (
        to_check.hasOwnProperty('input') &&
        to_check.hasOwnProperty('output') &&
        to_check.hasOwnProperty('optimal') &&
        to_check.hasOwnProperty('violation_vector')
      );
    }

    function get_data_from(obj) {
      this.input = obj.input;
      this.output = obj.output;
      this.optimal = obj.optimal;
      this.violation_vector = obj.violation_vector;
    }
  }
})();
