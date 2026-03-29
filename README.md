# CAT Analyzer Pro

Projeto com frontend em React/Vite e backend em FastAPI para análise de CATs.

## Backend MVP

O backend fica em [backend/](backend/README.md) e implementa:

- upload de PDF
- extração de texto com PyMuPDF
- OCR opcional com pytesseract para PDFs escaneados
- extração heurística de campos principais
- validação inteligente
- score final de qualidade

### Rodar o backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Endpoint principal

- `POST /analyze`

### Resposta

```json
{
  "texto_extraido": "...",
  "campos": {
    "nome_profissional": "...",
    "numero_art": "...",
    "data_execucao": "...",
    "descricao_servico": "..."
  },
  "validacao": {
    "valid": true,
    "erros": [],
    "alertas": []
  },
  "score": {
    "score": 100,
    "nivel": "alto"
  }
}
```
