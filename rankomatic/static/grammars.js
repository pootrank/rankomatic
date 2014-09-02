(function (window, document, undefined) {
    var target = document.getElementById('grammars');
    var spinner = new Spinner(Util.spinner_opts).spin(target);
    var dset_name = $("#info").attr("dset_name");
    var num_rankings = $("#info").attr("num_rankings");
    var url = '/grammars_stored/' +
              dset_name + '/' +
              num_rankings +
              '?page=' + QueryString.page +
              '&classical=' + QueryString.classical;

    (function get_grammars_if_stored() {
        $.ajax({
            url: url,
            success: function(data) {
                if (data === "false") {
                    setTimeout(get_grammars_if_stored, 300);
                } else if (data === "no grammars") {
                    spinner.stop()
                } else {
                    spinner.stop()
                    $("#grammars").html(data);
                    $('td.num_cot').each(toggle_closest_tr_if_zero);
                }
            },
            error: function(data) {
                spinner.stop();
                $("#grammars").html("Uh oh.");
            }
        });
    })();

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

    $("#grammars").click(function(event) {
        event.preventDefault();
        var $target = $(event.target);
        if ($target.attr('class') === "toggle-zero-candidates") {
            $target.prev().find('td.num_cot').each(toggle_closest_tr_if_zero);
            toggle_label_of_toggle_switch($target);
        }
    });


})(this, this.document);
