# Bíblia TUI — A Bíblia no seu terminal

Leitor da Bíblia ACF rápido, focado e totalmente offline para o terminal.

O **Bíblia TUI** abre uma interface de tela cheia controlada pelo teclado. Navegue pelos 66 livros, abra referências como `João 3:16`, pesquise em toda a Bíblia, mantenha um histórico e exporte trechos em Markdown.

```text
┌ Bíblia ACF ───────────────────────── João 3 ───────────────┐
│                                                            │
│  15  Para que todo aquele que nele crê não pereça...       │
│                                                            │
│  16  Porque Deus amou o mundo de tal maneira que deu...    │
│                                                            │
│  17  Porque Deus enviou o seu Filho ao mundo, não para...  │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ ←/→ capítulo  g referência  / busca  H histórico  ? ajuda  │
└────────────────────────────────────────────────────────────┘
```

## Recursos

- Leitura em tela cheia com quebra de linha adaptável.
- Navegação por livro, capítulo e versículo.
- Abertura por nome, abreviação ou referência completa.
- Pesquisa sem diferenciar maiúsculas, minúsculas ou acentos.
- Histórico das 100 referências abertas mais recentes.
- Restauração automática da última posição.
- Temas escuro, claro e monocromático.
- Cópia do versículo selecionado para a área de transferência.
- Exportação de versículo, intervalo ou capítulo em Markdown.
- Funcionamento offline depois da instalação.
- Nenhuma dependência Python externa.

## Requisitos

- Linux ou outro sistema com suporte a `curses`.
- Python 3.11 ou superior.
- Terminal com pelo menos 36 colunas e 8 linhas.
- Git para clonar o projeto.

## Instalação

```bash
git clone https://github.com/eliel9012/biblia-tui.git
cd biblia-tui
./install.sh
```

O instalador:

1. instala o aplicativo em `~/.local/share/biblia-tui`;
2. obtém o JSON ACF da fonte indicada em [Dados bíblicos](#dados-bíblicos);
3. cria o comando `~/.local/bin/biblia`.

Se `~/.local/bin` ainda não estiver no seu `PATH`, adicione ao arquivo de configuração do shell:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Uso

Abrir na última posição lida:

```bash
biblia
```

Abrir diretamente em uma referência:

```bash
biblia "João 3:16"
biblia "jo 3:16"
biblia "1 Coríntios 13"
biblia "Salmos 23"
```

Usar outro arquivo de dados:

```bash
biblia --data /caminho/para/acf.json
```

Exibir versão:

```bash
biblia --version
```

## Atalhos

| Tecla | Ação |
|---|---|
| `↑` / `↓` ou `k` / `j` | Versículo anterior ou seguinte |
| `PgUp` / `PgDn` | Mover uma página |
| `←` / `→` ou `h` / `l` | Capítulo anterior ou seguinte |
| `Home` / `End` | Primeiro ou último versículo |
| `g` | Abrir uma referência |
| `b` | Escolher livro e capítulo |
| `/` | Pesquisar palavra ou frase |
| `n` / `N` | Próximo ou anterior resultado |
| `H` | Abrir histórico de referências |
| `e` | Exportar trecho em Markdown |
| `y` | Copiar versículo selecionado |
| `t` | Alternar tema |
| `?` | Exibir ajuda |
| `q` | Sair |

## Exportação em Markdown

Dentro do aplicativo, pressione `e` e informe:

```text
João 3:16
João 3:16-18
Salmos 23
```

Os arquivos são gravados por padrão em `~/Bíblia/`.

Também é possível exportar sem abrir a interface:

```bash
biblia --export "João 3:16-18"
biblia --export "Salmos 23" --output salmo-23.md
```

Exemplo de saída:

```markdown
# João 3:16

> **16.** Porque Deus amou o mundo de tal maneira...

— *Almeida Corrigida Fiel (ACF)*
```

## Área de transferência

A tecla `y` tenta, nesta ordem, `wl-copy`, `xclip`, `xsel`, `pbcopy` e `termux-clipboard-set`. Sem uma dessas ferramentas, usa OSC 52 quando o terminal oferece suporte.

O texto copiado inclui versículo, referência e tradução.

## Estado e histórico

O aplicativo grava somente preferências locais:

```text
~/.config/biblia/state.json
~/.config/biblia/history.json
```

O estado contém última posição e tema. O histórico guarda no máximo 100 referências, elimina duplicatas e mantém a mais recente no topo.

## Dados bíblicos

A base usada possui:

- 66 livros;
- 1.189 capítulos;
- 31.106 versículos.

Fonte: repositório [thiagobodruk/biblia](https://github.com/thiagobodruk/biblia), arquivo `json/acf.json`.

O arquivo bíblico não é incorporado ao histórico deste projeto. O repositório de origem não apresentava uma licença detectável pelo GitHub quando este projeto foi criado. Consulte [LICENSE_DATA.md](LICENSE_DATA.md) antes de redistribuir os dados.

## Desenvolvimento

Clonar, obter dados e executar localmente:

```bash
git clone https://github.com/eliel9012/biblia-tui.git
cd biblia-tui
python3 scripts/download_data.py
python3 -m biblia_tui
```

Rodar testes:

```bash
python3 -m unittest discover -v
python3 -m compileall -q biblia_tui tests scripts biblia.py
```

Os testes usam uma base mínima própria; não precisam baixar o texto bíblico.

## Estrutura

```text
biblia-tui/
├── biblia_tui/
│   ├── __main__.py
│   ├── clipboard.py
│   ├── data.py
│   ├── exporter.py
│   ├── references.py
│   ├── storage.py
│   ├── themes.py
│   └── tui.py
├── data/                   # acf.json local, ignorado pelo Git
├── scripts/
├── tests/
├── biblia.py
├── install.sh
├── LICENSE
├── LICENSE_DATA.md
└── README.md
```

## Desinstalação

Remova os arquivos instalados:

```bash
rm "$HOME/.local/bin/biblia"
rm -r "$HOME/.local/share/biblia-tui"
```

Opcionalmente, remova estado e histórico:

```bash
rm -r "$HOME/.config/biblia"
```

## Licença

Código distribuído sob licença [MIT](LICENSE). Dados bíblicos possuem termos separados; veja [LICENSE_DATA.md](LICENSE_DATA.md).

---

**Bíblia TUI** — leitura bíblica direta, simples e sem distrações.
