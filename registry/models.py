from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=64)

    def __str__(self):
        return self.nome


class Commessa(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    # is it a number and does it have to unique?
    numero = models.IntegerField(unique=True)
    # default today?
    data = models.DateField()
    valore = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valore IVA inclusa"
    )
    valore_excluded = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valore IVA esclusa"
    )
    nota_valore = models.TextField(blank=True, default="")
    # TODO: this has to be calculated, make it read only in admin panel
    #  it will be composed of the sum of the integrations + commessa's valore
    totale_valore = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Imponibile + IVA"
    )

    def __str__(self):
        return f"Commessa numero {self.numero}"


class Sottocommessa(models.Model):
    commessa = models.ForeignKey(
        Commessa, related_name="sottocommesse", on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=64)

    class Meta:
        unique_together = ("commessa", "nome")


# TODO: max five of these per one Commessa
class Integrazione(models.Model):
    commessa = models.ForeignKey(Commessa, on_delete=models.CASCADE)
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    nota = models.TextField(blank=True, default="")


class PagamentoCommessa(models.Model):
    commessa = models.ForeignKey(
        Commessa, related_name="pagamenti_commessa", on_delete=models.CASCADE
    )
    # default today?
    data = models.DateField()
    imponibile = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Importo senza IVA"
    )
    imponibile_ivato = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Imponibile + IVA"
    )
    nome = models.CharField(max_length=64)


class IVA(models.Model):
    nome = models.CharField(max_length=32)
    value = models.DecimalField(max_digits=10, decimal_places=2)


class Fornitore(models.Model):
    nome = models.CharField(max_length=64)
    # TODO add more fields


# class TipoPagamento()
# RIBA
# bonifico bancario
# altro


class Costo(models.Model):
    # TODO add an easy way to filter by commessa
    sottocommessa = models.ForeignKey(Sottocommessa, on_delete=models.CASCADE)
    fornitore = models.ForeignKey(Fornitore, on_delete=models.CASCADE)
    descrizione = models.TextField(blank=True, default="")
    data = models.DateField()
    fattura = models.CharField(max_length=128)
    scadenza_pagamento = models.DateField()
    tipo_pagamento = models.CharField(max_length=64)
