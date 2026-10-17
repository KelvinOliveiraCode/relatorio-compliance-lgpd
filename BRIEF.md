# BRIEF — relatorio-compliance-lgpd

## Entregas

Projeto "relatorio-compliance-lgpd" (área Dados/BI): mapeamento de dados pessoais e relatório de compliance LGPD.

Arquivos criados:

- `pyproject.toml` — projeto Python (setuptools, layout `src`, MIT, autor Kelvin Oliveira).
- `src/relatorio_compliance_lgpd/__init__.py` — API pública do pacote.
- `src/relatorio_compliance_lgpd/mapeamento.py` — varredura de fontes sintéticas CSV/JSON em memória; detecção de campos pessoais (nome, CPF, e-mail, telefone); geração do relatório com contagem, localização e risco (baixo / médio / alto); código determinístico, tipado, com docstrings.
- `tests/test_mapeamento.py` — suíte pytest (15 testes).
- `README.md` — documentação bilíngue PT-BR + EN (título, descrição, como usar, testes, licença MIT, autor).
- `BRIEF.md` — este arquivo.

## Como verificar

No diretório raiz do projeto:

```
python -m pytest -q
```

Resultado dos testes: **PASS** — 15 passed (execução verificada em 16/10/2026, Python 3.14.3, pytest 9.1.1).

Caminhos:

- README: `C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\relatorio-compliance-lgpd\README.md`
- BRIEF: `C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\relatorio-compliance-lgpd\BRIEF.md`

Critérios de aceitação atendidos: relatório gerado; testes que passam; README PT/EN completo.
