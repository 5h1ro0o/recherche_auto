# Script pour recreer la base de donnees avec encodage UTF-8
# Ce script supprime et recree la base recherche_auto avec UTF-8

Write-Host "Recreation de la base de donnees avec encodage UTF-8..." -ForegroundColor Cyan
Write-Host ""

$DB_NAME = "recherche_auto"
$DB_USER = "app"
$DB_PASSWORD = "changeme"
$POSTGRES_USER = "postgres"

# Demander le mot de passe postgres
Write-Host "Veuillez entrer le mot de passe de l'utilisateur 'postgres':" -ForegroundColor Yellow
$POSTGRES_PASSWORD = Read-Host -AsSecureString
$POSTGRES_PASSWORD_TEXT = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($POSTGRES_PASSWORD))

Write-Host ""

try {
    $env:PGPASSWORD = $POSTGRES_PASSWORD_TEXT

    # Terminer toutes les connexions actives
    Write-Host "Fermeture des connexions actives..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" 2>$null

    # Supprimer la base si elle existe
    Write-Host "Suppression de l'ancienne base de donnees..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>$null

    # Supprimer l'utilisateur si il existe
    Write-Host "Suppression de l'ancien utilisateur..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d postgres -c "DROP USER IF EXISTS $DB_USER;" 2>$null

    # Creer la base avec UTF-8 explicite
    Write-Host "Creation de la nouvelle base avec UTF-8..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d postgres -c "CREATE DATABASE $DB_NAME WITH ENCODING 'UTF8' LC_COLLATE='C' LC_CTYPE='C' TEMPLATE=template0;"

    if ($LASTEXITCODE -ne 0) {
        throw "Echec de la creation de la base de donnees"
    }

    # Creer l'utilisateur
    Write-Host "Creation de l'utilisateur..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

    # Attribuer les privileges
    Write-Host "Attribution des privileges..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    & psql -U $POSTGRES_USER -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
    & psql -U $POSTGRES_USER -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
    & psql -U $POSTGRES_USER -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;"
    & psql -U $POSTGRES_USER -d $DB_NAME -c "ALTER DATABASE $DB_NAME SET client_encoding TO 'UTF8';"

    Remove-Item env:PGPASSWORD

    Write-Host ""
    Write-Host "Base de donnees recreee avec succes en UTF-8!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Prochaines etapes:" -ForegroundColor Cyan
    Write-Host "  1. Executer les migrations: alembic upgrade head" -ForegroundColor White
    Write-Host "  2. Relancer le serveur backend" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host "Erreur lors de la recreation:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Remove-Item env:PGPASSWORD -ErrorAction SilentlyContinue
    exit 1
}
