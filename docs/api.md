# Documentação da API

Todas as rotas (exceto `/api/health`) exigem autenticação via `Authorization: Bearer <api_key>`.

## Health

```http
GET /api/health
```
Resposta: `{"status": "ok", "app": "ECOdata", "version": "1.0.0", "scheduler": {...}}`

## Autenticação

```http
POST /api/auth/verify
```
Resposta: `{"authenticated": true, "username": "admin", "role": "admin"}`

```http
POST /api/auth/change-key
```
Gera nova API Key (invalida a anterior).

## Dashboard

```http
GET /api/dashboard/kpis
```
KPIs: total_execucoes, sucesso, falha, em_andamento, total_arquivos, uptime.

```http
GET /api/dashboard/status-grafico
```
Dados para gráfico de pizza (sucesso/falha).

```http
GET /api/dashboard/export-csv
```
Exporta histórico de execuções como CSV.

## Scheduler

```http
GET /api/scheduler?search=&tipo=&enabled=true
```
Lista agendamentos com filtros.

```http
POST /api/scheduler
```
Cria agendamento. Body: `{"name", "tipo", "cron_expression", "enabled", "send_sftp"}`

```http
PUT /api/scheduler/{id}
```
Atualiza agendamento.

```http
DELETE /api/scheduler/{id}
```
Exclui agendamento.

```http
POST /api/scheduler/{id}/toggle
```
Ativa/desativa agendamento.

```http
POST /api/scheduler/{id}/run
```
Executa agendamento imediatamente.

## Arquivos

```http
GET /api/files?tipo=&page=1&per_page=50&sort_by=modified&sort_order=desc
```
Lista arquivos gerados com paginação.

```http
GET /api/files/preview?filename=
```
Preview das primeiras 500 linhas.

```http
GET /api/files/download?filename=
```
Download do arquivo.

```http
DELETE /api/files?filename=
```
Exclui arquivo.

```http
POST /api/files/resend?filename=
```
Reenvia arquivo via SFTP.

## Logs

```http
GET /api/logs?level=INFO&page=1&per_page=50
```
Logs do sistema com filtro por nível.

## Configurações

```http
GET /api/config
```
Retorna configurações atuais (DB + AppConfig).

```http
PUT /api/config
```
Atualiza configuração. Body: `{"key": "log_retention_days", "value": "90"}`

## Backup

```http
GET /api/backup
```
Lista backups.

```http
POST /api/backup?tipo=
```
Cria backup.

```http
GET /api/backup/{id}/download
```
Download do backup.

## Auditoria

```http
GET /api/auditoria?page=1&per_page=50
```
Histórico de alterações.

## Execução

```http
POST /api/executar/{tipo}
```
Executa gerador (ESTOQUE, SELLOUT, PAINEL).

```http
POST /api/executar/{execution_id}/cancelar
```
Cancela execução em andamento.
