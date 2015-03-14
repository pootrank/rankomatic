(function() {
  angular
    .module('app.editor.tableaux')
    .directive("hideZero", ['$timeout', hideZero]);

  function hideZero($timeout) {
    return {
      restrict: 'A',
      link: set_up_hiding
    }

    function set_up_hiding(scope, element, attrs) {
      $timeout(hide_first_and_when_changed, 0);

      function hide_first_and_when_changed() {
        hide_zero();  // hide it to begin
        hide_on_change(element);
      }

      function hide_zero() {
        if (element.val() == 0) {
          element.val("");
        }
      }

      function hide_on_change() {
        element.bind('change', function() {
          hide_zero(element);
        });
      }
    }
  }
})();
