# Script d'initialisation de la base de donnees PostgreSQL
# Pour PostgreSQL 17

Write-Host "Initialisation de la base de donnees PostgreSQL 17..." -ForegroundColor Cyan
Write-Host ""

# Parametres
$DB_NAME = "recherche_auto"
$DB_USER = "app"
$DB_PASSWORD = "changeme"
$POSTGRES_USER = "postgres"

# Demander le mot de passe postgres
Write-Host "Veuillez entrer le mot de passe de l'utilisateur 'postgres':" -ForegroundColor Yellow
$POSTGRES_PASSWORD = Read-Host -AsSecureString
$POSTGRES_PASSWORD_TEXT = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($POSTGRES_PASSWORD))

Write-Host ""
Write-Host "Creation de la base de donnees et de l'utilisateur..." -ForegroundColor Green

try {
    # Executer les commandes SQL
    $env:PGPASSWORD = $POSTGRES_PASSWORD_TEXT

    Write-Host "Creation de la base de donnees..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -c "CREATE DATABASE $DB_NAME;" 2>$null

    Write-Host "Creation de l'utilisateur..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>$null

    Write-Host "Attribution des privileges..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    & psql -U $POSTGRES_USER -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
    & psql -U $POSTGRES_USER -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
    & psql -U $POSTGRES_USER -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;"

    Remove-Item env:PGPASSWORD

    Write-Host ""
    Write-Host "Base de donnees initialisee avec succes!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Informations de connexion:" -ForegroundColor Cyan
    Write-Host "  - Base de donnees: $DB_NAME" -ForegroundColor White
    Write-Host "  - Utilisateur: $DB_USER" -ForegroundColor White
    Write-Host "  - Mot de passe: $DB_PASSWORD" -ForegroundColor White
    Write-Host ""
    Write-Host "URL de connexion:" -ForegroundColor Cyan
    Write-Host "  postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@localhost:5432/$DB_NAME" -ForegroundColor White
    Write-Host ""

    # Creer le fichier .env
    Write-Host "Creation du fichier .env..." -ForegroundColor Cyan

    # Utiliser une here-string avec des guillemets simples pour eviter l'interpolation
    $ENV_CONTENT = @'
# Configuration pour PostgreSQL 17 en local
DATABASE_URL=postgresql+psycopg2://app:changeme@localhost:5432/recherche_auto

# Elasticsearch (optionnel)
ELASTIC_HOST=http://localhost:9200

# Redis (optionnel)
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=dev-secret-key-CHANGE-THIS-IN-PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30

# OpenAI (optionnel)
OPENAI_API_KEY=

# Logging
LOG_LEVEL=INFO

# Application
APP_NAME=Voiture Search
'@

    $ENV_CONTENT | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "Fichier .env cree!" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host "Erreur lors de l'initialisation:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifiez que:" -ForegroundColor Yellow
    Write-Host "  1. PostgreSQL 17 est bien demarre (services.msc)" -ForegroundColor White
    Write-Host "  2. Le mot de passe postgres est correct" -ForegroundColor White
    Write-Host "  3. psql est dans votre PATH" -ForegroundColor White
    exit 1
}

Write-Host "Prochaine etape: Lancer le script setup.ps1 pour tout configurer!" -ForegroundColor Cyan
