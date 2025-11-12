$(window).on("load", function () {
  const FORMSET_PREFIX = "sale_payments";

  function parseNumber(value) {
    const number = parseFloat(value);
    return Number.isFinite(number) ? number : 0;
  }

  // retorna TODAS as linhas do formset com base nos inputs target_value
  function getAllRows() {
    const rows = [];
    $(`input[name^="${FORMSET_PREFIX}-"][name$="-target_value"]`).each(function () {
      const row = $(this).closest(".dynamic-form");
      if (row.length) rows.push(row);
    });
    return rows;
  }

  function getTotalSaleValue() {
    const $total = $('input[name="total"]');
    return $total.length ? parseNumber($total.val()) : 0;
  }

  function calculateRemainingFor(targetRow) {
    const total = getTotalSaleValue();
    let sumOthers = 0;

    getAllRows().forEach(function (row) {
      if (row[0] !== targetRow[0]) {
        const val = parseNumber(row.find(`input[name$="-target_value"]`).val());
        sumOthers += val;
      }
    });

    console.log(total)
    return Math.max(total - sumOthers, 0);
  }

  function updateTargetValueLimit(row) {
    const $target = row.find(`input[name$="-target_value"]`);
    const maxAllowed = calculateRemainingFor(row);
    const current = parseNumber($target.val());

    $target.attr("max", maxAllowed);
    $target.attr("placeholder", `Máx: ${maxAllowed.toFixed(2)}`);

    if (current > maxAllowed) {
      $target.val(maxAllowed.toFixed(2)).trigger("input");
    }
  }

  function updateChange(row) {
    const type = row.find(`select[name$="-payment_type"]`).val();
    const target = parseNumber(row.find(`input[name$="-target_value"]`).val());
    const paid = parseNumber(row.find(`input[name$="-amount_paid"]`).val());
    const $change = row.find(`input[name$="-change"]`);

    const change = type === "CASH" && paid > target ? (paid - target) : 0;
    $change.val(change.toFixed(2));
  }

  function updateAllOtherRowsLimits(exceptRow) {
    getAllRows().forEach(function (row) {
      if (row[0] !== exceptRow[0]) updateTargetValueLimit(row);
    });
  }

  // listeners
  $(document).on(
    "input change",
    `input[name^="${FORMSET_PREFIX}-"][name$="-target_value"],
     input[name^="${FORMSET_PREFIX}-"][name$="-amount_paid"],
     select[name^="${FORMSET_PREFIX}-"][name$="-payment_type"]`,
    function () {
      const row = $(this).closest(".dynamic-form");
      updateChange(row);
      updateAllOtherRowsLimits(row);
    }
  );

  $(document).on(`${FORMSET_PREFIX}:form-added`, function (_e, row) {
    updateTargetValueLimit(row);
    updateChange(row);
    row.find(
      `input[name$="-target_value"], input[name$="-amount_paid"], select[name$="-payment_type"]`
    ).on("input change", function () {
      const inner = $(this).closest(".dynamic-form");
      updateChange(inner);
      updateAllOtherRowsLimits(inner);
    });
  });

  // init
  (function initialize() {
    const rows = getAllRows();
    rows.forEach(updateTargetValueLimit);
    rows.forEach(updateChange);
    // re-checa após hidratações/leitura de valores
    setTimeout(() => {
      const again = getAllRows();
      again.forEach(updateTargetValueLimit);
      again.forEach(updateChange);
    }, 300);
  })();
});
