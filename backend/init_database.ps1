# Script d'initialisation de la base de données PostgreSQL
# Pour PostgreSQL 17

Write-Host "🚀 Initialisation de la base de données PostgreSQL 17..." -ForegroundColor Cyan
Write-Host ""

# Paramètres
$DB_NAME = "recherche_auto"
$DB_USER = "app"
$DB_PASSWORD = "changeme"
$POSTGRES_USER = "postgres"

# Demander le mot de passe postgres
Write-Host "📝 Veuillez entrer le mot de passe de l'utilisateur 'postgres':" -ForegroundColor Yellow
$POSTGRES_PASSWORD = Read-Host -AsSecureString
$POSTGRES_PASSWORD_TEXT = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($POSTGRES_PASSWORD))

Write-Host ""
Write-Host "🔧 Création de la base de données et de l'utilisateur..." -ForegroundColor Green

# Créer un fichier SQL temporaire
$SQL_COMMANDS = @"
-- Vérifier si la base existe déjà
SELECT 'CREATE DATABASE $DB_NAME'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Se connecter à la nouvelle base (vous devrez le faire manuellement après)
\c $DB_NAME

-- Créer l'utilisateur s'il n'existe pas
DO
`$`$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$DB_USER') THEN
      CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
   END IF;
END
`$`$;

-- Donner tous les privilèges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;

-- Afficher un message de succès
SELECT '✅ Base de données créée avec succès!' as message;
"@

$SQL_FILE = "init_db_temp.sql"
$SQL_COMMANDS | Out-File -FilePath $SQL_FILE -Encoding UTF8

try {
    # Exécuter les commandes SQL
    $env:PGPASSWORD = $POSTGRES_PASSWORD_TEXT

    Write-Host "📊 Création de la base de données..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -c "CREATE DATABASE $DB_NAME;" 2>$null

    Write-Host "👤 Création de l'utilisateur..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>$null

    Write-Host "🔐 Attribution des privilèges..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    & psql -U $POSTGRES_USER -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
    & psql -U $POSTGRES_USER -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
    & psql -U $POSTGRES_USER -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;"

    Remove-Item $env:PGPASSWORD

    Write-Host ""
    Write-Host "✅ Base de données initialisée avec succès!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Informations de connexion:" -ForegroundColor Cyan
    Write-Host "  - Base de données: $DB_NAME" -ForegroundColor White
    Write-Host "  - Utilisateur: $DB_USER" -ForegroundColor White
    Write-Host "  - Mot de passe: $DB_PASSWORD" -ForegroundColor White
    Write-Host ""
    Write-Host "🔗 URL de connexion:" -ForegroundColor Cyan
    Write-Host "  postgresql+psycopg2://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME" -ForegroundColor White
    Write-Host ""

    # Créer le fichier .env
    Write-Host "📝 Création du fichier .env..." -ForegroundColor Cyan
    $ENV_CONTENT = @"
# Configuration pour PostgreSQL 17 en local
DATABASE_URL=postgresql+psycopg2://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Elasticsearch (optionnel)
ELASTIC_HOST=http://localhost:9200

# Redis (optionnel)
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=dev-secret-key-$(Get-Random)-change-in-production
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

    $ENV_CONTENT | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Fichier .env créé!" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host "❌ Erreur lors de l'initialisation:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Vérifiez que:" -ForegroundColor Yellow
    Write-Host "  1. PostgreSQL 17 est bien démarré (services.msc)" -ForegroundColor White
    Write-Host "  2. Le mot de passe postgres est correct" -ForegroundColor White
    Write-Host "  3. psql est dans votre PATH" -ForegroundColor White
    exit 1
} finally {
    # Nettoyer le fichier temporaire
    if (Test-Path $SQL_FILE) {
        Remove-Item $SQL_FILE
    }
}

Write-Host "🎯 Prochaine étape: Lancer le script setup.ps1 pour tout configurer!" -ForegroundColor Cyan
