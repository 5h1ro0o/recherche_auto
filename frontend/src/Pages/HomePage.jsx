// frontend/src/Pages/HomePage.jsx
import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function HomePage() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Trouvez votre véhicule idéal avec l'intelligence artificielle
          </h1>
          <p className="hero-subtitle">
            La première plateforme française qui combine recherche intelligente multi-sources
            et accompagnement personnalisé par des experts automobiles
          </p>
          <div className="hero-actions">
            <Link to="/search" className="btn-primary btn-large">
              🔍 Commencer ma recherche
            </Link>
            {!isAuthenticated && (
              <Link to="/register" className="btn-secondary btn-large">
                Créer mon compte gratuit
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="services-section">
        <h2 className="section-title">Nos Services</h2>
        <div className="services-grid">
          <div className="service-card">
            <div className="service-icon">🔍</div>
            <h3>Recherche Multi-Sources</h3>
            <p>
              Accédez simultanément à des milliers d'annonces provenant de LeBonCoin,
              AutoScout24 et bien d'autres plateformes. Un seul formulaire,
              tous les résultats.
            </p>
            <Link to="/search" className="service-link">
              Essayer maintenant →
            </Link>
          </div>

          <div className="service-card">
            <div className="service-icon">🤖</div>
            <h3>Filtres Intelligents</h3>
            <p>
              Notre IA analyse vos critères et vous propose uniquement les véhicules
              qui correspondent vraiment à vos besoins : budget, kilométrage,
              année, carburant et plus encore.
            </p>
            <Link to="/search" className="service-link">
              Découvrir les filtres →
            </Link>
          </div>

          <div className="service-card">
            <div className="service-icon">🤝</div>
            <h3>Mode Assisté</h3>
            <p>
              Vous ne savez pas par où commencer ? Nos experts automobiles analysent
              votre demande et vous proposent une sélection personnalisée de véhicules
              adaptés à votre profil.
            </p>
            {isAuthenticated ? (
              <Link to="/assisted" className="service-link">
                Faire une demande →
              </Link>
            ) : (
              <Link to="/register" className="service-link">
                S'inscrire pour y accéder →
              </Link>
            )}
          </div>

          <div className="service-card">
            <div className="service-icon">📚</div>
            <h3>Encyclopédie Auto</h3>
            <p>
              Consultez notre base de connaissances complète sur les marques,
              modèles, motorisations et conseils d'achat. Tout ce qu'il faut
              savoir avant d'acheter.
            </p>
            <Link to="/encyclopedia" className="service-link">
              Explorer l'encyclopédie →
            </Link>
          </div>

          <div className="service-card">
            <div className="service-icon">❤️</div>
            <h3>Favoris & Alertes</h3>
            <p>
              Sauvegardez vos annonces préférées et recevez des alertes en temps
              réel quand de nouveaux véhicules correspondant à vos critères sont
              publiés.
            </p>
            {isAuthenticated ? (
              <Link to="/favorites" className="service-link">
                Voir mes favoris →
              </Link>
            ) : (
              <Link to="/register" className="service-link">
                S'inscrire pour y accéder →
              </Link>
            )}
          </div>

          <div className="service-card">
            <div className="service-icon">💬</div>
            <h3>Messagerie Intégrée</h3>
            <p>
              Communiquez directement avec nos experts pour affiner votre recherche,
              poser des questions techniques ou obtenir des conseils personnalisés.
            </p>
            {isAuthenticated ? (
              <Link to="/messages" className="service-link">
                Mes messages →
              </Link>
            ) : (
              <Link to="/register" className="service-link">
                S'inscrire pour y accéder →
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works-section">
        <h2 className="section-title">Comment ça marche ?</h2>
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Définissez vos critères</h3>
            <p>
              Renseignez votre budget, le type de véhicule souhaité,
              le kilométrage maximal, l'année minimum et d'autres filtres précis.
            </p>
          </div>

          <div className="step-arrow">→</div>

          <div className="step">
            <div className="step-number">2</div>
            <h3>Notre IA recherche pour vous</h3>
            <p>
              En quelques secondes, nous parcourons des milliers d'annonces
              sur plusieurs plateformes et ne gardons que celles qui correspondent.
            </p>
          </div>

          <div className="step-arrow">→</div>

          <div className="step">
            <div className="step-number">3</div>
            <h3>Consultez et comparez</h3>
            <p>
              Visualisez tous les résultats au même endroit, ajoutez vos favoris,
              et demandez l'aide d'un expert si besoin.
            </p>
          </div>

          <div className="step-arrow">→</div>

          <div className="step">
            <div className="step-number">4</div>
            <h3>Trouvez votre véhicule</h3>
            <p>
              Contactez le vendeur directement via le lien de l'annonce
              et finalisez votre achat en toute confiance.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">500K+</div>
            <div className="stat-label">Annonces analysées</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">3</div>
            <div className="stat-label">Plateformes connectées</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">24/7</div>
            <div className="stat-label">Veille automatique</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">100%</div>
            <div className="stat-label">Gratuit</div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <h2>Prêt à trouver votre prochaine voiture ?</h2>
        <p>
          Rejoignez des milliers d'utilisateurs qui ont simplifié leur recherche
          de véhicule grâce à notre plateforme.
        </p>
        <div className="cta-actions">
          <Link to="/search" className="btn-primary btn-large">
            Lancer une recherche
          </Link>
          {!isAuthenticated && (
            <Link to="/register" className="btn-outline btn-large">
              Créer un compte
            </Link>
          )}
        </div>
      </section>
    </div>
  )
}
