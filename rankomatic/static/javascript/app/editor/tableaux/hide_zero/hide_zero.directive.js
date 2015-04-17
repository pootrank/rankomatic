(function() {
  angular
    .module('app.editor.tableaux')
    .directive("hideZero", ['$timeout', '$rootScope', hideZero]);

  function hideZero($timeout, $rootScope) {
    return {
      restrict: 'A',
      link: set_up_hiding
    }

    function set_up_hiding(scope, element, attrs) {
      $timeout(hide_first_and_when_changed, 0);

      function hide_first_and_when_changed() {
        hide_zero();  // hide it to begin
        hide_on_change();
      }

      function hide_zero() {
        if (element.val() == 0 || element.val() === null) {  // double equals on purpose
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
