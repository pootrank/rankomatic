(function() {
  'use strict';

  angular.module('app.editor', []);

  angular.module('app.editor').directive("hideZero", ['$timeout', function($timeout) {
    return {
      link: function(scope, element, attrs) {
        $timeout(function() {
          hide_zero(element);
          element.bind('change', function() {
            hide_zero(element);
          });
        }, 0);
      }
    }

    function hide_zero(element) {
      if (element.val() == 0) {
        element.val("");
      }
    }
  }]);

  angular.module('app.editor').directive("editInline", ['$rootScope', function($rootScope) {
    var MIN_INPUT_WIDTH = 56;

    var link = function(scope, element, attrs) {
      element.append('<span class="dummy"></span>');
      var input = element.find('input');
      var dummy = element.find('span.dummy');
      dummy.html(input.val());
      scope.$on('resize_input_container', function(e, to_resize) {
        if (to_resize.is(element)) {
          resize_input_container(element);
        }
      });
      input.bind("change keyup", function() {
        resize_input_container(element);
        $rootScope.$broadcast('table_width_changed');
      });
    }

    function resize_input_container(element) {
      var input = element.find('input');
      var dummy = element.find('.dummy');
      var spacer = input.attr('type') === 'number' ? 20 : 10;
      dummy.html(input.val());
      var input_width = dummy[0].offsetWidth + spacer;
      input_width = Math.max(input_width, MIN_INPUT_WIDTH);
      input.width(input_width);
      element.width(input[0].offsetWidth + spacer);
    }

    return {
      restrict: 'A',
      link: link
    };
  }]);

  angular.module('app.editor').directive("fixedHeader", ['$rootScope', '$timeout',
    function($rootScope, $timeout) {
      var IN_OUT_COL_MIN_WIDTH = 78;
      return {
        restrict: 'A',
        link: link,
      };

      function link(scope, element, attrs) {
        $timeout(function() {
          fix_header(element);
          register_width_listener(scope);
          equalize_table_widths(scope);
        }, 0);
      }

      function fix_header(element) {
        element.wrap('<div />');

        var head = element.find('thead');
        element.before(head);
        head.wrap('<table class="tableaux" />');  // retain CSS stuff on head

        element.wrap('<div class="scrollable" />');  // make table scrollable
      }

      function register_width_listener(scope) {
        $rootScope.$on('table_width_changed', function() {
          $timeout(function() {
            equalize_table_widths(scope);
          }, 0);
        });
      }

      function equalize_table_widths(scope) {
        $('.tableaux thead th').each(function(index) {
          index += 1;  // to use with nth-child
          var $this = $(this);
          var column = $('.tableaux tbody td:nth-child('+index+')');

          if ($this.hasClass('constraint')) {
            resize_constraint_column($this, column, scope);
          } else if ($this.hasClass('input-output')) {
            resize_input_output_column($this, column, scope);
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

      function resize_input_output_column(elem, column, scope) {
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
  }]);
})();
