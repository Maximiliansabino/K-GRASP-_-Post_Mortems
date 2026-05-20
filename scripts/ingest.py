#!/usr/bin/env python3
"""
K-GRASP Ingest Script
Populates the K-GRASP knowledge graph from post-mortem data.

Usage:
    python ingest.py --interactive --output ../grafo_populado.ttl
    python ingest.py --input post_mortem.txt --output ../grafo_populado.ttl

Dependencies:
    pip install rdflib
"""

from __future__ import annotations

import argparse
import re
import uuid

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

# ---------------------------------------------------------------------------
# Namespace
# ---------------------------------------------------------------------------

KGRASP = Namespace("http://cos.ufrj.br/kgrasp/games#")

# ---------------------------------------------------------------------------
# Canonical Dimensao instances (fixed in the ontology)
# ---------------------------------------------------------------------------

DIMENSOES: dict[str, URIRef] = {
    "produto":        KGRASP.Produto,
    "organização":    KGRASP.Organizacao,
    "organizacao":    KGRASP.Organizacao,
    "desenvolvimento": KGRASP.Desenvolvimento,
    "equipe":         KGRASP.Equipe,
    "recurso":        KGRASP.Recurso,
    "marketing":      KGRASP.Marketing,
}


# ---------------------------------------------------------------------------
# Graph helpers
# ---------------------------------------------------------------------------

def create_base_graph() -> Graph:
    """Return a new RDF graph with K-GRASP namespace bindings and ontology header."""
    g = Graph()
    g.bind("kgrasp", KGRASP)
    g.bind("rdf",  RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl",  OWL)
    g.bind("xsd",  XSD)

    onto = URIRef("http://cos.ufrj.br/kgrasp/games/populated")
    g.add((onto, RDF.type,       OWL.Ontology))
    g.add((onto, OWL.imports,    URIRef("http://cos.ufrj.br/kgrasp/games")))
    g.add((onto, RDFS.label,     Literal("K-GRASP Grafo Populado", lang="pt")))
    g.add((onto, RDFS.comment,   Literal(
        "Grafo de conhecimento populado a partir de post-mortems de projetos de jogos.", lang="pt"
    )))
    return g


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_]", "_", text.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug


def _make_uri(prefix: str, label: str) -> URIRef:
    slug = _slugify(label[:40])
    uid  = uuid.uuid4().hex[:8]
    return KGRASP[f"{prefix}_{slug}_{uid}"]


def add_projeto(g: Graph, nome: str) -> URIRef:
    uri = _make_uri("projeto", nome)
    g.add((uri, RDF.type,     KGRASP.Projeto))
    g.add((uri, RDFS.label,   Literal(nome, lang="pt")))
    return uri


def add_especialista(g: Graph, nome: str) -> URIRef:
    uri = _make_uri("especialista", nome)
    g.add((uri, RDF.type,     KGRASP.Especialista))
    g.add((uri, RDFS.label,   Literal(nome, lang="pt")))
    return uri


def add_decisao(
    g: Graph,
    descricao: str,
    projeto_uri: URIRef,
    especialista_uri: URIRef | None = None,
    dimensao_key: str | None = None,
    racional_texto: str | None = None,
    impacto_texto: str | None = None,
) -> URIRef:
    """Add a Decisao with optional Racional and Impacto to the graph."""
    decisao_uri = _make_uri("decisao", descricao)
    g.add((decisao_uri, RDF.type,   KGRASP.Decisao))
    g.add((decisao_uri, RDFS.label, Literal(descricao, lang="pt")))

    # Links
    g.add((projeto_uri, KGRASP.conteveDecisao, decisao_uri))
    if especialista_uri:
        g.add((especialista_uri, KGRASP.tomouDecisao, decisao_uri))

    # Dimensao
    if dimensao_key:
        dim_uri = DIMENSOES.get(dimensao_key.strip().lower())
        if dim_uri:
            g.add((decisao_uri, KGRASP.pertenceADimensao, dim_uri))

    # Racional
    if racional_texto:
        r_uri = _make_uri("racional", racional_texto)
        g.add((r_uri, RDF.type,   KGRASP.Racional))
        g.add((r_uri, RDFS.label, Literal(racional_texto, lang="pt")))
        g.add((decisao_uri, KGRASP.justificadaPor, r_uri))

    # Impacto
    if impacto_texto:
        i_uri = _make_uri("impacto", impacto_texto)
        g.add((i_uri, RDF.type,   KGRASP.Impacto))
        g.add((i_uri, RDFS.label, Literal(impacto_texto, lang="pt")))
        g.add((decisao_uri, KGRASP.gerouImpacto, i_uri))

    return decisao_uri


# ---------------------------------------------------------------------------
# Interactive session
# ---------------------------------------------------------------------------

def interactive_session(output_path: str) -> None:
    print("K-GRASP Interactive Ingest Session")
    print("=" * 40)
    g = create_base_graph()

    projeto_nome = input("Nome do projeto: ").strip()
    if not projeto_nome:
        print("Nenhum projeto informado. Encerrando.")
        return
    projeto_uri = add_projeto(g, projeto_nome)

    while True:
        print("\n--- Nova Decisão (deixe em branco para encerrar) ---")
        descricao = input("Descrição da decisão: ").strip()
        if not descricao:
            break

        esp_nome = input("Especialista responsável (opcional): ").strip()
        esp_uri  = add_especialista(g, esp_nome) if esp_nome else None

        print(f"Dimensões disponíveis: {', '.join(DIMENSOES)}")
        dim_key  = input("Dimensão (opcional): ").strip() or None
        racional = input("Racional/Justificativa (opcional): ").strip() or None
        impacto  = input("Impacto (opcional): ").strip() or None

        add_decisao(
            g, descricao, projeto_uri,
            especialista_uri=esp_uri,
            dimensao_key=dim_key,
            racional_texto=racional,
            impacto_texto=impacto,
        )
        print("Decisão adicionada.")

    g.serialize(destination=output_path, format="turtle")
    print(f"\nGrafo salvo em: {output_path}  ({len(g)} triplas)")


# ---------------------------------------------------------------------------
# Text-file ingestion (stub — wire NLP pipeline here)
# ---------------------------------------------------------------------------

def ingest_from_file(input_path: str, output_path: str) -> None:
    print(f"Ingesting from: {input_path}")
    g = create_base_graph()
    
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return

    # Heuristic: Find Projeto name (fallback to filename if not found)
    projeto_match = re.search(r"Projeto:\s*(.*)", content, re.IGNORECASE)
    if projeto_match:
        projeto_nome = projeto_match.group(1).strip()
    else:
        projeto_nome = input_path.split("/")[-1].split(".")[0]
        print(f"Aviso: 'Projeto:' não encontrado. Usando nome do arquivo: {projeto_nome}")
    
    projeto_uri = add_projeto(g, projeto_nome)

    # Split into blocks (separated by --- or double newlines)
    blocks = re.split(r"\n\s*---\s*\n|\n\n+", content)
    
    count = 0
    for block in blocks:
        if not block.strip():
            continue
            
        # Extract fields using regex
        dec_m = re.search(r"(?:Decis[ãa]o|Decision):\s*(.*)", block, re.IGNORECASE)
        if not dec_m:
            continue
            
        desc = dec_m.group(1).strip()
        
        esp_m = re.search(r"(?:Especialista|Specialist|By):\s*(.*)", block, re.IGNORECASE)
        dim_m = re.search(r"(?:Dimens[ãa]o|Dimension):\s*(.*)", block, re.IGNORECASE)
        rac_m = re.search(r"(?:Racional|Rationale|Why):\s*(.*)", block, re.IGNORECASE)
        imp_m = re.search(r"(?:Impacto|Impact):\s*(.*)", block, re.IGNORECASE)
        
        esp_nome = esp_m.group(1).strip() if esp_m else None
        esp_uri = add_especialista(g, esp_nome) if esp_nome else None
        dim_key = dim_m.group(1).strip() if dim_m else None
        rac_text = rac_m.group(1).strip() if rac_m else None
        imp_text = imp_m.group(1).strip() if imp_m else None
        
        add_decisao(
            g, desc, projeto_uri,
            especialista_uri=esp_uri,
            dimensao_key=dim_key,
            racional_texto=rac_text,
            impacto_texto=imp_text
        )
        count += 1

    g.serialize(destination=output_path, format="turtle")
    print(f"Ingestão concluída: {count} decisões importadas.")
    print(f"Grafo salvo em: {output_path} ({len(g)} triplas)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="K-GRASP: populate the RDF knowledge graph from post-mortem data"
    )
    parser.add_argument("--input",       help="Path to post-mortem text file or directory")
    parser.add_argument("--output",      default="grafo_populado.ttl",
                        help="Output Turtle file (default: grafo_populado.ttl)")
    parser.add_argument("--interactive", action="store_true",
                        help="Run in interactive ingestion mode")
    args = parser.parse_args()

    if args.interactive or not args.input:
        interactive_session(args.output)
    else:
        import os
        if os.path.isdir(args.input):
            print(f"Batch processing directory: {args.input}")
            g = create_base_graph()
            # We need to merge all files into one graph or handle them separately.
            # Merging into one graph is better for the final output.
            
            # Re-implement batch logic here to share the same Graph object
            files = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.endswith(".txt")]
            total_count = 0
            for input_file in files:
                print(f"Processing: {input_file}")
                # We'll use a modified version of ingest_from_file that takes a graph
                count = _ingest_to_graph(input_file, g)
                total_count += count
            
            g.serialize(destination=args.output, format="turtle")
            print(f"Ingestão batch concluída: {total_count} decisões importadas de {len(files)} arquivos.")
            print(f"Grafo salvo em: {args.output} ({len(g)} triplas)")
        else:
            ingest_from_file(args.input, args.output)

def _ingest_to_graph(input_path: str, g: Graph) -> int:
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Erro ao ler arquivo {input_path}: {e}")
        return 0

    # Heuristic: Find Projeto name
    projeto_match = re.search(r"Projeto:\s*(.*)", content, re.IGNORECASE)
    if projeto_match:
        projeto_nome = projeto_match.group(1).strip()
    else:
        projeto_nome = input_path.split("/")[-1].split(".")[0]
    
    projeto_uri = add_projeto(g, projeto_nome)

    blocks = re.split(r"\n\s*---\s*\n|\n\n+", content)
    count = 0
    for block in blocks:
        if not block.strip():
            continue
        dec_m = re.search(r"(?:Decis[ãa]o|Decision):\s*(.*)", block, re.IGNORECASE)
        if not dec_m:
            continue
        desc = dec_m.group(1).strip()
        esp_m = re.search(r"(?:Especialista|Specialist|By):\s*(.*)", block, re.IGNORECASE)
        dim_m = re.search(r"(?:Dimens[ãa]o|Dimension):\s*(.*)", block, re.IGNORECASE)
        rac_m = re.search(r"(?:Racional|Rationale|Why):\s*(.*)", block, re.IGNORECASE)
        imp_m = re.search(r"(?:Impacto|Impact):\s*(.*)", block, re.IGNORECASE)
        
        esp_nome = esp_m.group(1).strip() if esp_m else None
        esp_uri = add_especialista(g, esp_nome) if esp_nome else None
        dim_key = dim_m.group(1).strip() if dim_m else None
        rac_text = rac_m.group(1).strip() if rac_m else None
        imp_text = imp_m.group(1).strip() if imp_m else None
        
        add_decisao(
            g, desc, projeto_uri,
            especialista_uri=esp_uri,
            dimensao_key=dim_key,
            racional_texto=rac_text,
            impacto_texto=imp_text
        )
        count += 1
    return count


if __name__ == "__main__":
    main()
