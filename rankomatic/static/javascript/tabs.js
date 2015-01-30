/* constructor: TabList
 * usage: var tabs = new TabList($("#tab-list"));
 * ==============================================
 * Auto-magically create tabs.
 *
 * Call this constructor with the jQuery ul you want to make the tab-list. For
 * each li in the list, make sure it has class .navtab and a unique id. Each
 * tab's content is defined by the class .tab-content, and is linked to its
 * tab by adding a class that is the li.navtab's id, follwed by '-content'. For
 * example, the tab li.navtab#first-tab will display elements in the DOM with
 * the class 'first-tab-content', e.g. div.navtab-content.first-tab-content.
 * Those DOM elements must have both classes, so that they are linked generally
 * as tab content and to the specific tab.
 *
 * If no tab is initally specified as active, the first child of the ul is
 * designated as the initial active tab.
 */
function TabList($list) {
    this.list = $list;
    var $active = this.list.find("li.navtab.active");
    if ($active.length === 0) {
        $active = this.list.find("li.navtab:first-child");
    }
    this.show_tab($active);
    this.list.click($.proxy(this.show_clicked_tab, this));
}

TabList.prototype.show_tab = function($tab) {
    $(".navtab-content").hide();
    this.list.find("li.navtab").removeClass("active");
    $tab.addClass("active");
    var content_selector = "." + $tab.attr("id") + "-content";
    $(content_selector).show();
}

TabList.prototype.show_clicked_tab = function(event) {
    $tab = $(event.target).closest("li.navtab");
    if ($tab && !$tab.hasClass("active")) {
        this.show_tab($tab);
    }
}

