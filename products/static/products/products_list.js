$(document).ready(function() {

    var $searchCollapseButton = $('#searchCollapseButton'),
        $collapseBlock = $('#searchCollapse'),
        $searchInput = $('#searchInput'),
        $searchColSelectBlock = $('#col-selector');

    $searchCollapseButton.click(function() {
        if($collapseBlock.attr('aria-expanded')) {
            $searchInput.click();
        }
    });

    var buildList = function(fields) {
        return new List('items', {
            valueNames: fields
        });
    }

    if(typeof LIST_JS_OPTIONS !== 'undefined') {
        var fields = LIST_JS_OPTIONS.valueNames;

        for(var i = 0; i < fields.length; ++i) {
            var field = fields[i];

            var checkboxHtml = '<div class="checkbox-inline"><label><input checked type="checkbox" name="' + field + '">'+ field + '</label></div>';

            $searchColSelectBlock.append(checkboxHtml);
        }

        buildList(fields);

        $searchColSelectBlock.find('input:checkbox').click(function() {

            var fields = $searchColSelectBlock.find('input:checkbox:checked').map(function() {
                return this.name;
            });

            var searchList = buildList(fields);
        });
    }
});
