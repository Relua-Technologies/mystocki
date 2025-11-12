$(window).on("load", function () {
  const FORMSET_PREFIX = "sale_items";

  function adjustQuantityInput(row, select) {
    const selectedOption = select.find("option:selected");
    const unit = selectedOption.data("unit");
    const $quantityInput = row.find(`input[name^="${FORMSET_PREFIX}-"][name$="-quantity"]`);

    if (!$quantityInput.length) return;

    // Unidades inteiras → apenas números inteiros
    const integerUnits = ["un", "pc", "cx"];

    if (integerUnits.includes(unit)) {
      $quantityInput.attr("step", "1");
      const currentValue = parseFloat($quantityInput.val());
      if (!Number.isNaN(currentValue)) {
        $quantityInput.val(Math.floor(currentValue));
      }
    } else {
      // Unidades fracionadas → permite decimais
      $quantityInput.attr("step", "0.01");
    }
  }

  function initializeExistingRows() {
    $(".dynamic-form").each(function () {
      const row = $(this);
      const select = row.find(`select[name^="${FORMSET_PREFIX}-"][name$="-item"]`);
      if (select.length && select.val()) {
        adjustQuantityInput(row, select);
      }
    });
  }

  // Quando o usuário muda o item selecionado
  $(document).on("change", `select[name^="${FORMSET_PREFIX}-"][name$="-item"]`, function () {
    const select = $(this);
    const row = select.closest(".dynamic-form");
    adjustQuantityInput(row, select);
  });

  // Inicializa quando a página carrega
  initializeExistingRows();
  setTimeout(initializeExistingRows, 300);

  // Quando um novo form é adicionado dinamicamente
  $(document).on(`${FORMSET_PREFIX}:form-added`, function (_event, row) {
    const select = row.find(`select[name^="${FORMSET_PREFIX}-"][name$="-item"]`);
    if (select.length && select.val()) adjustQuantityInput(row, select);
  });
});
