/*! Remote 1.0.0 - MIT license - Copyright 2024 Deivid Hugo */
/*! Modified by Deivid Hugo to RemoteInDjangoForm */

(function($) {
    "use strict";

    $.fn.remoteInDjangoForm = function(options) {
        var defaults = $.fn.remoteInDjangoForm.defaults;
        var settings = $.extend({}, defaults, options);

        const $selectElement = $(this);
        const wasDisabled = $selectElement.prop("disabled");

        function updateOptions(data) {
            const selectedValue = $selectElement.val() || '';

            $selectElement.empty();
            const options = buildOptions(data);

            for (var i = 0; i < options.length; i++) {
                var key = options[i][0];
                var value = options[i][1];

                var option = $("<option />").val(key).text(value);
                $selectElement.append(option);
            }

            if (selectedValue) {
                $selectElement.val(selectedValue);
            }

            $selectElement.prop("disabled", wasDisabled || options.length === 0);
            $selectElement.trigger("change");
        }

        function buildOptions(data) {
            let options = [];
        
            if (settings.emptyLabel) {
                options.push(['', settings.emptyLabel]);
            }
        
            if (Array.isArray(data)) {
                options = options.concat(handleArrayData(data));
            } else {
                options = options.concat(handleObjectData(data));
            }
        
            return options;
        }

        function handleArrayData(data) {
            if (Array.isArray(data[0])) {
                return data;
            } else {
                return data.map(item => [Object.keys(item)[0], item[Object.keys(item)[0]]]);
            }
        }

        function handleObjectData(data) {
            return Object.entries(data).map(([key, value]) => [key, value]);
        }        
        
        function fetchData() {
            if (!settings.url) {
                console.error("RemoteInDjangoForm error: URL not specified.");
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

    $.fn.remoteInDjangoForm.defaults = {
        bootstrap: null,
        emptyLabel: null, 
    };
})(window.jQuery || window.Zepto);


function applyRemoteInDjangoForm($targetElement) {
    $targetElement.remoteInDjangoForm({
        url: $targetElement.data('url'),
        emptyLabel: $targetElement.data('empty-label') === '' ? null : $targetElement.data('empty-label'),
    });
}

function initializeRemoteInDjangoForms() {
    $('.remote-in-django-form').filter(function() {
        return !$(this).attr('name')?.includes('__prefix__');
    }).each(function() {
        applyRemoteInDjangoForm($(this));
    });
    
}

/*! Chained 1.0.0 - MIT license - Copyright 2010-2014 Mika Tuupola */
/*! Modified by Deivid Hugo */

(function($) {
    "use strict";

    $.fn.remoteChainedInDjangoForm = function(options) {
        var defaults = $.fn.remoteChainedInDjangoForm.defaults;
        var settings = $.extend({}, defaults, options);

        const $selectElement = $(this);
        const wasDisabled = $selectElement.prop("disabled");

        if (settings.loading) {
            settings.clear = true;
        }

        function buildOptions(data) {
            let options = [];
        
            if (settings.emptyLabel) {
                options.push(['', settings.emptyLabel]);
            }
        
            if (Array.isArray(data)) {
                options = options.concat(handleArrayData(data));
            } else {
                options = options.concat(handleObjectData(data));
            }
        
            return options;
        }

        function handleArrayData(data) {
            if (Array.isArray(data[0])) {
                return data;
            } else {
                return data.map(item => [Object.keys(item)[0], item[Object.keys(item)[0]]]);
            }
        }

        function handleObjectData(data) {
            return Object.entries(data).map(([key, value]) => [key, value]);
        }
        
        return this.each(function() {
            function updateOptions(data) {
                const selectedValue = $selectElement.val() || '';

                $selectElement.empty();
                const options = buildOptions(data);

                for (var i = 0; i < options.length; i++) {
                    var key = options[i][0];
                    var value = options[i][1];

                    if (key !== "selected") {
                        var option = $("<option />").val(key).append(value);
                        $selectElement.append(option);
                    } else {
                        selectedValue = value;
                    }
                }

                const $optionToSelect = $selectElement.children(`[value="${selectedValue}"]`);
                $optionToSelect.attr("selected", "selected");

                $selectElement.prop("disabled", wasDisabled || options.length === 0);
                $selectElement.trigger("change");
            }

            var selectElement = this;
            var xhr = false;

            $(settings.parents).each(function() {
                $(this).on("change", function() {
                    var requestData = {};

                    $(settings.parents).each(function() {
                        var attributeName = settings.urlParamField !== null ? settings.urlParamField : $(this).attr(settings.attribute);
                        var attributeValue = $(this).is("select") ? $(":selected", this).val() : $(this).val();
                        requestData[attributeName] = attributeValue;

                        if (settings.depends) {
                            $(settings.depends).each(function() {
                                if (selectElement !== this) {
                                    var attributeName = settings.urlParamField !== null ? settings.urlParamField : $(this).attr(settings.attribute);
                                    var attributeValue = $(this).val();
                                    requestData[attributeName] = attributeValue;
                                }
                            });
                        }
                    });

                    if (xhr && $.isFunction(xhr.abort)) {
                        xhr.abort();
                        xhr = false;
                    }

                    if ($(this).val() === "") {
                        updateOptions({});
                        return;
                    }

                    if (settings.clear) {
                        if (settings.loading) {
                            updateOptions.call(selectElement, { "": settings.loading });
                        } else {
                            $("option", selectElement).remove();
                            $(selectElement).trigger("change");
                        }
                    }

                    xhr = $.getJSON(settings.url, requestData, function(responseData) {
                        updateOptions.call(selectElement, responseData);
                    });
                });

                if (settings.bootstrap) {
                    updateOptions.call(selectElement, settings.bootstrap);
                    settings.bootstrap = null;
                }
            });
        });
    };

    $.fn.remoteChainedInDjangoForm.defaults = {
        attribute: "name",
        urlParamField: null,
        depends: null,
        bootstrap: null,
        loading: null,
        clear: false,
        emptyLabel: null, 
    };
})(window.jQuery || window.Zepto);

function applyRemoteChainedInDjangoForm($targetElement) {
    const parentName = $targetElement.data('parent-name');
    const elementName = $targetElement.attr('name');
    const prefix = elementName.split('-').slice(0, -1).join('-');
    const parentInputId = prefix ? 'id_' + prefix + '-' + parentName : 'id_' + parentName;

    $targetElement.remoteChainedInDjangoForm({
        parents: '#' + parentInputId,
        url: $targetElement.data('url'),
        emptyLabel: $targetElement.data('empty-label') === '' ? null : $targetElement.data('empty-label'),
        urlParamField: $targetElement.data('url-param-field') === '' ? null : $targetElement.data('url-param-field'),
    });

    $('#' + parentInputId).not('.remote-in-django-form').trigger('change');
}

function initializeRemoteChainedInDjangoForms() {
    $('.remote-chained-in-django-form').filter(function() {
        return !$(this).attr('name').includes('__prefix__');
    }).each(function() {
        applyRemoteChainedInDjangoForm($(this));
    });
}

/*! RemoteInDjangoForm 0.1.0 - MIT license - Copyright 2024 Deivid Hugo */

function observeRemoteInDjangoFormsChanges() {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                const addedNodes = Array.from(mutation.addedNodes).filter(node => node.nodeType === Node.ELEMENT_NODE);
                
                addedNodes.forEach(node => {
                    if (node.matches('.remote-in-django-form, .remote-chained-in-django-form') ||
                        node.querySelector('.remote-in-django-form, .remote-chained-in-django-form')) {
                        
                        const $newElements = $(node).find('.remote-in-django-form, .remote-chained-in-django-form');
                        $newElements.each(function() {
                            if ($(this).hasClass('remote-in-django-form')) {
                                applyRemoteInDjangoForm($(this));
                            }
                            if ($(this).hasClass('remote-chained-in-django-form')) {
                                applyRemoteChainedInDjangoForm($(this));
                            }
                        });
                    }
                });
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

$(document).ready(function() {
    initializeRemoteInDjangoForms();
    initializeRemoteChainedInDjangoForms();
    observeRemoteInDjangoFormsChanges();
});