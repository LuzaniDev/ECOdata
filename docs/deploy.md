# Guia de Deploy

## Docker (Recomendado)

```bash
# Build
docker build -t ecodata:latest .

# Executar com .env
docker run -d --name ecodata \
  --env-file .env \
  -p 8580:8580 \
  -v ecodata_data:/app/data \
  -v ecodata_output:/app/output \
  ecodata:latest
```

Ou com docker-compose:

```bash
docker-compose up -d
```

## Produção (Servidor Windows)

```bash
# Instalar como serviço Windows (usando nssm)
nssm install ECOdata "C:\caminho\para\.venv\Scripts\python.exe" "-m server.app"
nssm set ECOdata AppDirectory "C:\caminho\para\ECOdata"
nssm start ECOdata
```

## Proxy Reverso (Nginx)

```nginx
server {
    listen 80;
    server_name ecodata.exemplo.com;

    location / {
        proxy_pass http://127.0.0.1:8580;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## CI/CD

O projeto inclui GitHub Actions para:

- **CI:** Testes automatizados (ruff + mypy + pytest) em push/PR para `main`
- **CD:** Build de imagem Docker em push de tag `v*`

Para configurar CI/CD:

1. Faça push do repositório para o GitHub
2. As actions serão executadas automaticamente
3. Para release: `git tag v1.0.0 && git push origin v1.0.0`

## Monitoramento

Health check disponível em `/api/health` (sem autenticação).

Para Prometheus, configure coleta da métrica de health.
