# relatorio-compliance-lgpd

## Português (PT-BR)

### O que faz

Mapeia campos de dados pessoais (nome, CPF, e-mail, telefone) em fontes sintéticas CSV e JSON em memória e gera um relatório de compliance LGPD com contagem, localização e classificação de risco (baixo / médio / alto).

É um pacote Python puro, sem dependências externas. É determinístico: mesma entrada produz sempre a mesma saída, sem relógio, sem sorteio e sem rede.

### Como usar

No diretório raiz do projeto:

```
python -m relatorio_compliance_lgpd.mapeamento
```

Imprime o relatório no terminal. Para salvar em arquivo, use a função `salvar_relatorio` do pacote.

### Testes

```
python -m pytest -q
```

Executa a suíte pytest (15 testes). Todos devem passar.

### Estrutura

```
pyproject.toml         # projeto Python (setuptools, layout src)
src/relatorio_compliance_lgpd/mapeamento.py  # varredura e relatório LGPD
src/relatorio_compliance_lgpd/__init__.py    # API pública
tests/test_mapeamento.py                     # suíte pytest
README.md                                      # este arquivo
BRIEF.md                                       # entregas e verificação
```

### Licença

MIT.

### Autor

Kelvin Oliveira.

---

## English (EN)

### What it does

Maps personal data fields (name, CPF, e-mail, phone) in synthetic in-memory CSV and JSON sources and generates an LGPD compliance report with count, location, and risk classification (low / medium / high).

It is a pure Python package with no external dependencies. It is deterministic: the same input always produces the same output, with no clock, no randomness, and no network.

### How to use

In the project root directory:

```
python -m relatorio_compliance_lgpd.mapeamento
```

Prints the report to the terminal. To save to a file, use `salvar_relatorio` from the package.

### Tests

```
python -m pytest -q
```

Runs the pytest suite (15 tests). All must pass.

### Structure

```
pyproject.toml         # Python project (setuptools, src layout)
src/relatorio_compliance_lgpd/mapeamento.py  # LGPD scan and report
src/relatorio_compliance_lgpd/__init__.py    # public API
tests/test_mapeamento.py                     # pytest suite
README.md                                      # this file
BRIEF.md                                       # deliveries and verification
```

### License

MIT.

### Author

Kelvin Oliveira.
