class LoadingSpinner {
    static loadingSpinnerSelector = '#loading-spinner';
    static $loadingSpinner = null;

    static getSpinner() {
        if (!this.$loadingSpinner) {
            this.$loadingSpinner = $(this.loadingSpinnerSelector);
        }
        return this.$loadingSpinner;
    }

    static show() {
        this.getSpinner().show();
    }

    static hide() {
        this.getSpinner().hide();
    }

    static showOnFormSubmission() {
        $('form').on('submit', function () {
            LoadingSpinner.show();
        });
    }

    static showOnLinkClick() {
        $('a[href]')
            .not('[target="_blank"]')
            .not('[href="#"]')
            .not('[href*="javascript:void(0)"]')
            .on('click', function () {
                LoadingSpinner.show();
            });
    }

    static startPageLoadEvents() {
        $(window).on('load', function () {
            LoadingSpinner.showOnFormSubmission(); 
            LoadingSpinner.showOnLinkClick(); 
        });
    }

    static startBeforeUnloadEvents() {
        $(window).on('beforeunload', function () {
            LoadingSpinner.hide();
        });
    }

    static startEvents() {
        this.startPageLoadEvents();
        this.startBeforeUnloadEvents();
    }
}

LoadingSpinner.startEvents();
