# Script de démarrage pour l'application Recherche Auto
# Usage: .\start.ps1

Write-Host "🚀 Démarrage de l'application Recherche Auto..." -ForegroundColor Cyan
Write-Host ""

# Vérifier que Docker Desktop est lancé
Write-Host "🐳 Vérification de Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Desktop n'est pas lancé!" -ForegroundColor Red
    Write-Host "💡 Lancez Docker Desktop et réessayez." -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Docker est lancé" -ForegroundColor Green

# Démarrer les services Docker
Write-Host ""
Write-Host "📦 Démarrage des services (PostgreSQL, Elasticsearch, Redis)..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\infra"
docker-compose up -d

# Attendre que les services soient prêts
Write-Host ""
Write-Host "⏳ Attente du démarrage des services (30 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Vérifier l'état des services
Write-Host ""
Write-Host "🔍 Vérification de l'état des services..." -ForegroundColor Yellow
docker-compose ps

# Vérifier Elasticsearch
Write-Host ""
Write-Host "🔍 Test de connexion à Elasticsearch..." -ForegroundColor Yellow
try {
    $esResponse = Invoke-WebRequest -Uri "http://localhost:9200" -UseBasicParsing -TimeoutSec 5
    if ($esResponse.StatusCode -eq 200) {
        Write-Host "✅ Elasticsearch est accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Elasticsearch n'est pas encore prêt" -ForegroundColor Yellow
}

# Vérifier PostgreSQL
Write-Host ""
Write-Host "🐘 Test de connexion à PostgreSQL..." -ForegroundColor Yellow
$pgTest = docker exec recherche_auto-postgres-1 psql -U app -d vehicles -c "SELECT 1" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL est accessible" -ForegroundColor Green
} else {
    Write-Host "⚠️  PostgreSQL n'est pas encore prêt (c'est normal au premier lancement)" -ForegroundColor Yellow
}

# Créer les tables si nécessaire
Write-Host ""
Write-Host "📊 Création des tables de la base de données..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\backend"

# Vérifier que l'environnement virtuel existe
if (-Not (Test-Path ".venv")) {
    Write-Host "⚠️  Environnement virtuel Python non trouvé" -ForegroundColor Yellow
    Write-Host "💡 Créez-le avec: python -m venv .venv" -ForegroundColor Yellow
} else {
    # Activer l'environnement virtuel et créer les tables
    & ".venv\Scripts\Activate.ps1"

    Write-Host "🔧 Création des tables..." -ForegroundColor Yellow
    python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine); print('✅ Tables créées ou déjà existantes!')"

    # Vérifier si l'index Elasticsearch existe
    Write-Host ""
    Write-Host "🔍 Vérification de l'index Elasticsearch..." -ForegroundColor Yellow
    try {
        $indexCheck = Invoke-WebRequest -Uri "http://localhost:9200/vehicles/_count" -UseBasicParsing -TimeoutSec 5
        $countData = $indexCheck.Content | ConvertFrom-Json
        if ($countData.count -eq 0) {
            Write-Host "⚠️  L'index Elasticsearch est vide" -ForegroundColor Yellow
            Write-Host "💡 Initialisez-le avec: python init_db.py" -ForegroundColor Yellow
        } else {
            Write-Host "✅ Index Elasticsearch contient $($countData.count) véhicules" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  L'index Elasticsearch n'existe pas encore" -ForegroundColor Yellow
        Write-Host "💡 Créez-le avec: python init_db.py" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=" -repeat 60 -ForegroundColor Cyan
Write-Host "✅ Services démarrés avec succès!" -ForegroundColor Green
Write-Host "=" -repeat 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Prochaines étapes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Initialiser la base de données (si pas déjà fait):" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python init_db.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Démarrer le backend:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Démarrer le frontend (nouveau terminal):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Accéder à l'application:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛑 Pour arrêter les services:" -ForegroundColor Yellow
Write-Host "   cd infra && docker-compose down" -ForegroundColor Gray
Write-Host ""
