(function() {
  angular
    .module('app.editor.tableaux')
    .directive("fixedHeader",
               ['$rootScope', '$timeout', fixedHeader]);

  function fixedHeader($rootScope, $timeout) {
    var IN_OUT_COL_MIN_WIDTH = 78;

    return {
      restrict: 'A',
      link: set_up_fixed_header,
    };

    function set_up_fixed_header(scope, element, attrs) {
      $timeout(function() {
        fix_header(element);
        register_width_listener(scope);
        equalize_table_widths(scope);
      }, 0);

      function fix_header() {
        element.wrap('<div />');
        var head = element.find('thead');
        element.before(head);
        head.wrap('<table class="tableaux" />');  // retain CSS stuff on head
        element.wrap('<div class="scrollable" />');  // make table scrollable
      }

      function register_width_listener() {
        $rootScope.$on('table_width_changed', function() {
          $timeout(function() {
            equalize_table_widths(scope);
          }, 0);
        });
      }

      function equalize_table_widths() {
        $('.tableaux thead th').each(function(index) {
          index += 1;  // to use with nth-child selector
          var $this = $(this);
          var column = $('.tableaux tbody td:nth-child('+index+')');

          if ($this.hasClass('constraint')) {
            resize_constraint_column($this, column, scope);
          } else if ($this.hasClass('input-output')) {
            resize_input_output_column($this, column);
          }
        });
      }

      function resize_constraint_column(elem, column, scope) {
        resize_input_container(elem, scope);
        column.width(elem.width());
      }

      function resize_input_container(container, scope) {
        scope.$broadcast('resize_input_container', container);
      }

      function resize_input_output_column(elem, column) {
        var top = $(column[0]);
        resize_input_container(top, scope);
        var new_width = Math.max(IN_OUT_COL_MIN_WIDTH, get_column_width(column));
        elem.width(new_width);
        column.width(new_width);
      }

      function get_column_width(column) {
        var inner_widths = $.map(column.toArray(), function(elem) {
          var offset = elem.firstElementChild.offsetWidth;
          return offset;
        });
        var inner_width = Math.max.apply(Math, inner_widths);
        var column_width = inner_width + 10;
        return column_width;
      }
    }
  }
})();
