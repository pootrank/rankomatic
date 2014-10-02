(function (window, document, undefined) {
    var RETRY_WAIT_TIME = 1000;
    var target = document.getElementById('spinner');
    var spinner = new Spinner(Util.spinner_opts).spin(target);
    var dset_name = $("#info").attr("dset_name");
    var num_rankings = $("#info").attr("num_rankings");
    var stats_calculated_url = '/global_stats_calculated/' + dset_name + '/' +
              num_rankings +
              '?page=' + QueryString.page +
              '&classical=' + QueryString.classical;
    var grammars_stored_url = '/grammars_stored/' +
              dset_name + '/' +
              num_rankings +
              '?page=' + QueryString.page +
              '&classical=' + QueryString.classical;

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
                    $('#global-statistics').html(data['html_str']);
                    setTimeout(get_grammars_if_stored, RETRY_WAIT_TIME);
                }
            }
        })
    })();

    function get_grammars_if_stored() {
        $('#grammars').show();
        target = document.getElementById('grammars');
        $.ajax({
            url: grammars_stored_url,
            dataType: "json",
            success: function(data) {
                if (data['retry']) {
                    setTimeout(get_grammars_if_stored, RETRY_WAIT_TIME);
                } else {
                    if (data['grammars_exist']) {
                        var grammar_stat_url = '/grammar_stats_calculated/' +
                            data['dset_name'] + '/' + num_rankings +
                            '?classical=' + data['classical'] +
                            '&page=' + data['page'] +
                            '&job_id=' + data['job_id'];
                        setTimeout( function() {
                            poll_for_grammar_stats(grammar_stat_url, spinner)
                        }, RETRY_WAIT_TIME)
                    } else {
                        spinner.stop();
                    }
                }
            },
            error: function(data) {
                spinner.stop();
                $("#grammars").html("Uh oh.");
            }
        });
    }

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
                    $('#grammars').html(data['html_str']);
                    register_grammar_stats_listener();
                    $('td.num_cot').each(toggle_closest_tr_if_zero);
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

    function register_grammar_stats_listener() {
        $("#grammar_graphs").click(function(event) {
            event.preventDefault();
            var $target = $(event.target);
            if ($target.attr('class') === "toggle-zero-candidates") {
                $target.prev().find('td.num_cot').each(toggle_closest_tr_if_zero);
                toggle_label_of_toggle_switch($target);
            }
        });
    }


})(this, this.document);
