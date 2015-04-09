(function() {
  angular
    .module('app.editor')
    .config(['$provide', make_q_like_http]);

  function make_q_like_http($provide) {
    $provide.decorator('$q', function($delegate) {
      var defer = $delegate.defer;
      $delegate.defer = function() {
        var deferred = defer();

        deferred.promise.success = function(success_fn) {
          deferred.promise.then(function(response) {
            success_fn(response.data, response.status, response.headers);
          });
          return deferred.promise;
        }

        deferred.promise.error = function(error_fn) {
          deferred.promise.then(null, function(response) {
            error_fn(response.data, response.status, response.headers);
          });
          return deferred.promise;
        }
        return deferred;
      }
      return $delegate;
    });
  }
})();
