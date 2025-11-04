/*! Remote 1.0.0 - MIT license - Copyright 2024 Deivid Hugo */

(function($) {
    "use strict";

    $.remote = function(options) {
        var defaults = $.fn.remote.defaults;
        var settings = $.extend({}, defaults, options);

        function updateOptions(data) {
            var selectedValue = selectElement.val() || '';

            selectElement.empty();

            var options = [];

            if (settings.emptyLabel) {
                options.push(['', settings.emptyLabel]);
            }

            if ($.isArray(data)) {
                options = $.isArray(data[0]) ? options.concat(data) : options.concat($.map(data, function(item) {
                    return $.map(item, function(value, key) {
                        return [[key, value]];
                    });
                }));
            } else {
                for (var key in data) {
                    if (data.hasOwnProperty(key)) {
                        options.push([key, data[key]]);
                    }
                }
            }

            for (var i = 0; i < options.length; i++) {
                var key = options[i][0];
                var value = options[i][1];

                var option = $("<option />").val(key).text(value);
                selectElement.append(option);
            }

            if (selectedValue) {
                selectElement.val(selectedValue);
            }

            selectElement.prop("disabled", options.length === 0);
            selectElement.trigger("change");
        }

        function fetchData() {
            if (!settings.url) {
                console.error("Remote error: URL not specified.");
                return;
            }

            $.getJSON(settings.url, function(responseData) {
                updateOptions(responseData);
            });
        }

        var selectElement = $(this);

        if (settings.bootstrap) {
            updateOptions(settings.bootstrap);
        }

        fetchData(); 
        return selectElement;
    };

    $.fn.remote = $.remote;

    $.fn.remote.defaults = {
        bootstrap: null,
        emptyLabel: null, 
    };
})(window.jQuery || window.Zepto);
