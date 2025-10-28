# Script de configuration complète du backend
# Configure tout automatiquement pour PostgreSQL 17

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🚀 Configuration automatique du backend               ║" -ForegroundColor Cyan
Write-Host "║        PostgreSQL 17 + Alembic + Uvicorn                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Vérifier qu'on est dans le bon dossier
if (-not (Test-Path "app")) {
    Write-Host "❌ Erreur: Vous devez être dans le dossier 'backend'" -ForegroundColor Red
    Write-Host "💡 Exécutez: cd C:\Users\matte\Desktop\recherche_auto\backend" -ForegroundColor Yellow
    exit 1
}

# Étape 1: Vérifier l'environnement virtuel
Write-Host "📦 Étape 1/6: Vérification de l'environnement virtuel..." -ForegroundColor Green
if (-not (Test-Path ".venv")) {
    Write-Host "⚠️  Environnement virtuel non trouvé. Création..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✅ Environnement virtuel créé!" -ForegroundColor Green
} else {
    Write-Host "✅ Environnement virtuel trouvé!" -ForegroundColor Green
}

# Activer l'environnement virtuel
Write-Host "🔄 Activation de l'environnement virtuel..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Étape 2: Installer les dépendances
Write-Host ""
Write-Host "📦 Étape 2/6: Installation des dépendances..." -ForegroundColor Green
pip install -q --upgrade pip
pip install -q -r requirements.txt
Write-Host "✅ Dépendances installées!" -ForegroundColor Green

# Étape 3: Vérifier si .env existe
Write-Host ""
Write-Host "📝 Étape 3/6: Vérification du fichier .env..." -ForegroundColor Green
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Fichier .env non trouvé." -ForegroundColor Yellow
    Write-Host "🔧 Lancement de l'initialisation de la base de données..." -ForegroundColor Cyan
    Write-Host ""
    & .\init_database.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Échec de l'initialisation de la base de données" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Fichier .env trouvé!" -ForegroundColor Green
}

# Étape 4: Tester la connexion à la base de données
Write-Host ""
Write-Host "🔍 Étape 4/6: Test de connexion à PostgreSQL..." -ForegroundColor Green
python test_db_connection.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Impossible de se connecter à PostgreSQL" -ForegroundColor Red
    Write-Host "💡 Vérifiez votre fichier .env et que PostgreSQL est démarré" -ForegroundColor Yellow
    exit 1
}

# Étape 5: Exécuter les migrations Alembic
Write-Host ""
Write-Host "🗄️  Étape 5/6: Exécution des migrations Alembic..." -ForegroundColor Green
alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Échec des migrations" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Migrations appliquées avec succès!" -ForegroundColor Green

# Étape 6: Résumé
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║            ✅ Configuration terminée avec succès!          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Pour démarrer le backend:" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Le backend sera accessible sur:" -ForegroundColor Cyan
Write-Host "   http://localhost:8000" -ForegroundColor White
Write-Host "   http://localhost:8000/docs (Documentation API)" -ForegroundColor White
Write-Host ""
Write-Host "💡 Conseil: Gardez ce terminal ouvert et ouvrez un nouveau" -ForegroundColor Yellow
Write-Host "   terminal pour lancer le frontend (cd ../frontend && npm run dev)" -ForegroundColor Yellow
Write-Host ""

# Demander si on doit lancer le serveur
$response = Read-Host "Voulez-vous démarrer le backend maintenant? (O/n)"
if ($response -eq "" -or $response -eq "O" -or $response -eq "o") {
    Write-Host ""
    Write-Host "🚀 Démarrage du serveur backend..." -ForegroundColor Green
    Write-Host ""
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}
