$(function() {
    // handle "current toctree" for all levels
    var win = $(window);
    win.on('hashchange', reset);
    function reset() {
        setTimeout(function () {
            var anchor = encodeURI(window.location.hash) || '#';
            try {
                var vmenu = $('.wy-menu-vertical');
                var link = vmenu.find('[href="' + anchor + '"]');
                if (link.length === 0) {
                    var id_elt = $('.document [id="' + anchor.substring(1) + '"]');
                    var closest_section = id_elt.closest('div.section');
                    link = vmenu.find('[href="#' + closest_section.attr("id") + '"]');
                    if (link.length === 0) {
                        link = vmenu.find('[href="#"]');
                    }
                }
                if (link.length > 0) {
                    link.parents('li[class*="toctree-l"]').addClass('current');
                    link[0].scrollIntoView();
                }
            } catch (err) {
                console.log("Error expanding nav for anchor", err);
            }
        }, 100);
    }
    // mark current the actual current toctree node if not opened
    setTimeout(function() {
        var link = $('li[class*="toctree-l"]:not(.current) > a.reference.internal.current');
        if (link.length > 0) {
            link.parents('li[class*="toctree-l"]').addClass('current');
        }
    }, 100);
});
