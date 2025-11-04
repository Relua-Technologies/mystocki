$(window).on("load", function () {
  const FORMSET_PREFIX = "sale_items";

  function parseNumber(value) {
    const number = parseFloat(value);
    return Number.isFinite(number) ? number : 0;
  }

  function updateTotal(row) {
    const quantity = parseNumber(row.find('input[name$="-quantity"]').val());
    const discount = parseNumber(row.find('input[name$="-discount"]').val());
    const price = parseNumber(row.find('input[name$="-price"]').val());

    let total = quantity * price * (1 - discount / 100);
    if (!Number.isFinite(total)) total = 0;

    row.find('input[name$="-total"]').val(total.toFixed(2));
  }

  function updatePriceFromSelect(row, select) {
    const selectedOption = select.find("option:selected");
    const price = parseNumber(selectedOption.data("price"));
    row.find('input[name$="-price"]').val(price.toFixed(2));
    updateTotal(row);
  }

  $(document).on("change", `select[name^="${FORMSET_PREFIX}-"][name$="-item"]`, function () {
    const select = $(this);
    const row = select.closest(".dynamic-form");
    updatePriceFromSelect(row, select);
  });

  $(document).on(
    "input",
    `input[name^="${FORMSET_PREFIX}-"][name$="-quantity"], input[name^="${FORMSET_PREFIX}-"][name$="-discount"]`,
    function () {
      const row = $(this).closest(".dynamic-form");
      updateTotal(row);
    }
  );

  function initializeExistingRows() {
    $(`.dynamic-form`).each(function () {
      const row = $(this);
      const select = row.find(`select[name^="${FORMSET_PREFIX}-"][name$="-item"]`);

      if (select.length && select.val()) {
        updatePriceFromSelect(row, select);
      } else {
        updateTotal(row);
      }
    });
  }

  initializeExistingRows();

  setTimeout(initializeExistingRows, 300);

  $(document).on(`${FORMSET_PREFIX}:form-added`, function (_event, row) {
    const select = row.find(`select[name^="${FORMSET_PREFIX}-"][name$="-item"]`);
    if (select.length) {
      updatePriceFromSelect(row, select);
    } else {
      updateTotal(row);
    }
  });

  $(document).on(`${FORMSET_PREFIX}:form-removed`, function (_event, row) {
    updateTotal(row);
  });
});
