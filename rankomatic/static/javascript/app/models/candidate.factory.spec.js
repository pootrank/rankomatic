(function() {
  'use strict';

  describe("module: models,", function() {

    beforeEach(module('app.models'));

    describe("factory: Candidate", function() {
      var Candidate;

      beforeEach(inject(function(_Candidate_) {
        Candidate = _Candidate_;
        jasmine.addMatchers({toEqualCandidate: toEqualCandidate});
      }));

      it("should be able to load Candidate", function() {
        expect(Candidate).toBeDefined();
      });

      it("should make an empty Candidate with no arguments", function() {
        var cand = new Candidate();
        expect(cand).toEqualCandidate({
          input: '', output: '', optimal: false,
          violation_vector: [0, 0, 0]
        });
      });

      it("should make an empty Candidate with the specified number of constraints", function() {
        var cand = new Candidate(5);
        expect(cand).toEqualCandidate({
          input: '', output: '', optimal: false,
          violation_vector: [0, 0, 0, 0, 0]
        })
      });

      it("should make a filled candidate from a bare object", function() {
        var data = {
          input: 'i1', output: 'o1', optimal: true,
          violation_vector: [0, 1, 0, 2]
        }
        var cand = new Candidate(data);
        expect(cand).toEqualCandidate(data);
      });

      it("should check for required properties on an object", function() {
        var good = {input: '', output: '', optimal: '', violation_vector: ''};
        var bad = {input: '', output: '', OPT: '', violation_WRONG: ''};
        expect(Candidate.is_already_built(good)).toBe(true);
        expect(Candidate.is_already_built(bad)).toBe(false);
      });

      function toEqualCandidate(util, customTesters) {
        return {
          compare: function(actual, expected) {
            if (!Candidate.is_already_built(actual)) {
              return {
                pass: false,
                message: "Expected candidate to have input, output, optimal, and violation_vector properties, got "+actual+"."
              }
            } else if (actual.input !== expected.input) {
              return {
                pass: false,
                message: "Expected candidate to have input "+expected.input+", but got "+actual.input+"."
              }
            } else if (actual.output !== expected.output) {
              return {
                pass: false,
                message: "Expected candidate to have output "+expected.output+", but got "+actual.output+"."
              }
            } else if (actual.optimal !== expected.optimal) {
              return {
                pass: false,
                message: "Expected candidate to have optimal "+expected.optimal+", but got "+actual.optimal+"."
              }
            } else if (!util.equals(actual.violation_vector,
                       expected.violation_vector, customTesters)) {
              return {
                pass: false,
                message: "Expected candidate to have violation_vector "+expected.violation_vector+", but got "+actual.violation_vector+"."
              }
            } else {
              return {
                pass: true,
                message: "Expected candidates to differ"
              }
            }
          }
        }
      }
    });
  });
})();
