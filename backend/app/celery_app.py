# backend/app/celery_app.py - VERSION PRODUCTION AVEC MONITORING
import os
import logging

logger = logging.getLogger(__name__)

try:
    from celery import Celery, signals
    from celery.schedules import crontab
    from celery.utils.log import get_task_logger
    CELERY_AVAILABLE = True
except ImportError:
    print("⚠️ Celery n'est pas installé. Installer avec: pip install celery[redis]")
    CELERY_AVAILABLE = False
    Celery = None
    crontab = None

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

if CELERY_AVAILABLE:
    app = Celery(
        'voiture_search',
        broker=REDIS_URL,
        backend=REDIS_URL
    )

    app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Europe/Paris',
        enable_utc=True,
        
        # Configuration de performance
        worker_prefetch_multiplier=4,
        worker_max_tasks_per_child=1000,
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        
        # Retry configuration
        task_autoretry_for=(Exception,),
        task_retry_kwargs={'max_retries': 3},
        task_retry_backoff=True,
        task_retry_backoff_max=600,
        task_retry_jitter=True,
        
        # Timeouts
        task_soft_time_limit=3600,  # 1 heure
        task_time_limit=7200,       # 2 heures max
        
        # Monitoring
        task_send_sent_event=True,
        task_track_started=True,
        
        # Beat schedule - Scraping intelligent par plages horaires
        beat_schedule={
            # ============ LEBONCOIN - Fréquence adaptative ============
            'scrape-lbc-peak-hours': {
                'task': 'app.tasks.scrape_leboncoin',
                'schedule': crontab(minute='*/20', hour='8-20'),  # Toutes les 20min en journée
                'options': {
                    'expires': 1200,  # Expiration 20min
                    'priority': 9     # Haute priorité
                },
                'kwargs': {
                    'query': 'voiture',
                    'max_pages': 5,
                    'deep_scrape': False  # Rapide en peak
                }
            },
            'scrape-lbc-off-peak': {
                'task': 'app.tasks.scrape_leboncoin',
                'schedule': crontab(minute=0, hour='0-7,21-23'),  # Toutes les heures la nuit
                'options': {
                    'expires': 3600,
                    'priority': 5
                },
                'kwargs': {
                    'query': 'voiture',
                    'max_pages': 10,
                    'deep_scrape': True  # Scraping complet la nuit
                }
            },
            
            # ============ LACENTRALE - Moins fréquent (contenu plus stable) ============
            'scrape-lacentrale-morning': {
                'task': 'app.tasks.scrape_lacentrale',
                'schedule': crontab(minute=30, hour='6,9,12'),  # 3x par jour
                'options': {
                    'expires': 3600,
                    'priority': 7
                },
                'kwargs': {
                    'queries': ['volkswagen:golf', 'peugeot:208', 'renault:clio'],
                    'max_pages': 10
                }
            },
            'scrape-lacentrale-evening': {
                'task': 'app.tasks.scrape_lacentrale',
                'schedule': crontab(minute=0, hour='18'),  # Soir
                'options': {
                    'expires': 3600,
                    'priority': 6
                },
                'kwargs': {
                    'queries': ['bmw:serie-3', 'audi:a3', 'mercedes:classe-a'],
                    'max_pages': 8
                }
            },
            
            # ============ AUTOSCOUT24 - Scraping hebdomadaire (international) ============
            'scrape-autoscout-daily': {
                'task': 'app.tasks.scrape_autoscout',
                'schedule': crontab(minute=0, hour='3'),  # 3h du matin
                'options': {
                    'expires': 7200,
                    'priority': 4
                },
                'kwargs': {
                    'max_pages': 5
                }
            },
            
            # ============ MAINTENANCE & MONITORING ============
            'cleanup-old-listings': {
                'task': 'app.tasks.cleanup_old_listings',
                'schedule': crontab(minute=0, hour='2'),  # 2h du matin quotidien
                'options': {
                    'priority': 3
                }
            },
            'update-elasticsearch-index': {
                'task': 'app.tasks.update_elasticsearch_index',
                'schedule': crontab(minute='*/30'),  # Toutes les 30min
                'options': {
                    'priority': 6
                }
            },
            'send-alert-notifications': {
                'task': 'app.tasks.send_alert_notifications',
                'schedule': crontab(minute='*/15'),  # Toutes les 15min
                'options': {
                    'priority': 8
                }
            },
            'generate-stats-report': {
                'task': 'app.tasks.generate_stats_report',
                'schedule': crontab(minute=0, hour='8'),  # 8h du matin
                'options': {
                    'priority': 2
                }
            },
            
            # ============ HEALTH CHECKS ============
            'health-check-scrapers': {
                'task': 'app.tasks.health_check_scrapers',
                'schedule': crontab(minute='*/5'),  # Toutes les 5min
                'options': {
                    'priority': 10  # Priorité max
                }
            }
        }
    )
    
    # ============ SIGNAL HANDLERS POUR MONITORING ============
    
    @signals.task_prerun.connect
    def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
        """Avant l'exécution d'une tâche"""
        task_logger = get_task_logger(task.name)
        task_logger.info(f"🚀 DÉMARRAGE: {task.name} (ID: {task_id})")
    
    @signals.task_postrun.connect
    def task_postrun_handler(sender=None, task_id=None, task=None, state=None, **kwargs):
        """Après l'exécution d'une tâche"""
        task_logger = get_task_logger(task.name)
        task_logger.info(f"✅ TERMINÉ: {task.name} (ID: {task_id}, État: {state})")
    
    @signals.task_failure.connect
    def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
        """En cas d'échec d'une tâche"""
        task_logger = get_task_logger(sender.name)
        task_logger.error(f"❌ ÉCHEC: {sender.name} (ID: {task_id})")
        task_logger.error(f"   Erreur: {exception}")
        
        # TODO: Envoyer alerte (email, Slack, etc.)
        # send_failure_alert(sender.name, task_id, exception)
    
    @signals.task_retry.connect
    def task_retry_handler(sender=None, task_id=None, reason=None, **kwargs):
        """En cas de retry d'une tâche"""
        task_logger = get_task_logger(sender.name)
        task_logger.warning(f"🔄 RETRY: {sender.name} (ID: {task_id})")
        task_logger.warning(f"   Raison: {reason}")
    
    @signals.task_success.connect
    def task_success_handler(sender=None, result=None, **kwargs):
        """En cas de succès d'une tâche"""
        task_logger = get_task_logger(sender.name)
        task_logger.info(f"🎉 SUCCÈS: {sender.name}")
        
        # Log résultat si c'est un scraper
        if isinstance(result, dict) and 'count' in result:
            task_logger.info(f"   Résultat: {result['count']} annonces")
    
    # ============ MONITORING UTILITIES ============
    
    def get_task_stats():
        """Récupère les statistiques des tâches"""
        from celery.task.control import inspect
        
        i = inspect(app=app)
        
        stats = {
            'active': i.active(),
            'scheduled': i.scheduled(),
            'reserved': i.reserved(),
            'stats': i.stats()
        }
        
        return stats
    
    def get_queue_length():
        """Récupère la longueur de la queue Redis"""
        try:
            from redis import from_url
            redis_client = from_url(REDIS_URL, decode_responses=True)
            
            queue_lengths = {}
            for queue_name in ['celery', 'scraper_queue']:
                length = redis_client.llen(queue_name)
                queue_lengths[queue_name] = length
            
            return queue_lengths
        except Exception as e:
            logger.error(f"Erreur récupération longueur queue: {e}")
            return {}
    
    def purge_queue(queue_name: str = 'celery'):
        """Purge une queue (attention, action destructive)"""
        from celery.bin.celery import celery as celery_bin
        
        try:
            app.control.purge()
            logger.info(f"✅ Queue {queue_name} purgée")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur purge queue: {e}")
            return False
    
    # ============ HEALTH CHECK ============
    
    def check_celery_health():
        """Vérifie la santé du système Celery"""
        from celery.task.control import inspect
        
        health = {
            'broker_available': False,
            'workers_available': False,
            'beat_running': False,
            'queue_ok': False
        }
        
        try:
            # Test broker
            app.broker_connection().ensure_connection(max_retries=3)
            health['broker_available'] = True
            
            # Test workers
            i = inspect(app=app)
            active_workers = i.active()
            if active_workers:
                health['workers_available'] = True
            
            # Test queue
            queue_lengths = get_queue_length()
            if queue_lengths and all(length < 10000 for length in queue_lengths.values()):
                health['queue_ok'] = True
            
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
        
        return health

else:
    app = None
    print("❌ Celery non disponible")


# ============ CLI UTILITAIRES ============

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Celery Management CLI")
    parser.add_argument('command', choices=['stats', 'health', 'queue-length', 'purge'], 
                       help='Commande à exécuter')
    parser.add_argument('--queue', default='celery', help='Nom de la queue (pour purge)')
    
    args = parser.parse_args()
    
    if not CELERY_AVAILABLE:
        print("❌ Celery n'est pas disponible")
        exit(1)
    
    print("="*70)
    print(f"🔧 CELERY MANAGEMENT - {args.command.upper()}")
    print("="*70)
    print()
    
    if args.command == 'stats':
        print("📊 Statistiques des tâches:")
        stats = get_task_stats()
        
        import json
        print(json.dumps(stats, indent=2, default=str))
    
    elif args.command == 'health':
        print("🏥 Health Check:")
        health = check_celery_health()
        
        for key, status in health.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {key}: {status}")
    
    elif args.command == 'queue-length':
        print("📦 Longueur des queues:")
        lengths = get_queue_length()
        
        for queue, length in lengths.items():
            print(f"  • {queue}: {length} items")
    
    elif args.command == 'purge':
        confirm = input(f"⚠️  Voulez-vous vraiment purger la queue '{args.queue}'? (yes/no): ")
        
        if confirm.lower() == 'yes':
            result = purge_queue(args.queue)
            if result:
                print(f"✅ Queue '{args.queue}' purgée")
            else:
                print(f"❌ Erreur lors de la purge")
        else:
            print("❌ Opération annulée")
    
    print()
    print("="*70)