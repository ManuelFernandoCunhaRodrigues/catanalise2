# Backend CAT - MVP minimo

Backend simples em FastAPI para receber um PDF de CAT, processar o upload, comparar CAT x ART, salvar historico e expor uma carga pronta para demonstracao.

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
    processor.py
```

## Instalacao

```bash
pip install fastapi uvicorn python-multipart
```

Ou usando o arquivo de dependencias:

```bash
pip install -r requirements.txt
```

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

Retorna uma carga fixa para demonstracoes guiadas do produto.

### `POST /analyze`

Recebe um arquivo PDF em `multipart/form-data` no campo `file`.

```json
{
  "filename": "arquivo.pdf",
  "status": "processado",
  "resultado": {
    "mensagem": "Documento recebido com sucesso",
    "score": 85,
    "nivel": "medio"
  }
}
```

Toda analise enviada para esse endpoint e salva automaticamente no SQLite.

### `GET /history`

Retorna o historico resumido das analises salvas.

### `GET /history/{id}`

Retorna todos os dados de uma analise especifica.

### `POST /compare-cat-art`

Compara uma CAT com uma ART informada manualmente ou buscada automaticamente na base simulada.

## Regras basicas do MVP

- aceita apenas arquivos `.pdf`
- rejeita arquivo vazio
- salva o arquivo na pasta `uploads/`
- salva a analise em `database.db`
- retorna analise simulada pronta para integracao futura com IA
- compara CAT e ART com base simulada para auditoria documental

## Observacao

O metodo `process_file` ja usa `async/await` e foi organizado para facilitar a troca da simulacao por uma analise real depois.
O banco SQLite usa `sqlite3` nativo com queries parametrizadas, JSON string para listas e historico auditavel.
