(function() {
  'use strict';

  angular
    .module('app.models')
    .factory('Candidate', candidate);

  function candidate() {
    return Candidate;

    function Candidate(init) {
      var ret, vvec;
      if (typeof init === "number") {
        vvec = [];
        for (var i = 0; i < init; ++i) {
          vvec.push('');
        }
        ret = {
          input: '',
          output: '',
          optimal: false,
          violation_vector: vvec
        };
      } else if (init.constructor === Object &&
                 init.hasOwnProperty('input') &&
                 init.hasOwnProperty('output') &&
                 init.hasOwnProperty('optimal') &&
                 init.hasOwnProperty('violation_vector')) {
        ret = init;
      } else {
        throw ('Error: Candidates must have input, output, '+
               'optimal, and violation_vector properties');
      }
      return ret;
    }
  }
})();
