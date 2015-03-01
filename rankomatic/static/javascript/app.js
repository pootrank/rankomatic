'use strict';

var app = angular.module("OtorderdTableaux", []);

var Candidate = function(num_constraints) {
  num_constraints = num_constraints || 3;

  var vvec = []
  for (var i = 0; i < num_constraints; ++i) {
    vvec.push('');
  }

  return {
    input: '',
    output: '',
    optimal: false,
    violation_vector: vvec
  }
}

var InputGroup = function(num_constraints) {
  return {
    candidates: [new Candidate(num_constraints)],

    get input() {
      return this.candidates[0].input;
    },

    set input(val) {
      for (var i = 0; i < this.candidates.length; ++i) {
        this.candidates[i].input = val;
      }
    },

    add_candidate: function(index, num_constraints) {
      var cand = new Candidate(num_constraints);
      cand.input = this.input;
      this.candidates.insert(index, cand);
    }
  }
}

var Dataset = function() {
  return {
    name: '',
    constraints: ['', '', ''],
    input_groups: [new InputGroup()]
  }
}

app.controller("tableauxCtrl", ['$scope', '$rootScope',
function($scope, $rootScope) {
  var MAX_NUM_CONSTRAINTS = 5;
  var MIN_NUM_CONSTRAINTS = 1;
  var MIN_NUM_INPUT_GROUPS = 1;
  var MIN_NUM_CANDIDATES_PER_INPUT_GROUP = 1;

  $scope.dset = new Dataset();

  $scope.input_class = function(input_group, candidate) {
    if (input_group.candidates.indexOf(candidate) === 0) {
      return "first-input";
    } else {
      return "not-first-input";
    }
  }

  $scope.add_constraint_left = function(index) {
    add_constraint(index);
  }

  $scope.add_constraint_right = function(index) {
    add_constraint(index + 1);
  }

  var add_constraint = function(index) {
    if ($scope.dset.constraints.length < MAX_NUM_CONSTRAINTS) {
      apply_to_constraints_and_vvecs(function(arr) {
        arr.insert(index, "");
      });
      $rootScope.$broadcast('table_width_changed');
    }
  }

  $scope.delete_constraint = function(index) {
    if ($scope.dset.constraints.length > MIN_NUM_CONSTRAINTS) {
      apply_to_constraints_and_vvecs(function(arr) {
        arr.remove(index);
      });
      $rootScope.$broadcast('table_width_changed');
    }
  }

  var apply_to_constraints_and_vvecs = function(fun) {
    fun($scope.dset.constraints)
    $scope.dset.input_groups.forEach(function(ig) {
      ig.candidates.forEach(function(cand) {
        fun(cand.violation_vector);
      });
    });
  }

  $scope.add_input_group_above = function(input_group) {
    var index = $scope.dset.input_groups.indexOf(input_group);
    add_input_group(index);
  }

  $scope.add_input_group_below = function(input_group) {
    var index = $scope.dset.input_groups.indexOf(input_group);
    add_input_group(index + 1);
  }

  var add_input_group = function(index) {
    var ig =  new InputGroup($scope.dset.constraints.length);
    $scope.dset.input_groups.insert(index, ig);
    $rootScope.$broadcast('table_width_changed');
  }

  $scope.delete_input_group = function(input_group) {
    if ($scope.dset.input_groups.length > MIN_NUM_INPUT_GROUPS){
      var index = $scope.dset.input_groups.indexOf(input_group);
      $scope.dset.input_groups.remove(index);
      $rootScope.$broadcast('table_width_changed');
    }
  }

  $scope.add_candidate_above = function(cand, input_group) {
    var index = input_group.candidates.indexOf(cand);
    add_candidate(index, input_group);
  }

  $scope.add_candidate_below = function(cand, input_group) {
    var index = input_group.candidates.indexOf(cand);
    add_candidate(index + 1, input_group);
  }

  var add_candidate = function(index, input_group) {
    input_group.add_candidate(index, $scope.dset.constraints.length);
    $rootScope.$broadcast('table_width_changed');
  }

  $scope.delete_candidate = function(cand, input_group) {
    if (input_group.candidates.length > MIN_NUM_CANDIDATES_PER_INPUT_GROUP) {
      var index = input_group.candidates.indexOf(cand);
      input_group.candidates.remove(index);
      $rootScope.$broadcast('table_width_changed');
    } else {
      $scope.delete_input_group(input_group);
    }
  }

  Array.prototype.remove = function(index) {
    this.splice(index, 1);
  }

  Array.prototype.insert = function(index, val) {
    this.splice(index, 0, val);
  }
}]);

app.directive("editInline", ['$rootScope', function($rootScope) {
  var MIN_INPUT_WIDTH = 56;
  var link = function(scope, element, attrs) {
    element.append('<span class="dummy"></span>');
    var input = element.find('input');
    var dummy = element.find('span.dummy');
    dummy.html(input.val());
    input.bind("keydown keyup", function() {
      var spacer = 10;
      var type = input.attr('type');
      if (type === "number") {
        spacer += 10;
      }
      dummy.html(input.val());
      var input_width = dummy[0].offsetWidth + spacer;
      input_width = Math.max(input_width, MIN_INPUT_WIDTH);
      input.css('width', input_width + 'px');
      element.css('width', (input[0].offsetWidth + spacer) + 'px');
      $rootScope.$broadcast('table_width_changed');
    });
  }
  return {link: link};
}]);

app.directive("fixedHeader", ['$rootScope', '$timeout',
  function($rootScope, $timeout) {
    return {
      restrict: 'A',
      link: link
    };

  function link(scope, element, attrs) {
    $timeout(function() {
      element.wrap('<div />')
      var head = element.find('thead');
      element.before(head);
      head.wrap('<table class="tableaux" />');
      element.wrap('<div class="scrollable" />');
      $rootScope.$on('table_width_changed', function() {
        console.log('table width changed');
        $('.tableaux thead th').each(function(index) {
          var column = element.find('tbody:eq(0) td:eq('+index+')');
          var head_width = $(this).width();
          var column_width = column.width();
          if (head_width < column_width) {
            $(this).width(column_width);
          } else if (head_width > column_width) {
            column.width(head_width);
          }
        });
      });
      $rootScope.$broadcast('table_width_changed');
    }, 0);
  }
}]);
