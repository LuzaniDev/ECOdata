# ECOdata

Sistema de integração Tradefy — geração de arquivos **ESTOQUE**, **SELLOUT** e **PAINEL** com envio SFTP, agendamento e dashboard.

## Stack

- **Backend:** Python 3.12 / FastAPI / SQLAlchemy / SQLite
- **Banco de dados:** Firebird (geradores) + SQLite (app)
- **Frontend:** Vue 3 + TypeScript + Vite + Tailwind CSS + ECharts
- **Infra:** Docker / GitHub Actions

## Quick Start

```bash
# 1. Clone
git clone <repo> && cd ECOdata

# 2. Ambiente virtual
python -m venv .venv && .venv\Scripts\activate

# 3. Dependências
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Preencha DB_HOST, DB_PATH, DB_USER, DB_PASSWORD (Firebird)

# 5. Iniciar
python -m server.app
```

Ou via executável (recomendado para produção):
```bash
run_exe.py
```
(O executável inicia o serviço Firebird, cria diretórios e sobe o servidor.)

Acesse `http://localhost:8580`.

A API Key é gerada automaticamente na primeira execução e salva em `data/.api_key`.

## Estrutura

```
src/                    # Geradores + integração Firebird/SFTP
  generators/           # estoque.py, sellout.py, painel.py
  db.py                 # Pool Firebird
  sftp.py               # Envio SFTP com retry
  config.py             # Configurações via env vars
server/                 # API FastAPI
  api/                  # Rotas (dashboard, files, scheduler, ...)
  core/                 # Auth, database, executor, audit, scheduler
  static/               # Frontend compilado
tests/                  # Testes pytest
```

## API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/health` | Health check (público) |
| POST | `/api/auth/verify` | Verificar API Key |
| GET | `/api/dashboard/kpis` | KPIs do dashboard |
| GET | `/api/scheduler` | Listar agendamentos |
| POST | `/api/scheduler` | Criar agendamento |
| GET | `/api/files` | Listar arquivos gerados |
| GET | `/api/files/preview` | Preview de arquivo |
| GET | `/api/files/download` | Download de arquivo |
| DELETE | `/api/files` | Excluir arquivo |
| POST | `/api/files/resend` | Reenvio SFTP |
| GET | `/api/logs` | Logs do sistema |
| GET | `/api/config` | Configurações |
| PUT | `/api/config` | Atualizar configuração |
| POST | `/api/backup` | Criar backup |
| GET | `/api/auditoria` | Auditoria de alterações |
| POST | `/api/executar/{tipo}` | Executar gerador |

Autenticação: `Authorization: Bearer <api_key>` ou `X-API-Key: <api_key>`

## Testes

```bash
pytest tests/ -v
```

## Docker

```bash
docker-compose up -d
```

## CI/CD

- **CI:** Ruff + mypy + pytest (push/PR para main)
- **CD:** Build Docker image em push de tag `v*`

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `DB_HOST` | Host Firebird |
| `DB_PATH` | Caminho do banco Firebird |
| `DB_USER` | Usuário Firebird |
| `DB_PASSWORD` | Senha Firebird |
| `CODIGO_EMPRESA` | Código da empresa (01) |
| `CNPJ_DISTRIBUIDOR` | CNPJ do distribuidor (opcional) |
| `CNPJ_INDUSTRIA` | CNPJ da indústria (opcional) |
| `SFTP_HOST` | Host SFTP |
| `SFTP_PORT` | Porta SFTP (2222) |
| `SFTP_USER` | Usuário SFTP |
| `SFTP_PASSWORD` | Senha SFTP |
| `SFTP_REMOTE_DIR` | Diretório remoto SFTP (/) |
| `SFTP_HOST_KEY` | Fingerprint SHA256 do host SFTP |
| `OUTPUT_DIR` | Diretório de saída dos arquivos (output) |
| `CORS_ORIGINS` | Origens CORS |
| `ECODATA_HOST` | Host do servidor (0.0.0.0) |
| `ECODATA_PORT` | Porta do servidor (8580) |
| `SMTP_HOST` | Servidor SMTP (notificação) |
| `SMTP_PORT` | Porta SMTP (587) |
| `SMTP_USER` | Usuário SMTP |
| `SMTP_PASSWORD` | Senha SMTP |
| `NOTIFY_EMAILS` | E-mails para notificação |
| `LOG_LEVEL` | Nível de log (INFO) |
