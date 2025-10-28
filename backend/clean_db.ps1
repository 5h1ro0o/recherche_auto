# Script pour nettoyer la base de donnees en cas de migration echouee

Write-Host "Nettoyage de la base de donnees PostgreSQL..." -ForegroundColor Cyan
Write-Host ""

$DB_NAME = "recherche_auto"
$POSTGRES_USER = "postgres"

# Demander le mot de passe postgres
Write-Host "Veuillez entrer le mot de passe de l'utilisateur 'postgres':" -ForegroundColor Yellow
$POSTGRES_PASSWORD = Read-Host -AsSecureString
$POSTGRES_PASSWORD_TEXT = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($POSTGRES_PASSWORD))

Write-Host ""
Write-Host "Nettoyage complet de la base de donnees..." -ForegroundColor Green

try {
    $env:PGPASSWORD = $POSTGRES_PASSWORD_TEXT

    # Supprimer toutes les tables en cascade
    Write-Host "Suppression de toutes les tables..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS proposed_vehicles CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS assisted_requests CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS scraper_logs CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS messages CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS conversations CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS favorites CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS alerts CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS search_history CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS vehicles CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS users CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TABLE IF EXISTS alembic_version CASCADE;" 2>$null

    # Supprimer tous les types ENUM
    Write-Host "Suppression des types ENUM..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TYPE IF EXISTS proposalstatus CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TYPE IF EXISTS requeststatus CASCADE;" 2>$null
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TYPE IF EXISTS userrole CASCADE;" 2>$null

    Remove-Item env:PGPASSWORD

    Write-Host ""
    Write-Host "Base de donnees nettoyee avec succes!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Vous pouvez maintenant relancer:" -ForegroundColor Cyan
    Write-Host "  .\setup.ps1" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host "Erreur lors du nettoyage:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
