from datetime import date

from django.contrib import admin

from registry.models import (
    Cliente,
    Commessa,
    Costo,
    Fornitore,
    Integrazione,
    PagamentoCommessa,
    Sottocommessa,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome",)


class SottocommessaInline(admin.TabularInline):
    model = Sottocommessa


class PagamentoCommessaInline(admin.TabularInline):
    model = PagamentoCommessa


class IntegrazioneInline(admin.TabularInline):
    model = Integrazione


@admin.register(Commessa)
class CommessaAdmin(admin.ModelAdmin):
    list_display = ("numero", "data", "valore", "nota_valore", "totale_valore")
    inlines = [PagamentoCommessaInline, SottocommessaInline, IntegrazioneInline]

    # TODO: pagamenti dopo totale
    # fieldsets = (
    #     (
    #         None,
    #         {"fields": ("numero", "data", "valore", "nota_valore", "totale_valore")},
    #     ),
    # )


# TODO: check on the ordering of the sidebar menu


@admin.register(Sottocommessa)
class SottocommessaAdmin(admin.ModelAdmin):
    list_display = ("commessa", "nome")


@admin.register(Fornitore)
class FornitoreAdmin(admin.ModelAdmin):
    list_display = ("nome",)


@admin.register(Costo)
class CostoAdmin(admin.ModelAdmin):
    raw_id_fields = ("sottocommessa",)
    list_display = (
        "sottocommessa",
        "fornitore",
        "data",
        "fattura",
        "scadenza_pagamento",
        "tipo_pagamento",
        "get_pagamento_scaduto"
    )
    list_filter = ("scadenza_pagamento", )

    def get_pagamento_scaduto(self, obj: Costo):
        return obj.scadenza_pagamento < date.today()

    get_pagamento_scaduto.description = 'pagamento_scaduto'
    get_pagamento_scaduto.boolean = True


# TODO add costo aggregated
