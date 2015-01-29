(function (window, document, undefined) {
    graph_template = Handlebars.compile($("#entailment_graph_template").html());
    var dset_name = $("#entailments").attr("class");
    graph_url = "/graphs/" + dset_name + "/entailments.png";

    var target = document.getElementById('entailments');
    var spinner = new Spinner(Util.spinner_opts).spin(target);

    (function get_entailments_if_finished() {
        $.ajax({
            url: '/entailments_calculated/' + dset_name + '/',
            success: function(data) {
                if (data === "true") {
                    spinner.stop()
                    $("#entailments").html(graph_template({url: graph_url}));
                } else {
                    setTimeout(get_entailments_if_finished, 300);
                }
            }
        });
    })();
})(this, this.document);
