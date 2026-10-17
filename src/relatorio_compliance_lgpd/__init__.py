"""Pacote de mapeamento de dados pessoais e relatório de compliance LGPD."""

from .mapeamento import (
    CampoPessoal,
    FonteDado,
    RelatorioLGPD,
    detectar_tipo_campo,
    gerar_relatorio,
    formatar_relatorio,
    salvar_relatorio,
    varrer_csv,
    varrer_json,
    fontes_sinteticas,
)

__all__ = [
    "CampoPessoal",
    "FonteDado",
    "RelatorioLGPD",
    "detectar_tipo_campo",
    "gerar_relatorio",
    "formatar_relatorio",
    "salvar_relatorio",
    "varrer_csv",
    "varrer_json",
    "fontes_sinteticas",
]
