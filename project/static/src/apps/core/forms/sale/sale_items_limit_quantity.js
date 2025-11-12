$(window).on("load", function () {
  const FORMSET_PREFIX = "sale_items";

  function parseNumber(value) {
    const number = parseFloat(value);
    return Number.isFinite(number) ? number : 0;
  }

  function updateQuantityLimit(row, select) {
    const selectedOption = select.find("option:selected");
    const availableQuantity = parseNumber(selectedOption.data("quantity"));
    const $quantityInput = row.find(`input[name^="${FORMSET_PREFIX}-"][name$="-quantity"]`);
    const currentValue = parseNumber($quantityInput.val());

    if ($quantityInput.length) {
      $quantityInput.attr("type", "number");
      $quantityInput.attr("min", 0);

      const isEditingExisting = currentValue > 0 && select.val();

      // Se está em edição, soma o valor atual ao estoque disponível
      const effectiveMax = isEditingExisting ? currentValue + availableQuantity : availableQuantity;
      $quantityInput.attr("max", effectiveMax);

      if (isEditingExisting) {
        $quantityInput.attr("placeholder", `Em edição (${currentValue}/${effectiveMax})`);
        $quantityInput.removeClass("border-red-500 bg-red-50");
      } else if (availableQuantity > 0) {
        $quantityInput.attr("placeholder", `Disponível: ${availableQuantity}`);
        $quantityInput.removeClass("border-red-500 bg-red-50");
      } else {
        $quantityInput.attr("placeholder", "Sem estoque disponível");
        $quantityInput.addClass("border-red-500 bg-red-50");
        $quantityInput.val("");
      }
    }
  }

  function enforceQuantityLimit($input) {
    const max = parseFloat($input.attr("max")) || 0;
    const min = parseFloat($input.attr("min")) || 0;
    let val = parseFloat($input.val()) || 0;
    if (val > max) val = max;
    else if (val < min) val = min;
    $input.val(val);
  }

  function initializeExistingRows() {
    $(".dynamic-form").each(function () {
      const row = $(this);
      const select = row.find(`select[name^="${FORMSET_PREFIX}-"][name$="-item"]`);
      if (select.length && select.val()) updateQuantityLimit(row, select);
    });
  }

  $(document).on("change", `select[name^="${FORMSET_PREFIX}-"][name$="-item"]`, function () {
    const select = $(this);
    const row = select.closest(".dynamic-form");
    updateQuantityLimit(row, select);
  });

  $(document).on("input", `input[name^="${FORMSET_PREFIX}-"][name$="-quantity"]`, function () {
    enforceQuantityLimit($(this));
  });

  initializeExistingRows();
  setTimeout(initializeExistingRows, 300);

  $(document).on(`${FORMSET_PREFIX}:form-added`, function (_event, row) {
    const select = row.find(`select[name^="${FORMSET_PREFIX}-"][name$="-item"]`);
    if (select.length && select.val()) updateQuantityLimit(row, select);
    const quantityInput = row.find(`input[name^="${FORMSET_PREFIX}-"][name$="-quantity"]`);
    quantityInput.on("input", function () {
      enforceQuantityLimit($(this));
    });
  });
});
