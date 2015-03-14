(function() {
  'use strict';

  describe('module: models', function() {

    beforeEach(module('app.models'));
    beforeEach(function() {
      module(function($provide) {
        $provide.value('Candidate', function(init) {
          return {input: '', init: init, violation_vector: [0,0,0]};
        });
      });
    });

    describe('factory: InputGroup', function() {
      var InputGroup;

      beforeEach(inject(function(_InputGroup_) {
        InputGroup = _InputGroup_;
      }));

      it('should load by injecting InputGroup', function() {
        expect(InputGroup).toBeDefined();
      });

      it('should create one candidate with init arg three when called empty', function() {
        var ig = new InputGroup();
        expect(ig.input).toBe('');
        expect(ig.candidates).toEqual([{input: "", init: 3, violation_vector: [0,0,0]}]);
      });

      it('should create one candidate with the numerical init arg', function() {
        var ig = new InputGroup(5);
        expect(ig.input).toBe('');
        expect(ig.candidates).toEqual([{input: "", init: 5, violation_vector: [0,0,0]}]);
      });

      it('should create a candidate for each candidate in the init object', function() {
        var arr = {candidates: [1, 2, 3]};
        var ig = new InputGroup(arr);
        expect(ig.input).toBe('');
        expect(ig.candidates).toEqual([
          {init: 1, input: '', violation_vector: [0,0,0,]},
          {init: 2, input: '', violation_vector: [0,0,0,]},
          {init: 3, input: '', violation_vector: [0,0,0,]},
        ]);
      });

      describe('input getter and setter', function() {
        var ig;

        beforeEach(function() {
          ig = new InputGroup({candidates: [1, 2, 3]});
        });

        it('should return the default input with no modification', function() {
          expect(ig.input).toBe('');
        });

        it('should return the input of the candidates if they are changed', function() {
          for (var i = 0; i < ig.candidates.length; ++i) {
            ig.candidates[i].input = 'INPUT';
          }
          expect(ig.input).toBe('INPUT');
        });

        it('should set all of the candidate inputs when set', function() {
          ig.input = "NEW INPUT";
          for (var i = 0; i < ig.candidates; ++i) {
            expect(ig.candidates[i].input.toBe("NEW INPUT"));
          }
        });
      });

      describe('method: add_candidate', function() {
        var ig;

        beforeEach(function() {
          ig = new InputGroup({candidates: [1, 2]})
        });

        it('should add a blank cand with init arg 3 in the 0th spot', function() {
          ig.add_candidate(0);
          expect(ig.candidates).toEqual([
            {input:'', init: 3, violation_vector: [0, 0, 0]},
            {input:'', init: 1, violation_vector: [0, 0, 0]},
            {input:'', init: 2, violation_vector: [0, 0, 0]}
          ]);
        });

        it('should set the input to be the same as the input groups input', function() {
          ig.input = 'NEW INPUT';
          ig.add_candidate(2);
          expect(ig.candidates).toEqual([
            {input:'NEW INPUT', init: 1, violation_vector: [0, 0, 0]},
            {input:'NEW INPUT', init: 2, violation_vector: [0, 0, 0]},
            {input:'NEW INPUT', init: 3, violation_vector: [0, 0, 0]},
          ]);
        });
      });
    });
  });
})();
