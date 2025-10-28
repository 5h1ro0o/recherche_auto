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
Write-Host "Nettoyage des types ENUM orphelins..." -ForegroundColor Green

try {
    $env:PGPASSWORD = $POSTGRES_PASSWORD_TEXT

    # Supprimer le type userrole s'il existe
    Write-Host "Suppression du type userrole..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TYPE IF EXISTS userrole CASCADE;" 2>$null

    # Supprimer le type requeststatus s'il existe
    Write-Host "Suppression du type requeststatus..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TYPE IF EXISTS requeststatus CASCADE;" 2>$null

    # Supprimer le type proposalstatus s'il existe
    Write-Host "Suppression du type proposalstatus..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DROP TYPE IF EXISTS proposalstatus CASCADE;" 2>$null

    # Remettre la table alembic_version a zero
    Write-Host "Reinitialisation d'Alembic..." -ForegroundColor Cyan
    & psql -U $POSTGRES_USER -d $DB_NAME -c "DELETE FROM alembic_version;" 2>$null

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
