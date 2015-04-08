(function() {
  angular
    .module('app.editor.tableaux')
    .directive('otEditInline',
               ['$rootScope', editInline]);

  function editInline($rootScope) {
    var MIN_INPUT_WIDTH = 56
    var NUMBER_SPACER = 20;
    var TEXT_SPACER = 10;

    var directive =  {
      restrict: 'A',
      link: set_up_width_matching
    };

    return directive;

    function set_up_width_matching(scope, element, attrs) {
      var elems = build_matching_elements();
      bind_input_resize_listeners(elems);

      function build_matching_elements() {
        element.append('<span class="dummy"></span>');
        var elems = get_inner_elems(element);
        elems.dummy.html(elems.input.val());
        elems.dummy.css('font-size', elems.input.css('font-size'));
        return elems;
      }

      function get_inner_elems() {
        return {
          input: element.find('input'),
          dummy: element.find('.dummy')
        }
      }

      function bind_input_resize_listeners(elems) {
        scope.$on('resize_input_container', resize_from_elswhere_in_column);
        elems.input.bind("change keyup", resize_by_changing_input);
      }

      function resize_from_elswhere_in_column(e, to_resize) {
        if (to_resize.is(element)) {
          resize_input_container();
        }
      }

      function resize_by_changing_input() {
        resize_input_container();
        $rootScope.$broadcast('table_width_changed');
      }

      function resize_input_container() {
        var elems = get_inner_elems();
        var spacer = get_spacer(elems.input);
        set_input_width(elems, spacer);
        set_container_width(elems, spacer);
      }

      function get_spacer(input) {
        if (input.attr('type') === 'number') {
          return NUMBER_SPACER;
        } else {
          return TEXT_SPACER;
        }
      }

      function set_input_width(elems, spacer) {
        elems.dummy.html(elems.input.val());
        var input_width = elems.dummy[0].offsetWidth + spacer;
        input_width = Math.max(input_width, MIN_INPUT_WIDTH);
        elems.input.width(input_width);
      }

      function set_container_width(elems, spacer) {
        var container_width = elems.input[0].offsetWidth + spacer;
        element.width(container_width);
      }
    }
  }
})();
