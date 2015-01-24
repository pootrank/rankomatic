(function(window, document, undefined) {
    var table_template = Handlebars.compile($("#apriori_table").html())

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
        $("#apriori_page").show();
        show_apriori_table();
    });

    function show_apriori_table() {
        //var constraints = $("#tableaux th.constraint").map(function() {
                //return this.find("input").value;
            //}).get();
        var constraints = ['a', 'b', 'c'];
        $("apriori_table_container").html(table_template(
            {'constraints': constraints}
        ));
        console.log(table_template({'constraints': constraints}))
    }


})(this, this.document)
