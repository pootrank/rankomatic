(function() {
  'use strict';

  angular
    .module('app.models')
    .factory('InputGroup', ['Candidate', input_group]);

  function input_group(Candidate) {
    return InputGroup;

    function InputGroup(init) {
      var candidates;
      if (!init) {
        candidates = [new Candidate(3)];
      } else if (typeof init === "number") {
        candidates = [new Candidate(init)];
      } else if (init.constructor === Object) {
        candidates = [];
        for (var i = 0; i < init.candidates.length; ++i) {
          candidates.push(new Candidate(init.candidates[i]));
        }
      }
      return {
        candidates: candidates,

        get input() {
          return this.candidates[0].input;
        },

        set input(val) {
          for (var i = 0; i < this.candidates.length; ++i) {
            this.candidates[i].input = val;
          }
        },

        add_candidate: function(index, num_constraints) {
          var cand = new Candidate(num_constraints);
          cand.input = this.input;
          this.candidates.insert(index, cand);
        }
      }
    }
  }
})();
