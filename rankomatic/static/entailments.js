(function (window, document, undefined) {
    graph_template = Handlebars.compile($("#entailment_graph_template").html());
    var dset_name = $("#entailments").attr("class");
    graph_url = "/graphs/" + dset_name + "/entailments.svg";

    (function get_entailments_if_finished() {
        $.ajax({
            url: '/entailments_calculated/' + dset_name + '/',
            success: function(data) {
                if (data === "true") {
                    $("#entailments").html(graph_template({url: graph_url}));
                } else {
                    $("#entailments").html("Calculating entailments...");
                    setTimeout(get_entailments_if_finished, 300);
                }
            }
        });
    })();

})(this, this.document);
