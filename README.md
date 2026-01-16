# Sistema de Gerenciamento de Aluguéis

**Visão Geral**:
- **Descrição**: API em FastAPI para gerenciamento de imóveis, contratos, proprietários, inquilinos, pagamentos e notificações.
- **Tecnologias principais**: FastAPI, SQLAlchemy, Alembic, MySQL (PyMySQL), APScheduler, Firebase (FireStore/Storage), WeasyPrint para PDFs.

**Recursos**:
- **Contratos**: geração e exportação de PDF.
- **Autenticação**: JWT e controles de usuário.
- **Notificações**: agendadas via scheduler.
- **Integração Firebase**: envio/armazenamento (presença de arquivo de credenciais).

**Estrutura do projeto**:
- **`api/`**: código principal da aplicação (rotas, serviços, utils).
- **`alembic/`**: migrações do banco de dados.
- **`requirements.txt`**: dependências do projeto.
- **`FIREBASE_CREDENTIALS_PATH.json`**: credenciais do Firebase (presente no repositório).

Arquivos de referência:
- [api/main.py](api/main.py#L1-L40)
- [requirements.txt](requirements.txt)
- [alembic.ini](alembic.ini)
- [api/scheduler/jobs_runner.py](api/scheduler/jobs_runner.py)

**Pré-requisitos**:
- Python 3.11+ recomendado
- MySQL ou servidor compatível
- Variáveis de ambiente e acesso ao Firebase (se usar integração)

**Instalação (local)**:
1. Criar e ativar ambiente virtual:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Windows CMD
.\.venv\Scripts\activate.bat
```

2. Instalar dependências:

```bash
pip install -r requirements.txt
```

3. Criar arquivo `.env` baseado nas variáveis esperadas (ex.: `ENV`, `DATABASE_URL`, `FIREBASE_CREDENTIALS_PATH`, `SECRET_KEY`, etc.).

Observação: o projeto carrega `.env` automaticamente em `api/main.py`.

**Migrações de banco (Alembic)**:
- Gerar nova migration (após alterar models):

```bash
alembic revision --autogenerate -m "mensagem"
```

- Aplicar migrações:

```bash
alembic upgrade head
```

**Executar a aplicação**:
- Em desenvolvimento (com reload):

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

- Em produção (exemplo):

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Scheduler / Jobs agendados**:
- O scheduler está em [api/scheduler/jobs_runner.py](api/scheduler/jobs_runner.py) e usa `APScheduler` para executar jobs periódicos (notificações, verificações de vencimentos, etc.).
- Para rodar o scheduler isoladamente, execute o módulo dedicado ou integre ao processo principal conforme a arquitetura atual.

**Logs**:
- Logs são gravados na pasta `logs/`.

**Firebase**:
- O projeto usa bibliotecas do Google/Firebase listadas em `requirements.txt`.
- Configure a variável `FIREBASE_CREDENTIALS_PATH` apontando para o arquivo `FIREBASE_CREDENTIALS_PATH.json` ou coloque o arquivo no local esperado.

**Testes**:
- Não há suite de testes automática incluída; recomenda-se adicionar `pytest` e criar testes para rotas e serviços.

**Boas práticas e próximos passos sugeridos**:
- Externalizar configurações sensíveis via variáveis de ambiente ou um cofre de segredos.
- Adicionar CI com checagem de lint e testes automatizados.
- Adicionar um `docker-compose` para facilitar orquestração local (DB + app).
- Criar um `Makefile` ou scripts de gerenciamento (start, migrate, seed).

**Contato / Manutenção**:
- Para dúvidas sobre arquitetura, abra uma issue ou contate o autor do repositório.

---

Se quiser, eu posso:
- Gerar um exemplo de `.env` com as variáveis mais comuns.
- Adicionar um `docker-compose.yml` com MySQL + app.
- Criar scripts `make`/`batch` para facilitar execução local.

Indique qual item prefere que eu faça a seguir.