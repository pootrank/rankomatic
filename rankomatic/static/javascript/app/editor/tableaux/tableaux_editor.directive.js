(function() {
  'use strict';

  angular
    .module('app.editor.tableaux')
    .directive('otTableauxEditor', TableauxEditor);

  function TableauxEditor() {
    return {
      restrict: 'E',
      templateUrl: '/javascript/app/editor/tableaux/tableaux_editor.html'
    }
  }
})();
