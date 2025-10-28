# Script de configuration complete du backend
# Configure tout automatiquement pour PostgreSQL 17

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     Configuration automatique du backend                  " -ForegroundColor Cyan
Write-Host "        PostgreSQL 17 + Alembic + Uvicorn                  " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verifier qu'on est dans le bon dossier
if (-not (Test-Path "app")) {
    Write-Host "Erreur: Vous devez etre dans le dossier 'backend'" -ForegroundColor Red
    Write-Host "Executez: cd C:\Users\matte\Desktop\recherche_auto\backend" -ForegroundColor Yellow
    exit 1
}

# Etape 1: Verifier l'environnement virtuel
Write-Host "Etape 1/6: Verification de l'environnement virtuel..." -ForegroundColor Green
if (-not (Test-Path ".venv")) {
    Write-Host "Environnement virtuel non trouve. Creation..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "Environnement virtuel cree!" -ForegroundColor Green
} else {
    Write-Host "Environnement virtuel trouve!" -ForegroundColor Green
}

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Etape 2: Installer les dependances
Write-Host ""
Write-Host "Etape 2/6: Installation des dependances..." -ForegroundColor Green
pip install -q --upgrade pip
pip install -q -r requirements.txt
Write-Host "Dependances installees!" -ForegroundColor Green

# Etape 3: Verifier si .env existe
Write-Host ""
Write-Host "Etape 3/6: Verification du fichier .env..." -ForegroundColor Green
if (-not (Test-Path ".env")) {
    Write-Host "Fichier .env non trouve." -ForegroundColor Yellow
    Write-Host "Lancement de l'initialisation de la base de donnees..." -ForegroundColor Cyan
    Write-Host ""
    & .\init_database.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Echec de l'initialisation de la base de donnees" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Fichier .env trouve!" -ForegroundColor Green
}

# Etape 4: Tester la connexion a la base de donnees
Write-Host ""
Write-Host "Etape 4/6: Test de connexion a PostgreSQL..." -ForegroundColor Green
python test_db_connection.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Impossible de se connecter a PostgreSQL" -ForegroundColor Red
    Write-Host "Verifiez votre fichier .env et que PostgreSQL est demarre" -ForegroundColor Yellow
    exit 1
}

# Etape 5: Executer les migrations Alembic
Write-Host ""
Write-Host "Etape 5/6: Execution des migrations Alembic..." -ForegroundColor Green
alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "Echec des migrations" -ForegroundColor Red
    exit 1
}
Write-Host "Migrations appliquees avec succes!" -ForegroundColor Green

# Etape 6: Resume
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "            Configuration terminee avec succes!            " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour demarrer le backend:" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "Le backend sera accessible sur:" -ForegroundColor Cyan
Write-Host "   http://localhost:8000" -ForegroundColor White
Write-Host "   http://localhost:8000/docs (Documentation API)" -ForegroundColor White
Write-Host ""
Write-Host "Conseil: Gardez ce terminal ouvert et ouvrez un nouveau" -ForegroundColor Yellow
Write-Host "   terminal pour lancer le frontend (cd ../frontend && npm run dev)" -ForegroundColor Yellow
Write-Host ""

# Demander si on doit lancer le serveur
$response = Read-Host "Voulez-vous demarrer le backend maintenant? (O/n)"
if ($response -eq "" -or $response -eq "O" -or $response -eq "o") {
    Write-Host ""
    Write-Host "Demarrage du serveur backend..." -ForegroundColor Green
    Write-Host ""
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}
