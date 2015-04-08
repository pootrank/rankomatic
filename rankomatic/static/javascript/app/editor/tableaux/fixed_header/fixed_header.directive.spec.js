(function() {
  'use strict';

  describe('module: app.editor.tableaux', function() {

    beforeEach(module('app.editor.tableaux'));

    describe('directive: fixed-header', function() {

      beforeEach(inject(function($compile, $rootScope, $timeout) {
        var html = "";
        html += '<table fixed-header class="tableaux">';
          html += '<thead>';
            html += '<tr>';
              html += '<th class="input-output">Input</th>';
              html += '<th class="input-output">Output</th>';
              html += '<th class="constraint"><input type="text"></input></th>';
              html += '<th class="constraint"><input type="text"></input></th>';
              html += '<th class="constraint"><input type="text"></input></th>';
            html += '</tr>';
          html += '</thead>';
          html += '<tbody ng-repeat="i in [1, 2]">';
            html += '<tr ng-repeat="j in [1, 2]">';
              html += '<td class="input"><input type="text"></input></td>';
              html += '<td class="output"><input type="text"></input></td>';
              html += '<td class="violation_vector">a</td>';
              html += '<td class="violation_vector">a</td>';
              html += '<td class="violation_vector">a</td>';
            html += '</tr>';
          html += '</tbody>';
        html += '</table>';
        html = $(html);

        $(document).find('body').append(html);
        this.$r = $rootScope;
        this.$t = $timeout;
        spyOn(this.$r, '$broadcast').and.callThrough();

        this.table = $compile(html)(this.$r);
        this.$r.$digest();
        this.$t.flush();
        this.table = this.table.parent().parent();

        var table = this.table;
        this.check_widths = function() {
          this.$r.$broadcast('table_width_changed');
          this.$t.flush();
          table.find('thead th').each(function(index) {
            index += 1;
            var $this = $(this);
            var column = table.find('tbody td:nth-child('+index+')');
            var col_width;
            if ($this.hasClass('input-output')) {
              col_width = get_col_width(column);
            } else {
              col_width = column.width();
            }
            expect($this.width()).toBe(col_width);
          });

          function get_col_width(col) {
            var inner_widths = $.map(col.toArray(), function(elem) {
              return elem.firstElementChild.offsetWidth;
            });
            var inner_width = Math.max.apply(Math, inner_widths);
            return inner_width + 10;
          }
        }
      }));

      afterEach(function() {
        $(document).find('body').html('');
      });

      it('should have 2 tbody and 4 tr elements', function() {
        expect(this.table.find('tbody').length).toBe(2);
        expect(this.table.find('tbody tr').length).toBe(4);
      });

      it('should have the same widths to begin with', function() {
        this.check_widths();
      });

      it('should have the same widths when a constraint label is resized', function() {
        var first_cons = this.table.find('th.constraint:eq(0)');
        var original_width = first_cons.width();
        first_cons.width(original_width + 30);
        this.check_widths();
      });

      it('should have the same widths when an input value is resized', function() {
        var first_input = this.table.find('td.input:eq(0)');
        var original_width = first_input.width();
        first_input.width(original_width + 30);
        this.check_widths();
      });

      it('should have the same widths when a constraint is deleted', function() {
        this.table.find('th.constraint:eq(1)').remove();
        this.table.find('td.violation_vector:eq(1)').remove()
        this.check_widths();
      });

      it('should have the same widths when a constraints is added', function() {
        var th_html = this.table.find('th.constraint:eq(1)').html();
        var td_html = this.table.find('td.violation_vector:eq(1)').html()
        this.table.find('thead tr').append($(th_html));
        this.table.find('tbody tr').append($(td_html));
        this.check_widths();
      });

      it('should have the same widths when a constraint label is lengthened and shortened', function() {
        var first_cons = this.table.find('th.constraint:eq(0)');
        var original_width = first_cons.width();
        first_cons.width(original_width + 30);
        this.check_widths();
        first_cons.width(original_width);
        this.check_widths();
      });

      it('should have the same widths when an input label is lengthened and shortened', function() {
        var first_input = this.table.find('td.input:eq(0)');
        var original_width = first_input.width();
        first_input.width(original_width + 30);
        this.check_widths();
        first_input.width(original_width);
        this.check_widths();
      });
    });
  });
})();
