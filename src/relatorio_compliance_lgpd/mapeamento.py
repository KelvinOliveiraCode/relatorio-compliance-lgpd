"""Mapeamento de dados pessoais e relatório de compliance LGPD.

Varre fontes sintéticas (CSV/JSON em memória), detecta campos de dados
pessoais (nome, CPF, e-mail, telefone) e gera um relatório de compliance
com contagem, localização e classificação de risco.

O módulo é determinístico: não usa relógio, não usa sorteio e não faz
chamadas de rede. Todas as fontes de dados são strings fixas em memória.
"""

from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

__all__ = [
    "CampoPessoal",
    "FonteDado",
    "RelatorioLGPD",
    "CSV_CLIENTES",
    "JSON_USUARIOS",
    "detectar_tipo_campo",
    "varrer_csv",
    "varrer_json",
    "gerar_relatorio",
    "formatar_relatorio",
    "salvar_relatorio",
    "fontes_sinteticas",
    "main",
]

# Padrões de nome de campo que indicam dados pessoais (LGPD).
_PADROES_CAMPO: Dict[str, re.Pattern[str]] = {
    "nome": re.compile(
        r"\b(nome|nome_completo|cliente|usuario|usuario_nome)\b", re.IGNORECASE
    ),
    "cpf": re.compile(r"\b(cpf|cpf_cliente|documento_cpf)\b", re.IGNORECASE),
    "email": re.compile(
        r"\b(email|email_cliente|e_mail|correio_eletronico|contato_email)\b",
        re.IGNORECASE,
    ),
    "telefone": re.compile(
        r"\b(telefone|tel|celular|telefone_cliente|contato_telefone)\b",
        re.IGNORECASE,
    ),
}

# Padrões de valor usados para confirmar a ocorrência do dado pessoal.
_PADROES_VALOR: Dict[str, re.Pattern[str]] = {
    "cpf": re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "telefone": re.compile(r"\b\(?\d{2}\)?\s?\d{4,5}-?\d{4}\b"),
}

# Peso de risco por tipo de dado pessoal (identificadores diretos pesam mais).
_PESO_RISCO: Dict[str, int] = {
    "cpf": 40,
    "nome": 25,
    "telefone": 20,
    "email": 15,
}

LIMITE_RISCO_ALTO = 60
LIMITE_RISCO_MEDIO = 30

# Fontes sintéticas em memória (CSV e JSON).
CSV_CLIENTES = """id,nome_completo,cpf,email,telefone,cidade
1,Ana Silva,123.456.789-01,ana@exemplo.com,11 9999-1234,São Paulo
2,Bruno Souza,987.654.321-02,bruno@exemplo.com,21 9888-5678,Rio de Janeiro
3,Carla Dias,111.222.333-44,carla@exemplo.com,11 9777-3333,São Paulo
"""

JSON_USUARIOS = """[
  {"usuario_nome":"Carlos","cpf_cliente":"111.222.333-44","email_cliente":"carlos@x.com","telefone_cliente":"31 9777-3333"},
  {"usuario_nome":"Diana","cpf_cliente":"555.666.777-88","email_cliente":"diana@x.com","telefone_cliente":"31 9666-2222"}
]"""


def detectar_tipo_campo(nome_campo: str) -> Optional[str]:
    """Retorna o tipo de dado pessoal detectado em um nome de campo.

    Args:
        nome_campo: Nome da coluna ou chave a ser avaliada.

    Returns:
        Tipo detectado ('nome', 'cpf', 'email', 'telefone') ou None.
    """
    for tipo, padrao in _PADROES_CAMPO.items():
        if padrao.search(nome_campo):
            return tipo
    return None


def _contar_ocorrencias_valor(tipo: str, valores: Iterable[str]) -> int:
    """Conta valores que confirmam o padrão do tipo de dado pessoal.

    Quando não há padrão de valor para o tipo, retorna o total de valores
    não vazios fornecidos.
    """
    padrao = _PADROES_VALOR.get(tipo)
    if padrao is None:
        return sum(1 for v in valores if v is not None and str(v) != "")
    return sum(1 for v in valores if v is not None and padrao.search(str(v)))


@dataclass
class CampoPessoal:
    """Um campo de dado pessoal encontrado em uma fonte de dados."""

    fonte: str
    campo: str
    tipo: str
    ocorrencias: int = 0
    localizacao: str = ""
    risco: str = ""


@dataclass
class FonteDado:
    """Uma fonte de dados varrida (CSV ou JSON em memória)."""

    nome: str
    formato: str
    linhas: int
    campos_pessoais: List[CampoPessoal] = field(default_factory=list)

    @property
    def total_campos_pessoais(self) -> int:
        return sum(campo.ocorrencias for campo in self.campos_pessoais)


@dataclass
class RelatorioLGPD:
    """Resultado agregado da varredura de compliance LGPD."""

    total_fontes: int = 0
    total_campos_pessoais: int = 0
    campos_por_tipo: Dict[str, int] = field(default_factory=dict)
    fontes: List[FonteDado] = field(default_factory=list)
    risco_geral: str = ""

    @property
    def tem_dados_pessoais(self) -> bool:
        return self.total_campos_pessoais > 0


def varrer_csv(texto_csv: str, nome_fonte: str = "fonte_csv") -> FonteDado:
    """Varre um conteúdo CSV em memória em busca de campos pessoais.

    Args:
        texto_csv: Conteúdo do CSV como string.
        nome_fonte: Identificador da fonte no relatório.

    Returns:
        FonteDado preenchida com os campos pessoais detectados.
    """
    leitor = csv.DictReader(io.StringIO(texto_csv))
    colunas = leitor.fieldnames or []
    linhas = list(leitor)

    campos: List[CampoPessoal] = []
    for coluna in colunas:
        tipo = detectar_tipo_campo(coluna)
        if tipo is None:
            continue
        valores = [
            linha.get(coluna, "")
            for linha in linhas
            if linha.get(coluna) is not None and str(linha.get(coluna, "")) != ""
        ]
        ocorrencias = _contar_ocorrencias_valor(tipo, valores) or len(valores)
        campos.append(
            CampoPessoal(
                fonte=nome_fonte,
                campo=coluna,
                tipo=tipo,
                ocorrencias=ocorrencias,
                localizacao=f"coluna '{coluna}'",
                risco=_classificar_risco(tipo, ocorrencias),
            )
        )

    return FonteDado(
        nome=nome_fonte,
        formato="csv",
        linhas=len(linhas),
        campos_pessoais=campos,
    )


def varrer_json(texto_json: str, nome_fonte: str = "fonte_json") -> FonteDado:
    """Varre um conteúdo JSON em memória em busca de campos pessoais.

    Suporta objeto único ou lista de objetos.

    Args:
        texto_json: Conteúdo do JSON como string.
        nome_fonte: Identificador da fonte no relatório.

    Returns:
        FonteDado preenchida com os campos pessoais detectados.
    """
    dados = json.loads(texto_json)
    registros: List[Dict[str, Any]] = (
        dados if isinstance(dados, list) else [dados]
    )

    colunas: List[str] = []
    vistos: set[str] = set()
    for registro in registros:
        for chave in registro.keys():
            if chave not in vistos:
                vistos.add(chave)
                colunas.append(chave)

    campos: List[CampoPessoal] = []
    for coluna in colunas:
        tipo = detectar_tipo_campo(coluna)
        if tipo is None:
            continue
        valores = [
            str(registro.get(coluna, ""))
            for registro in registros
            if registro.get(coluna) is not None
            and str(registro.get(coluna, "")) != ""
        ]
        ocorrencias = _contar_ocorrencias_valor(tipo, valores) or len(valores)
        campos.append(
            CampoPessoal(
                fonte=nome_fonte,
                campo=coluna,
                tipo=tipo,
                ocorrencias=ocorrencias,
                localizacao=f"chave '{coluna}'",
                risco=_classificar_risco(tipo, ocorrencias),
            )
        )

    return FonteDado(
        nome=nome_fonte,
        formato="json",
        linhas=len(registros),
        campos_pessoais=campos,
    )


def _classificar_risco(tipo: str, ocorrencias: int) -> str:
    """Classifica o risco de um campo com base no tipo e no volume."""
    peso = _PESO_RISCO.get(tipo, 10) * min(ocorrencias, 5)
    if peso >= LIMITE_RISCO_ALTO:
        return "alto"
    if peso >= LIMITE_RISCO_MEDIO:
        return "medio"
    return "baixo"


def gerar_relatorio(fontes: Iterable[FonteDado]) -> RelatorioLGPD:
    """Gera o relatório de compliance LGPD a partir das fontes varridas.

    Args:
        fontes: Iterável de fontes já varridas.

    Returns:
        RelatorioLGPD agregado.
    """
    lista_fontes = list(fontes)
    total_campos = 0
    campos_por_tipo: Dict[str, int] = {}

    for fonte in lista_fontes:
        total_campos += fonte.total_campos_pessoais
        for campo in fonte.campos_pessoais:
            campos_por_tipo[campo.tipo] = (
                campos_por_tipo.get(campo.tipo, 0) + campo.ocorrencias
            )

    peso_total = sum(
        _PESO_RISCO.get(campo.tipo, 10) * campo.ocorrencias
        for fonte in lista_fontes
        for campo in fonte.campos_pessoais
    )
    if peso_total >= LIMITE_RISCO_ALTO:
        risco_geral = "alto"
    elif peso_total >= LIMITE_RISCO_MEDIO:
        risco_geral = "medio"
    else:
        risco_geral = "baixo"

    return RelatorioLGPD(
        total_fontes=len(lista_fontes),
        total_campos_pessoais=total_campos,
        campos_por_tipo=campos_por_tipo,
        fontes=lista_fontes,
        risco_geral=risco_geral,
    )


def formatar_relatorio(relatorio: RelatorioLGPD) -> str:
    """Formata o relatório como texto legível."""

    def linha_risco(campo: CampoPessoal) -> str:
        return (
            f"  [{campo.tipo}] {campo.campo} | ocorrências={campo.ocorrencias} | "
            f"localização={campo.localizacao} | risco={campo.risco}"
        )

    linhas: List[str] = []
    linhas.append("RELATÓRIO DE COMPLIANCE LGPD")
    linhas.append("=" * 40)
    linhas.append(f"Total de fontes varridas: {relatorio.total_fontes}")
    linhas.append(f"Total de campos pessoais: {relatorio.total_campos_pessoais}")
    linhas.append(f"Risco geral: {relatorio.risco_geral.upper()}")
    linhas.append("")
    linhas.append("Campos por tipo:")
    for tipo in sorted(relatorio.campos_por_tipo):
        linhas.append(f"  - {tipo}: {relatorio.campos_por_tipo[tipo]}")
    linhas.append("")
    for fonte in relatorio.fontes:
        linhas.append(
            f"Fonte: {fonte.nome} ({fonte.formato}, {fonte.linhas} linhas)"
        )
        if not fonte.campos_pessoais:
            linhas.append("  Nenhum campo pessoal detectado.")
        for campo in fonte.campos_pessoais:
            linhas.append(linha_risco(campo))
        linhas.append("")
    return "\n".join(linhas)


def salvar_relatorio(relatorio: RelatorioLGPD, caminho: Path) -> None:
    """Salva o relatório formatado em um arquivo de texto."""
    Path(caminho).write_text(formatar_relatorio(relatorio), encoding="utf-8")


def fontes_sinteticas() -> List[FonteDado]:
    """Retorna fontes sintéticas (CSV/JSON em memória) já varridas."""
    return [varrer_csv(CSV_CLIENTES, "clientes.csv"), varrer_json(JSON_USUARIOS, "usuarios.json")]


def main() -> None:
    """Ponto de entrada da CLI: gera e imprime o relatório LGPD."""
    relatorio = gerar_relatorio(fontes_sinteticas())
    print(formatar_relatorio(relatorio))


if __name__ == "__main__":
    main()
