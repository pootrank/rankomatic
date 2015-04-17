(function() {
  'use strict';

  describe('module: app.editor.tableaux', function() {
    beforeEach(module('app.editor.tableaux'));

    describe('directive: hideZero', function() {
      beforeEach(inject(function(_$compile_, $rootScope, $timeout) {
        var html = '<input hide-zero type="number"></input>';
        this.$compile = _$compile_;

        this.input = this.$compile(html)($rootScope);
        $rootScope.$digest();
        $timeout.flush();
      }));

      it('should compile with the attribute hide-zero', function() {
        expect(this.input).toBeDefined();
      });

      it('should show a blank string initially', function() {
        expect(this.input.val()).toBe('');
      });

      it('should show the number for positive numbers', function() {
        for(var i = 1; i < 11; ++i) {
          this.input.val(i);
          this.input.triggerHandler('change');
          expect(parseInt(this.input.val())).toBe(i);
        }
      });

      it('should show an empty string for 0', function() {
        this.input.val(0);
        this.input.triggerHandler('change');
        expect(this.input.val()).toBe('');
      });

      it('should show an empty string for null', function() {
        this.input.val(null);
        this.input.triggerHandler('change');
        expect(this.input.val()).toBe('');
      });
    });
  });
})();
