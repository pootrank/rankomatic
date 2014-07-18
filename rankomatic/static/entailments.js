(function (window, document, undefined) {
    graph_template = Handlebars.compile($("#entailment_graph_template").html());
    var dset_name = $("#entailments").attr("class");
    graph_url = "/graphs/" + dset_name + "/entailments.svg";
    var opts = {
        lines: 13, // The number of lines to draw
        length: 20, // The length of each line
        width: 10, // The line thickness
        radius: 30, // The radius of the inner circle
        corners: 1, // Corner roundness (0..1)
        rotate: 0, // The rotation offset
        direction: 1, // 1: clockwise, -1: counterclockwise
        color: '#000', // #rgb or #rrggbb or array of colors
        speed: 1, // Rounds per second
        trail: 60, // Afterglow percentage
        shadow: false, // Whether to render a shadow
        hwaccel: false, // Whether to use hardware acceleration
        className: 'spinner', // The CSS class to assign to the spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        top: '50%', // Top position relative to parent
        left: '50%' // Left position relative to parent
    };
    var target = document.getElementById('entailments');
    var spinner = new Spinner(opts).spin(target);

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
