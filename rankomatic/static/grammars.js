(function (window, document, undefined) {
    var target = document.getElementById('grammars');
    var spinner = new Spinner(Util.spinner_opts).spin(target);
    var dset_name = $("#info").attr("dset_name");
    var num_rankings = $("#info").attr("num_rankings");
    var url = '/grammars_stored/' +
              dset_name + '/' +
              num_rankings +
              '?page=' + QueryString.page;

    (function get_grammars_if_stored() {
        $.ajax({
            url: url,
            success: function(data) {
                if (data === "false") {
                    setTimeout(get_grammars_if_stored, 300);
                } else {
                    spinner.stop()
                    $("#grammars").html(data);
                }
            },
            error: function(data) {
                spinner.stop();
                $("#grammars").html("Uh oh.");
            }
        });
    })();

})(this, this.document);
