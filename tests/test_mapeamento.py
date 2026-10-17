"""Suíte de testes do mapeamento de compliance LGPD."""

from relatorio_compliance_lgpd.mapeamento import (
    CampoPessoal,
    FonteDado,
    RelatorioLGPD,
    CSV_CLIENTES,
    JSON_USUARIOS,
    detectar_tipo_campo,
    gerar_relatorio,
    formatar_relatorio,
    salvar_relatorio,
    varrer_csv,
    varrer_json,
    fontes_sinteticas,
)


class TestDetectarTipoCampo:
    """Detecção de tipo por nome de campo."""

    def test_detecta_nome(self):
        assert detectar_tipo_campo("nome_completo") == "nome"
        assert detectar_tipo_campo("usuario") == "nome"

    def test_detecta_cpf(self):
        assert detectar_tipo_campo("cpf") == "cpf"
        assert detectar_tipo_campo("cpf_cliente") == "cpf"

    def test_detecta_email(self):
        assert detectar_tipo_campo("email") == "email"
        assert detectar_tipo_campo("correio_eletronico") == "email"

    def test_detecta_telefone(self):
        assert detectar_tipo_campo("telefone") == "telefone"
        assert detectar_tipo_campo("tel") == "telefone"

    def test_nao_detecta_campo_comum(self):
        assert detectar_tipo_campo("cidade") is None
        assert detectar_tipo_campo("id") is None
        assert detectar_tipo_campo("") is None


class TestVarreCSV:
    """Varredura de conteúdo CSV em memória."""

    def test_detecta_campos_pessoais(self):
        fonte = varrer_csv(CSV_CLIENTES, "clientes.csv")
        assert fonte.formato == "csv"
        assert fonte.linhas == 3
        tipos = {campo.tipo for campo in fonte.campos_pessoais}
        assert tipos == {"nome", "cpf", "email", "telefone"}
        assert fonte.total_campos_pessoais == 12  # 3 linhas × 4 campos

    def test_preenche_ocorrencias_localizacao_risco(self):
        fonte = varrer_csv(CSV_CLIENTES, "clientes.csv")
        campo_cpf = next(c for c in fonte.campos_pessoais if c.tipo == "cpf")
        assert campo_cpf.ocorrencias == 3
        assert campo_cpf.localizacao == "coluna 'cpf'"
        assert campo_cpf.risco == "alto"


class TestVarreJSON:
    """Varredura de conteúdo JSON em memória."""

    def test_detecta_campos_pessoais_lista(self):
        fonte = varrer_json(JSON_USUARIOS, "usuarios.json")
        assert fonte.formato == "json"
        assert fonte.linhas == 2
        tipos = {campo.tipo for campo in fonte.campos_pessoais}
        assert tipos == {"nome", "cpf", "email", "telefone"}

    def test_detecta_campos_pessoais_objeto_unico(self):
        objeto = '{"nome":"Eva","email":"eva@x.com"}'
        fonte = varrer_json(objeto, "unico.json")
        tipos = {campo.tipo for campo in fonte.campos_pessoais}
        assert tipos == {"nome", "email"}
        assert fonte.linhas == 1


class TestGerarRelatorio:
    """Geração e agregação do relatório."""

    def test_agrega_fontes(self):
        fontes = fontes_sinteticas()
        relatorio = gerar_relatorio(fontes)
        assert relatorio.total_fontes == 2
        assert relatorio.total_campos_pessoais == 20  # 12 (csv) + 8 (json)
        assert relatorio.campos_por_tipo["cpf"] == 5
        assert relatorio.campos_por_tipo["nome"] == 5
        assert relatorio.campos_por_tipo["email"] == 5
        assert relatorio.campos_por_tipo["telefone"] == 5
        assert relatorio.tem_dados_pessoais

    def test_risco_geral_alto(self):
        fontes = fontes_sinteticas()
        relatorio = gerar_relatorio(fontes)
        assert relatorio.risco_geral == "alto"

    def test_risco_geral_baixo_sem_dados(self):
        vazia = FonteDado(nome="vazia.csv", formato="csv", linhas=0)
        relatorio = gerar_relatorio([vazia])
        assert relatorio.total_campos_pessoais == 0
        assert relatorio.risco_geral == "baixo"
        assert not relatorio.tem_dados_pessoais


class TestFormatarESalvarRelatorio:
    """Formatação e persistência do relatório."""

    def test_formatacao_contem_cabecalho(self):
        relatorio = gerar_relatorio(fontes_sinteticas())
        texto = formatar_relatorio(relatorio)
        assert "RELATÓRIO DE COMPLIANCE LGPD" in texto
        assert "Risco geral: ALTO" in texto
        assert "clientes.csv" in texto
        assert "usuarios.json" in texto

    def test_salva_em_arquivo(self, tmp_path):
        relatorio = gerar_relatorio(fontes_sinteticas())
        destino = tmp_path / "relatorio.txt"
        salvar_relatorio(relatorio, destino)
        conteúdo = destino.read_text(encoding="utf-8")
        assert "RELATÓRIO DE COMPLIANCE LGPD" in conteúdo


class TestDeterminismo:
    """O módulo deve ser determinístico (mesma entrada, mesma saída)."""

    def test_duas_varreduras_sao_iguais(self):
        fontes_a = fontes_sinteticas()
        fontes_b = fontes_sinteticas()
        relatorio_a = gerar_relatorio(fontes_a)
        relatorio_b = gerar_relatorio(fontes_b)
        assert relatorio_a.total_campos_pessoais == relatorio_b.total_campos_pessoais
        assert relatorio_a.risco_geral == relatorio_b.risco_geral
        assert formatar_relatorio(relatorio_a) == formatar_relatorio(relatorio_b)
