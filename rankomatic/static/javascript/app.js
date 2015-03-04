'use strict';
var IN_OUT_COL_MIN_WIDTH = 78;
var MIN_INPUT_WIDTH = 56;

var app = angular.module("OtorderdTableaux", []);

var Candidate = function(init) {
  var ret, vvec;
  if (typeof init === "number") {
    vvec = [];
    for (var i = 0; i < init; ++i) {
      vvec.push('');
    }
    ret = {
      input: '',
      output: '',
      optimal: false,
      violation_vector: vvec
    };
  } else if (init.constructor === Object &&
             init.hasOwnProperty('input') &&
             init.hasOwnProperty('output') &&
             init.hasOwnProperty('optimal') &&
             init.hasOwnProperty('violation_vector')) {
    ret = init;
  } else {
    throw ('Error: Candidates must have input, output, '+
          'optimal, and violation_vector properties');
  }
  return ret;
}

var InputGroup = function(init) {
  var candidates;
  console.log(init.constructor);
  if (!init) {
    candidates = [new Candidate(3)];
  } else if (typeof init === "number") {
    candidates = [new Candidate(init)];
  } else if (init.constructor === Object) {
    candidates = [];
    for (var i = 0; i < init.candidates.length; ++i) {
      candidates.push(new Candidate(init.candidates[i]));
    }
  }
  return {
    candidates: candidates,

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

var Dataset = function(name, constraints, input_groups) {
  name = name || '';
  constraints = constraints || ['', '', ''];
  if (!(input_groups && input_groups.length)) {
    input_groups = [new InputGroup(constraints.length)];
  } else {
    for (var i = 0; i < input_groups.length; ++i) {
      input_groups[i] = new InputGroup(input_groups[i]);
    }
  }
  input_groups = input_groups || [new InputGroup(constraints.length)];
  this.name = name;
  this.constraints = constraints;
  this.input_groups = input_groups;
}

app.controller("tableauxCtrl", ['$scope', '$rootScope', '$http',
function($scope, $rootScope, $http) {
  var MAX_NUM_CONSTRAINTS = 5;
  var MIN_NUM_CONSTRAINTS = 1;
  var MIN_NUM_INPUT_GROUPS = 1;
  var MIN_NUM_CANDIDATES_PER_INPUT_GROUP = 1;

  var dset_name = document.URL.match(/\/([^\/]*?)\/edit/)[1];
  $http.get('/'+dset_name+'.json').success(function(data) {
    console.log(data.name);
    console.log(data.constraints);
    console.log(data.input_groups);
    $scope.dset = new Dataset(data.name, data.constraints, data.input_groups);
    $rootScope.$broadcast('table_width_changed');
  });


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

app.directive("hideZero", ['$timeout', function($timeout) {
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

app.directive("editInline", ['$rootScope', function($rootScope) {
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

app.directive("fixedHeader", ['$rootScope', '$timeout',

  function($rootScope, $timeout) {
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
