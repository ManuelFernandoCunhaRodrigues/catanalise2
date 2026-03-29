# CAT Analyzer Pro

Projeto com frontend em React/Vite e backend em FastAPI para analise de CATs.

## O que o backend entrega

- upload de PDF
- extracao de texto com PyMuPDF
- OCR opcional com `pytesseract` para PDFs escaneados
- extracao heuristica dos campos principais
- validacao de dados e consistencia temporal
- comparacao CAT x ART com base simulada
- deteccao de risco documental
- score final de confiabilidade
- feedback inteligente e historico persistido em SQLite

## Como rodar o frontend

```bash
npm install
npm run dev
```

## Como rodar o backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoint principal

- `POST /analyze`

## Exemplo de resposta

```json
{
  "analysis_id": 12,
  "filename": "arquivo.pdf",
  "status": "processado",
  "resultado": {
    "mensagem": "Documento processado com sucesso e score 92 de confiabilidade.",
    "score": 92,
    "nivel": "alto"
  },
  "dados_extraidos": {
    "nome_profissional": "Joao Silva",
    "numero_art": "123456789",
    "data_inicio": "01/01/2023",
    "data_fim": "10/01/2023",
    "descricao_servico": "Execucao de drenagem e pavimentacao",
    "contratante": "Empresa X"
  },
  "validacao": {
    "valid": true,
    "erros": [],
    "alertas": [],
    "inconsistencias": [],
    "score": 100,
    "nivel": "alto"
  },
  "score_confiabilidade": {
    "score": 92,
    "nivel": "alto",
    "justificativa": [],
    "resumo": "Este documento apresenta boa consistencia geral e alto nivel de confiabilidade."
  }
}
```
