# Backend CAT

Backend em FastAPI para receber uma CAT em PDF, extrair informacoes, validar o documento, comparar com ART, calcular score de confiabilidade e persistir o historico.

## Estrutura

```text
backend/
  database/
    db.py
    models.py
    repository.py
  database.db
  main.py
  requirements.txt
  services/
    art_integration.py
    extractor.py
    feedback.py
    fraud_detector.py
    parser.py
    processor.py
    scorer.py
    validator.py
```

## Instalacao

```bash
pip install -r requirements.txt
```

OCR com `pytesseract` continua opcional. Quando o binario do Tesseract nao estiver instalado, o backend segue funcionando para PDFs com camada de texto.

## Como rodar

```bash
uvicorn main:app --reload
```

## Endpoints

### `GET /`

```json
{
  "status": "API rodando"
}
```

### `GET /demo`

Retorna um payload fixo para apresentacoes guiadas.

### `POST /analyze`

Recebe um arquivo PDF em `multipart/form-data` no campo `file` e retorna um payload completo com:

- dados extraidos
- validacao
- comparacao CAT x ART
- deteccao de fraude
- score de confiabilidade
- feedback inteligente

Toda analise enviada para esse endpoint e salva automaticamente no SQLite.

### `GET /history`

Retorna o historico resumido das analises salvas.

### `GET /history/{id}`

Retorna os detalhes da analise, incluindo o payload completo persistido.

### `POST /compare-cat-art`

Compara uma CAT com uma ART informada manualmente ou buscada automaticamente na base simulada.

## Regras basicas

- aceita apenas arquivos `.pdf`
- rejeita arquivo vazio
- rejeita arquivo acima de 10 MB
- salva o arquivo na pasta `uploads/`
- salva a analise em `database.db`
- usa queries parametrizadas no SQLite
- restringe CORS por configuracao para evitar `*` com credenciais
