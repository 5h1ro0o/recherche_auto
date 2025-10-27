#!/usr/bin/env python3
# backend/start_services.py - Script de démarrage orchestré
"""
Script de démarrage pour tous les services de l'application

Usage:
    python start_services.py --all                    # Tout démarrer
    python start_services.py --api                    # API FastAPI uniquement
    python start_services.py --worker                 # Worker scraping uniquement
    python start_services.py --celery                 # Celery worker + beat
    python start_services.py --check                  # Vérifier dépendances
"""

import os
import sys
import subprocess
import time
import signal
import argparse
from typing import List, Dict
import psutil

# Couleurs pour output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


class ServiceManager:
    """Gestionnaire de services"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Configure les handlers pour arrêt propre"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Arrêt propre de tous les services"""
        print_warning("\n🛑 Signal d'arrêt reçu, fermeture des services...")
        self.stop_all()
        sys.exit(0)
    
    def check_dependencies(self) -> bool:
        """Vérifie que toutes les dépendances sont installées"""
        print_header("VÉRIFICATION DES DÉPENDANCES")
        
        all_ok = True
        
        # Python packages
        packages = [
            ('fastapi', 'FastAPI'),
            ('uvicorn', 'Uvicorn'),
            ('sqlalchemy', 'SQLAlchemy'),
            ('psycopg2', 'psycopg2'),
            ('elasticsearch', 'Elasticsearch'),
            ('redis', 'Redis'),
            ('celery', 'Celery'),
            ('playwright', 'Playwright'),
        ]
        
        for module, name in packages:
            try:
                __import__(module)
                print_success(f"{name} installé")
            except ImportError:
                print_error(f"{name} manquant - pip install {module}")
                all_ok = False
        
        # Services externes
        print("\n📦 Vérification des services externes:")
        
        # PostgreSQL
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', '127.0.0.1'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'vehicles'),
                user=os.getenv('DB_USER', 'app'),
                password=os.getenv('DB_PASSWORD', 'changeme')
            )
            conn.close()
            print_success("PostgreSQL accessible")
        except Exception as e:
            print_error(f"PostgreSQL non accessible: {e}")
            all_ok = False
        
        # Redis
        try:
            import redis
            r = redis.from_url(os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'))
            r.ping()
            print_success("Redis accessible")
        except Exception as e:
            print_error(f"Redis non accessible: {e}")
            all_ok = False
        
        # Elasticsearch
        try:
            from elasticsearch import Elasticsearch
            es = Elasticsearch([os.getenv('ELASTIC_HOST', 'http://127.0.0.1:9200')])
            es.ping()
            print_success("Elasticsearch accessible")
        except Exception as e:
            print_error(f"Elasticsearch non accessible: {e}")
            all_ok = False
        
        if all_ok:
            print_success("\n✅ Toutes les dépendances sont OK!")
        else:
            print_error("\n❌ Certaines dépendances manquent")
        
        return all_ok
    
    def start_api(self):
        """Démarre l'API FastAPI"""
        print_header("DÉMARRAGE API FASTAPI")
        
        cmd = [
            "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ]
        
        print_info(f"Commande: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, cwd="backend")
        self.processes['api'] = process
        
        time.sleep(2)
        
        if process.poll() is None:
            print_success("API démarrée sur http://localhost:8000")
            print_info("Documentation: http://localhost:8000/docs")
        else:
            print_error("Échec démarrage API")
    
    def start_worker(self):
        """Démarre le worker de scraping"""
        print_header("DÉMARRAGE WORKER SCRAPING")
        
        cmd = [
            sys.executable,
            "app/worker.py",
            "--run-worker"
        ]
        
        print_info(f"Commande: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, cwd="backend")
        self.processes['worker'] = process
        
        time.sleep(1)
        
        if process.poll() is None:
            print_success("Worker démarré")
        else:
            print_error("Échec démarrage worker")
    
    def start_celery_worker(self):
        """Démarre Celery worker"""
        print_header("DÉMARRAGE CELERY WORKER")
        
        cmd = [
            "celery",
            "-A", "app.celery_app",
            "worker",
            "--loglevel=info",
            "--concurrency=4",
            "--pool=prefork"
        ]
        
        print_info(f"Commande: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, cwd="backend")
        self.processes['celery_worker'] = process
        
        time.sleep(2)
        
        if process.poll() is None:
            print_success("Celery worker démarré")
        else:
            print_error("Échec démarrage Celery worker")
    
    def start_celery_beat(self):
        """Démarre Celery beat (scheduler)"""
        print_header("DÉMARRAGE CELERY BEAT")
        
        cmd = [
            "celery",
            "-A", "app.celery_app",
            "beat",
            "--loglevel=info"
        ]
        
        print_info(f"Commande: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, cwd="backend")
        self.processes['celery_beat'] = process
        
        time.sleep(1)
        
        if process.poll() is None:
            print_success("Celery beat démarré")
        else:
            print_error("Échec démarrage Celery beat")
    
    def start_flower(self):
        """Démarre Flower (monitoring Celery)"""
        print_header("DÉMARRAGE FLOWER")
        
        cmd = [
            "celery",
            "-A", "app.celery_app",
            "flower",
            "--port=5555",
            "--loglevel=info"
        ]
        
        print_info(f"Commande: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, cwd="backend")
        self.processes['flower'] = process
        
        time.sleep(2)
        
        if process.poll() is None:
            print_success("Flower démarré sur http://localhost:5555")
        else:
            print_error("Échec démarrage Flower")
    
    def stop_all(self):
        """Arrête tous les services"""
        print_header("ARRÊT DES SERVICES")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print_info(f"Arrêt de {name}...")
                
                try:
                    # Tenter arrêt gracieux
                    process.terminate()
                    process.wait(timeout=10)
                    print_success(f"{name} arrêté")
                except subprocess.TimeoutExpired:
                    # Force kill si timeout
                    print_warning(f"Force kill de {name}")
                    process.kill()
                    process.wait()
        
        self.processes.clear()
        print_success("Tous les services sont arrêtés")
    
    def status(self):
        """Affiche le statut des services"""
        print_header("STATUT DES SERVICES")
        
        if not self.processes:
            print_warning("Aucun service n'est démarré")
            return
        
        for name, process in self.processes.items():
            if process.poll() is None:
                # Process actif
                try:
                    p = psutil.Process(process.pid)
                    cpu = p.cpu_percent(interval=0.1)
                    mem = p.memory_info().rss / 1024 / 1024  # MB
                    
                    print_success(f"{name} (PID: {process.pid}) - CPU: {cpu:.1f}% - RAM: {mem:.1f}MB")
                except:
                    print_success(f"{name} (PID: {process.pid}) - Actif")
            else:
                print_error(f"{name} - Arrêté (code: {process.returncode})")
    
    def logs(self, service: str = None):
        """Affiche les logs d'un service"""
        if service and service in self.processes:
            process = self.processes[service]
            if process.poll() is None:
                print_info(f"Logs de {service} (CTRL+C pour quitter):")
                try:
                    process.wait()
                except KeyboardInterrupt:
                    pass
        else:
            print_warning("Service non trouvé ou non démarré")


def main():
    parser = argparse.ArgumentParser(
        description="Gestionnaire de services Voiture Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python start_services.py --all                # Tout démarrer
  python start_services.py --api --worker       # API + Worker uniquement
  python start_services.py --celery --flower    # Celery + Monitoring
  python start_services.py --check              # Vérifier environnement
        """
    )
    
    parser.add_argument('--all', action='store_true', 
                       help='Démarrer tous les services')
    parser.add_argument('--api', action='store_true', 
                       help='Démarrer API FastAPI')
    parser.add_argument('--worker', action='store_true', 
                       help='Démarrer worker scraping')
    parser.add_argument('--celery', action='store_true', 
                       help='Démarrer Celery worker + beat')
    parser.add_argument('--flower', action='store_true', 
                       help='Démarrer Flower (monitoring Celery)')
    parser.add_argument('--check', action='store_true', 
                       help='Vérifier dépendances uniquement')
    parser.add_argument('--status', action='store_true', 
                       help='Afficher statut des services')
    
    args = parser.parse_args()
    
    # Si aucun argument, afficher aide
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    manager = ServiceManager()
    
    # Vérification dépendances
    if args.check:
        success = manager.check_dependencies()
        sys.exit(0 if success else 1)
    
    # Statut
    if args.status:
        manager.status()
        return
    
    # Vérifier avant de démarrer
    print_info("Vérification des dépendances...")
    if not manager.check_dependencies():
        print_error("Certaines dépendances manquent. Installez-les avant de continuer.")
        sys.exit(1)
    
    # Démarrage des services
    try:
        if args.all:
            manager.start_api()
            time.sleep(2)
            manager.start_worker()
            time.sleep(2)
            manager.start_celery_worker()
            time.sleep(2)
            manager.start_celery_beat()
            time.sleep(2)
            manager.start_flower()
        else:
            if args.api:
                manager.start_api()
                time.sleep(2)
            
            if args.worker:
                manager.start_worker()
                time.sleep(2)
            
            if args.celery:
                manager.start_celery_worker()
                time.sleep(2)
                manager.start_celery_beat()
                time.sleep(2)
            
            if args.flower:
                manager.start_flower()
                time.sleep(2)
        
        # Afficher statut
        time.sleep(2)
        manager.status()
        
        # Afficher URLs importantes
        print_header("URLS IMPORTANTES")
        print_info("API Documentation: http://localhost:8000/docs")
        print_info("API Health: http://localhost:8000/")
        if args.flower or args.all:
            print_info("Flower (Celery): http://localhost:5555")
        
        # Garder le script actif
        print_header("SERVICES ACTIFS")
        print_info("Appuyez sur CTRL+C pour arrêter tous les services")
        
        while True:
            time.sleep(10)
            
            # Vérifier que les services sont toujours actifs
            for name, process in list(manager.processes.items()):
                if process.poll() is not None:
                    print_error(f"{name} s'est arrêté (code: {process.returncode})")
                    del manager.processes[name]
            
            if not manager.processes:
                print_error("Tous les services se sont arrêtés")
                break
    
    except KeyboardInterrupt:
        print_warning("\n🛑 Arrêt demandé par l'utilisateur")
        manager.stop_all()
    except Exception as e:
        print_error(f"Erreur: {e}")
        manager.stop_all()
        sys.exit(1)


if __name__ == "__main__":
    main()