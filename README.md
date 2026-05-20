# K-GRASP — Knowledge Graph for Game Development Retrospectives

## Visão Geral

**K-GRASP** (Knowledge Graph for Game Retrospective Analysis and Software Practices) é uma ontologia OWL para captura e consulta do conhecimento embutido em post-mortems de projetos de jogos digitais.

O objetivo é estruturar **decisões arquiteturais**, seus **racionais** e **impactos** em dimensões temáticas, possibilitando consultas SPARQL sobre o legado de projetos encerrados.

## Estrutura do Repositório

```
kgrasp/
├── ontologia_kgrasp.ttl     # Ontologia estrutural (classes, propriedades, instâncias fixas)
├── grafo_populado.ttl       # Grafo populado com instâncias de post-mortems
├── queries/
│   └── cq_example.rq       # Competency Questions em SPARQL
├── scripts/
│   └── ingest.py           # Script Python (rdflib) para popular o grafo
└── README.md               # Este arquivo
```

## Namespace

```
http://cos.ufrj.br/kgrasp/games#
```

Prefixo convencional: `kgrasp:`

---

## Classes

| Classe | URI | Descrição |
|--------|-----|-----------|
| `Projeto` | `kgrasp:Projeto` | Projeto de jogo digital analisado no post-mortem |
| `Especialista` | `kgrasp:Especialista` | Profissional que participou das decisões |
| `Decisao` | `kgrasp:Decisao` | Decisão tomada durante o desenvolvimento |
| `Racional` | `kgrasp:Racional` | Justificativa por trás da decisão |
| `Impacto` | `kgrasp:Impacto` | Consequência/efeito da decisão |
| `Dimensao` | `kgrasp:Dimensao` | Dimensão temática de análise |

---

## Propriedades de Objeto

| Propriedade | Domínio → Range | Descrição |
|-------------|-----------------|-----------|
| `conteveDecisao` | `Projeto → Decisao` | Projeto conteve esta decisão |
| `tomouDecisao` | `Especialista → Decisao` | Especialista tomou esta decisão |
| `justificadaPor` | `Decisao → Racional` | Decisão justificada por este racional |
| `gerouImpacto` | `Decisao → Impacto` | Decisão gerou este impacto |
| `pertenceADimensao` | `Decisao ∪ Impacto → Dimensao` | Pertence à dimensão temática |

---

## Instâncias Fixas — Dimensão

As 6 dimensões canônicas são pré-definidas na ontologia:

| Instância | URI | Descrição |
|-----------|-----|-----------|
| Produto | `kgrasp:Produto` | Produto final, mecânicas e design do jogo |
| Organização | `kgrasp:Organizacao` | Estrutura organizacional e gestão |
| Desenvolvimento | `kgrasp:Desenvolvimento` | Processo técnico de desenvolvimento |
| Equipe | `kgrasp:Equipe` | Equipe, habilidades e dinâmicas |
| Recurso | `kgrasp:Recurso` | Recursos financeiros, de tempo e materiais |
| Marketing | `kgrasp:Marketing` | Marketing, divulgação e estratégia de mercado |

---

## Competency Questions (CQ Index)

| ID | Arquivo | Pergunta |
|----|---------|---------|
| CQ-01 | `queries/cq_example.rq` | Qual foi o racional por trás das decisões no projeto X? |

---

## Como Usar

### 1. Populando o grafo (modo interativo)

```bash
cd kgrasp/scripts/
pip install rdflib
python ingest.py --interactive --output ../grafo_populado.ttl
```

### 2. Populando a partir de arquivo ou pasta

```bash
# Processar um único arquivo
python scripts/ingest.py --input post_mortem.txt --output grafo_populado.ttl

# Processar todos os arquivos .txt em uma pasta (Batch Mode)
python scripts/ingest.py --input post_mortem/ --output grafo_populado.ttl
```

### 3. Visualizando o grafo

```bash
# Requer rdflib, networkx e matplotlib
python scripts/visualize.py grafo_populado.ttl kgrasp_populated.png
```

### 4. Consultando o grafo com SPARQL

```bash
# Com Apache Jena ARQ:
arq --data grafo_populado.ttl --query queries/cq_example.rq

# Com Python + rdflib:
python - <<'EOF'
from rdflib import Graph
g = Graph()
g.parse("grafo_populado.ttl", format="turtle")
results = g.query(open("queries/cq_example.rq").read())
for row in results:
    print(row)
EOF
```

### 4. Validando a ontologia

```bash
# Com Apache Jena RIOT:
riot --validate ontologia_kgrasp.ttl
```

---

## Referências

- Programa de Pós-Graduação em Engenharia de Sistemas e Computação — PESC/UFRJ
- K-GRASP Research Project — COS/UFRJ
