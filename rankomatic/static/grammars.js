(function (window, document, undefined) {
    var RETRY_WAIT_TIME = 1000;
    var target = document.getElementById('spinner');
    var spinner = new Spinner(Util.spinner_opts).spin(target);
    var dset_name = $("#info").attr("dset_name");
    var sort_value = $("#info").attr("sort_value");
    var stats_calculated_url = '/global_stats_calculated/' + dset_name + '/' +
              sort_value +
              '?page=' + QueryString.page +
              '&classical=' + QueryString.classical +
              '&sort_by=' + QueryString.sort_by;
    var grammars_stored_url = '/grammars_stored/' +
              dset_name + '/' +
              sort_value +
              '?page=' + QueryString.page +
              '&classical=' + QueryString.classical +
              '&sort_by=' + QueryString.sort_by;

    (function get_stats_if_calculated() {
        $.ajax({
            url: stats_calculated_url,
            dataType: "json",
            success: function(data) {
                if (data['retry']) {
                    setTimeout(get_stats_if_calculated, RETRY_WAIT_TIME);
                } else if (data['need_redirect']) {
                    window.location.href = data['redirect_url'];
                } else if (data['finished']) {
                    if (data['grammars_exist']) {
                        $('#grammars').show();
                        $('#global-statistics').html(data['html_str']);
                        setTimeout( function() {
                            poll_for_grammar_stats(data['grammar_stat_url'],
                                                   spinner);
                        }, RETRY_WAIT_TIME);
                    } else {
                        spinner.stop();
                        $('#global-statistics').html("<h2>No compatible grammars found.</h2>");
                        $('#grammars').hide();
                    }
                }
            }
        })
    })();

    function poll_for_grammar_stats(url, spinner) {
        $.ajax({
            url: url,
            dataType: 'json',
            success: function(data) {
                if (data['retry']) {
                    setTimeout(function() {
                        poll_for_grammar_stats(url, spinner)
                    }, RETRY_WAIT_TIME);
                } else {
                    spinner.stop();
                    console.log(data)
                    $('#grammars').html(data['html_str']);
                    register_grammar_listeners();
                    $('td.num_cot').each(toggle_closest_tr_if_zero);
                    $('#sort-grammars-by').val(QueryString.sort_by);
                }
            }
        })
    }

    function toggle_label_of_toggle_switch($switch) {
        var show_str = "Show all candidates";
        var hide_str = "Hide candidates that never win";
        if ($switch.html() === show_str) {
            $switch.html(hide_str);
        } else if ($switch.html() === hide_str) {
            $switch.html(show_str);
        }
    }

    function toggle_closest_tr_if_zero() {
        var $this = $(this);
        if ($this.html() === "0") {
            $this.closest('tr').toggle(200);
        }
    }

    function register_grammar_listeners() {
        $("#grammar_graphs").click(function(event) {
            event.preventDefault();
            var $target = $(event.target);
            if ($target.attr('class') === "toggle-zero-candidates") {
                $target.prev().find('td.num_cot').each(toggle_closest_tr_if_zero);
                toggle_label_of_toggle_switch($target);
            }
        });

        $('#sort-header button').click(function(event) {
            event.preventDefault();
            var choice = $('#sort-grammars-by').val();
            if (choice !== QueryString['sort_by']) {
                var sort_url = '/' + dset_name + '/grammars/0' +
                        '?page=0' +
                        '&classical=' + QueryString.classical +
                        '&sort_by=' + choice;
                window.location.href = sort_url;
            }
        });
    }


})(this, this.document);
