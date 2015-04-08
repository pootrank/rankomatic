(function() {
  'use strict';

  angular
    .module('app.editor')
    .directive('otEditorControls', EditorControls);

  function EditorControls() {
    return {
      restrict: 'E',
      templateUrl: '/javascript/app/editor/controls/editor_controls.html'
    }
  }
})();
