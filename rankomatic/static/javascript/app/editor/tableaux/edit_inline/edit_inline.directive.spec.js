(function() {
  'use strict';

  describe('module: app.editor.tableaux', function() {

    beforeEach(module('app.editor.tableaux'));

    describe('directive: editInline', function() {

      var LONG_INPUT = 'a very very long input that will make its surroundings move';
      var MED_INPUT = 'a sort of long input';
      var SHORT_INPUT = 'short';

      beforeEach(inject(function($compile, $rootScope) {
        var html = $('<div ot-edit-inline><input type="text"></input></div>');
        $(document).find('body').append(html);
        this.$r = $rootScope;
        this.div = $compile(html)($rootScope);
        this.$r.$digest();
        spyOn(this.$r, '$broadcast').and.callThrough();
        this.input = this.div.find('input');
        this.input.change();
        this.initial_width = this.div.width();

        var input = this.input;
        this.change_input = function(val) {
          input.val(val);
          input.change();
        }
      }));

      afterEach(function() {
        this.div.remove();
      });

      it('should compile the directive', function() {
        expect(this.div).toBeDefined();
      });

      it('should begin with the initial width', function() {
        expect(this.div.width()).toBe(this.initial_width);
      });

      it('should increase in width when the input is lengthened', function() {
        this.change_input(LONG_INPUT);
        expect(this.div.width()).toBeGreaterThan(this.initial_width);
        expect(this.$r.$broadcast).toHaveBeenCalledWith('table_width_changed');
      });

      it('should decrease in width when input val is shortened', function() {
        this.change_input(LONG_INPUT);
        var big_width = this.div.width();
        this.change_input(SHORT_INPUT);
        expect(this.div.width()).toBeLessThan(big_width);
        expect(this.$r.$broadcast).toHaveBeenCalledWith('table_width_changed');
      });

      it('should resize the div when the right event is broadcast', function() {
        this.change_input(LONG_INPUT);
        this.input.val('');
        var big_because_something_else = this.div.width();
        this.$r.$broadcast('resize_input_container', this.div);
        expect(this.div.width()).toBeLessThan(big_because_something_else);
      });

      it('should not resize the div if a different element is broadcast', function() {
        this.change_input(LONG_INPUT);
        this.input.val('');
        var big_width = this.div.width();
        this.$r.$broadcast('resize_input_container', this.input);
        expect(this.div.width()).toBe(big_width);
      });
    });
  });
})();
