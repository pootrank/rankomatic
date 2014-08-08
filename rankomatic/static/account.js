(function(window, document, undefined) {
    alert_template = Handlebars.compile($("#alert_template").html());

    $('tbody').on("click", ".delete", function(e) {
        e.preventDefault();
        $(this).next().show(200);
        $(this).addClass("disabled");
    })

    $('tbody').on("click", ".no", function(e) {
        e.preventDefault();
        hide_delete_confirmation($(this));
    })

    $('tbody').on("click", ".yes", function(e) {
        e.preventDefault();
        $this = $(this);
        var dset_name = $this.closest("tr").attr("id")
        $.ajax({url: make_delete_url(dset_name),
            success: function(result) {
                var selector = 'tr[id="' + dset_name + '"]'
                $(selector).hide(500);
            },
            error: function(result, status, error) {
                display_deletion_error(dset_name);
                hide_delete_confirmation($this);
            }
        })
    })

    function hide_delete_confirmation($pressed) {
        $pressed.closest(".initially_hidden").hide(200);
        $pressed.closest("td").children("a").removeClass("disabled");
    }

    function make_delete_url(dset_name) {
        return "/delete/" + dset_name + "/";
    }

    function display_deletion_error(dset_name) {
        var msg = "Error deleting " + decodeURIComponent(dset_name);
        $("#messages").prepend(alert_template({message: msg}));
    }

})(this, this.document);
