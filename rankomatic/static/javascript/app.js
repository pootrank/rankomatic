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

app.controller("tableauxCtrl", ['$scope', function($scope) {
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
    }
  }

  $scope.delete_constraint = function(index) {
    if ($scope.dset.constraints.length > MIN_NUM_CONSTRAINTS) {
      apply_to_constraints_and_vvecs(function(arr) {
        arr.remove(index);
      });
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
  }

  $scope.delete_input_group = function(input_group) {
    if ($scope.dset.input_groups.length > MIN_NUM_INPUT_GROUPS){
      var index = $scope.dset.input_groups.indexOf(input_group);
      $scope.dset.input_groups.remove(index);
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
  }

  $scope.delete_candidate = function(cand, input_group) {
    if (input_group.candidates.length > MIN_NUM_CANDIDATES_PER_INPUT_GROUP) {
      var index = input_group.candidates.indexOf(cand);
      input_group.candidates.remove(index);
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

app.directive("editInline", function() {
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
      input.css('width', (dummy[0].offsetWidth + spacer) + 'px');
      element.css('width', (input[0].offsetWidth + spacer) + 'px');
    });
  }
  return {link: link};
});

app.directive("fixedHeader", ['$timeout', function($timeout) {
  return {
    restrict: 'A',
    link: link
  };

  function link(scope, element, attrs) {
    //$timeout(function() {
      //element.stickyTableHeaders({fixedOffset: 40});
    //}, 0);
  }
}]);
  //var link = function(scope, element, attrs) {
    //var fixed_header;
    //function init() {
      //element.wrap('<div class="container" />');
      //fixed_header = element.clone();
      //fixed_header
        //.find("tbody")
          //.remove()
        //.end()
        //.addClass("fixed")
        //.insertBefore(element);
      //resize_fixed();
    //}

    //function resize_fixed() {
      //fixed_header.find("th").each(function(index) {
        //var width = element.find('th').eq(index).outerWidth();
        //$(this).css("width", width + "px");
      //});
    //}

    //function scroll_fixed() {
      //var offsets = get_offsets(this);
      //console.log(offsets);
      //if (original_header_visible(offsets)) {
        //fixed_header.hide();
      //} else if (original_header_not_visible) {
        //fixed_header.show();
      //}
    //}

    //function get_offsets(obj) {
      //var table_offset_top = element.offset().top;
      //return {
        //offset: $(obj).scrollTop(),
        //table_offset_top: table_offset_top,
        //table_offset_bottom: get_bottom_offset(table_offset_top)
      //}
    //}

    //function get_bottom_offset(top_offset) {
      //return top_offset + element.height() - element.find("thead").height();
    //}

    //function original_header_visible(o) {
      //return o.offset < o.table_offset_top || o.offset > o.table_offset_bottom;
    //}

    //function original_header_not_visible(o, fixed_header) {
      //return (o.offset >= o.table_offset_top &&
              //o.offset <= o.table_offset_bottom &&
              //fixed_header.is(":hidden"));
    //}

    //$(document).ready(function() {
      //$(window).resize(resize_fixed);
      //$(window).scroll(scroll_fixed);
      //init();
    //});
  //}
  //return {link: link};
//});
