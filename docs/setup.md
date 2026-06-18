# Guia de Instalação

## Pré-requisitos

- Python 3.12+
- Firebird 2.5+ (servidor com banco de dados configurado)
- Acesso ao SFTP da Tradefy (opcional para testes)

## Instalação Local

```bash
# 1. Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.venv\Scripts\activate
# Ativar (Linux/Mac)
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
```

Edite `.env` com as credenciais do Firebird e SFTP.

## Execução

```bash
python -m server.app
```

Servidor inicia em `http://localhost:8580`.

Na primeira execução, uma API Key é gerada e salva em `data/.api_key`.

## Instalação Docker

```bash
# 1. Construir e iniciar
docker-compose up -d

# 2. Verificar logs
docker-compose logs -f

# 3. Parar
docker-compose down
```

## Agendamento Windows

Para ambientes Windows sem Docker, use o Agendador de Tarefas:

```bash
# Exportar schedule como tarefa agendada
curl -X POST http://localhost:8580/api/scheduler/1/export-windows \
  -H "Authorization: Bearer <api_key>"
```

## Backups

O sistema realiza backup automático do banco SQLite (`data/server.db`) na pasta `backups/`. Retenção configurável via `AppConfig` (`backup_retention_days`).

## Notificações

Configure SMTP ou Webhook para receber notificações de execução:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu@email.com
SMTP_PASSWORD=sua-senha
SMTP_FROM=seu@email.com
SMTP_TO=destino@email.com
```

Ou via webhook:

```env
WEBHOOK_URL=https://hooks.example.com/ecodata
```
