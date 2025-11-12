from django.db import models
from decimal import Decimal


class SalePayment(models.Model):
    PAYMENT_TYPES = [
        ("CASH", "Dinheiro"),
        ("PIX", "Pix"),
        ("CARD", "Cartão"),
        ("CREDIT", "Crédito"),
        ("DEBIT", "Débito"),
        ("MUMBUCA", "Mumbuca"),
    ]

    sale = models.ForeignKey(
        "Sale",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Venda",
    )

    payment_type = models.CharField(
        max_length=10,
        choices=PAYMENT_TYPES,
        verbose_name="Tipo de Pagamento",
    )

    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor a Pagar",
        help_text="Quanto deste pagamento deveria cobrir da venda."
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Pago",
    )

    change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Troco",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sale_payment"
        verbose_name = "Pagamento de Venda"
        verbose_name_plural = "Pagamentos de Vendas"

    def __str__(self):
        return f"{self.get_payment_type_display()} - Pago: R$ {self.amount_paid:.2f}"

    def save(self, *args, **kwargs):
        if self.payment_type == "CASH":
            self.change = max(self.amount_paid - self.target_value, Decimal("0.00"))
        else:
            self.change = Decimal("0.00")
        super().save(*args, **kwargs)
