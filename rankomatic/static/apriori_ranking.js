(function(window, document, undefined) {
    var table_template = Handlebars.compile($("#apriori_table_template").html())
    var apriori_ranking = []

    function switch_tabs_to_this(target) {
        $("#edit_tabs li").each(function() {
            $(this).removeClass("active");
        });
        $(target).addClass("active");
    }

    $("#edit_tab").click(function() {
        switch_tabs_to_this(this);
        $("#apriori_page").hide();
        $("#dataset").show();
    });

    $("#apriori_tab").click(function() {
        switch_tabs_to_this(this);
        $("#dataset").hide();
        show_apriori_table();
        $("#apriori_page").show();
    });

    function show_apriori_table() {
        var constraints = $("#tableaux_header th.constraint").map(function() {
                return $(this).find("input").val();
            }).get();
        var grid = []
        for (i = 0; i < constraints.length; i++) {
            grid.push({
                'constraint': constraints[i],
                'dominates': constraints
            });
        }
        $("#apriori_table_container").html(table_template(
            {'constraints': grid}
        ));
        $("#header_label").attr('colspan', constraints.length);
        deactivate_diagonal();
        set_apriori_listeners();
        $("input.apriori_check").hide();
    }

    function deactivate_diagonal() {
        $("#apriori_table input.apriori_check").each(function() {
            var col = $(this).attr('name');
            var row = $(this).closest("tr").attr('id').slice(4);
            if (row === col) {
                deactivate_td($(this).closest("td"));
            }
        });
    }

    function deactivate_td($to_deactivate) {
        $to_deactivate.removeClass("checked unchecked");
        $to_deactivate.addClass("deactivated");
        $to_deactivate.find("input").attr("disabled", "true");
    }

    function set_apriori_listeners() {
        $("#apriori_table").click(function(event) {
            //event.preventDefault();
            var $target = $(event.target);
            if ($target.is('input')) {
                console.log("got input", $target);
                $target = $target.closest("td");
            }
            if ($target.is('td.checkbox_container')) {
                if (!$target.hasClass("deactivated")) {
                    toggle_check_container($target);
                }
            }
        });
    }

    function toggle_check_container($to_toggle) {
        console.log("toggling...", $to_toggle);
        if ($to_toggle.hasClass("checked")) {
            $to_toggle.removeClass("checked");
            $to_toggle.addClass("unchecked");
            $input = $to_toggle.find("input");
            $input.prop('checked', false);
            $to_toggle.html($input[0].outerHTML);

        } else {
            $to_toggle.removeClass("unchecked");
            $to_toggle.addClass("checked");
            $to_toggle.find("input").prop('checked', true);
            $to_toggle.prepend("&#10003;")
        }
    }
})(this, this.document)
