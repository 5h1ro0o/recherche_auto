# Script pour recreer le fichier .env avec les bonnes valeurs

Write-Host "Recreation du fichier .env..." -ForegroundColor Cyan

$ENV_CONTENT = @"
# Configuration pour PostgreSQL 17 en local
DATABASE_URL=postgresql+psycopg2://app:changeme@localhost:5432/recherche_auto

# Elasticsearch (optionnel)
ELASTIC_HOST=http://localhost:9200

# Redis (optionnel)
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30

# OpenAI (optionnel)
OPENAI_API_KEY=

# Logging
LOG_LEVEL=INFO

# Application
APP_NAME=Voiture Search
"@

$ENV_CONTENT | Out-File -FilePath ".env" -Encoding UTF8 -Force
Write-Host "Fichier .env recree avec succes!" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Base de donnees: recherche_auto" -ForegroundColor White
Write-Host "  Utilisateur: app" -ForegroundColor White
Write-Host "  Mot de passe: changeme" -ForegroundColor White
Write-Host ""
Write-Host "Si vous utilisez un mot de passe different pour PostgreSQL," -ForegroundColor Yellow
Write-Host "editez le fichier .env et modifiez la ligne DATABASE_URL" -ForegroundColor Yellow
