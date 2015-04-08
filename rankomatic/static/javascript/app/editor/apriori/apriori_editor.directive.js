(function() {
  'use strict';

  angular
    .module('app.editor.apriori')
    .directive('otAprioriEditor', AprioriEditor);

  function AprioriEditor() {
    return {
      restrict: 'E',
      templateUrl: '/javascript/app/editor/apriori/apriori_editor.html'
    }
  }
})();
