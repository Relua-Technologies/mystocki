$(window).on("load", function () {
  const FORMSET_PREFIX = "sale_payments";

  function parseNumber(value) {
    const number = parseFloat(value);
    return Number.isFinite(number) ? number : 0;
  }

  function updateChange(row) {
    const paymentType = row.find(`select[name$="-payment_type"]`).val();
    const targetValue = parseNumber(row.find(`input[name$="-target_value"]`).val());
    const amountPaid = parseNumber(row.find(`input[name$="-amount_paid"]`).val());
    const $changeInput = row.find(`input[name$="-change"]`);

    let change = 0;
    if (paymentType === "CASH" && amountPaid > targetValue) {
      change = amountPaid - targetValue;
    }
    $changeInput.val(change.toFixed(2));
    updateSalePaymentTotals();
  }

  function updateSalePaymentTotals() {
    let totalTarget = 0;
    let totalPaid = 0;

    $(`input[name^="${FORMSET_PREFIX}-"][name$="-target_value"]`).each(function () {
      totalTarget += parseNumber($(this).val());
    });

    $(`input[name^="${FORMSET_PREFIX}-"][name$="-amount_paid"]`).each(function () {
      totalPaid += parseNumber($(this).val());
    });

    const $summary = $("#sale-payment-summary");
    if ($summary.length) {
      $summary.html(`
        <div class="mt-2 text-sm text-gray-700">
          <strong>Total a Pagar:</strong> R$ ${totalTarget.toFixed(2)} <br>
          <strong>Total Pago:</strong> R$ ${totalPaid.toFixed(2)} <br>
          <strong>Diferença:</strong> R$ ${(totalPaid - totalTarget).toFixed(2)}
        </div>
      `);
    }
  }

  function initializeExistingRows() {
    $(".dynamic-form").each(function () {
      const row = $(this);
      const paymentType = row.find(`select[name^="${FORMSET_PREFIX}-"][name$="-payment_type"]`).val();
      if (paymentType) updateChange(row);
    });
  }

  $(document).on(
    "input change",
    `select[name^="${FORMSET_PREFIX}-"][name$="-payment_type"],
     input[name^="${FORMSET_PREFIX}-"][name$="-target_value"],
     input[name^="${FORMSET_PREFIX}-"][name$="-amount_paid"]`,
    function () {
      const row = $(this).closest(".dynamic-form");
      updateChange(row);
    }
  );

  $(document).on(`${FORMSET_PREFIX}:form-added`, function (_event, row) {
    row.find(`select[name$="-payment_type"], input[name$="-target_value"], input[name$="-amount_paid"]`).on(
      "input change",
      function () {
        updateChange(row);
      }
    );
  });

  initializeExistingRows();
  setTimeout(initializeExistingRows, 300);
});
