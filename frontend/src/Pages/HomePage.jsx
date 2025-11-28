import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function HomePage() {
  const { isAuthenticated } = useAuth()

  return (
    <div>
      {/* Hero Section */}
      <section style={{
        background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
        color: 'white',
        padding: '80px 20px',
        textAlign: 'center',
      }}>
        <div style={{
          maxWidth: '900px',
          margin: '0 auto',
        }}>
          <h1 style={{
            fontSize: '48px',
            fontWeight: 700,
            margin: '0 0 24px 0',
            lineHeight: 1.2,
          }}>
            Trouvez votre véhicule idéal avec l'intelligence artificielle
          </h1>
          <p style={{
            fontSize: '20px',
            margin: '0 0 40px 0',
            opacity: 0.95,
            lineHeight: 1.6,
          }}>
            La première plateforme française qui combine recherche intelligente multi-sources
            et accompagnement personnalisé par des experts automobiles
          </p>
          <div style={{
            display: 'flex',
            gap: '16px',
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}>
            <Link
              to="/search"
              style={{
                padding: '16px 32px',
                background: 'white',
                color: '#4F46E5',
                textDecoration: 'none',
                borderRadius: '12px',
                fontSize: '18px',
                fontWeight: 600,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.15)',
                transition: 'all 0.2s',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)'
                e.target.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.2)'
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)'
                e.target.style.boxShadow = '0 4px 24px rgba(0, 0, 0, 0.15)'
              }}
            >
              <span>🔍</span>
              <span>Commencer ma recherche</span>
            </Link>
            {!isAuthenticated && (
              <Link
                to="/register"
                style={{
                  padding: '16px 32px',
                  background: 'transparent',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '12px',
                  fontSize: '18px',
                  fontWeight: 600,
                  border: '2px solid white',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.1)'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'transparent'
                }}
              >
                Créer mon compte gratuit
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section style={{
        padding: '80px 20px',
        background: '#F9FAFB',
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
        }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: 700,
            textAlign: 'center',
            margin: '0 0 16px 0',
            color: '#222222',
          }}>
            Nos Services
          </h2>
          <p style={{
            fontSize: '18px',
            textAlign: 'center',
            color: '#6B7280',
            margin: '0 0 48px 0',
          }}>
            Tout ce dont vous avez besoin pour trouver votre véhicule
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '24px',
          }}>
            <ServiceCard
              icon="🔍"
              title="Recherche Multi-Sources"
              description="Accédez simultanément à des milliers d'annonces provenant de LeBonCoin, AutoScout24 et bien d'autres plateformes. Un seul formulaire, tous les résultats."
              link="/search"
              linkText="Essayer maintenant →"
            />

            <ServiceCard
              icon="🤖"
              title="Filtres Intelligents"
              description="Notre IA analyse vos critères et vous propose uniquement les véhicules qui correspondent vraiment à vos besoins : budget, kilométrage, année, carburant et plus encore."
              link="/search"
              linkText="Découvrir les filtres →"
            />

            <ServiceCard
              icon="🤝"
              title="Mode Assisté"
              description="Vous ne savez pas par où commencer ? Nos experts automobiles analysent votre demande et vous proposent une sélection personnalisée de véhicules adaptés à votre profil."
              link={isAuthenticated ? "/assisted" : "/register"}
              linkText={isAuthenticated ? "Faire une demande →" : "S'inscrire pour y accéder →"}
            />

            <ServiceCard
              icon="📚"
              title="Encyclopédie Auto"
              description="Consultez notre base de connaissances complète sur les marques, modèles, motorisations et conseils d'achat. Tout ce qu'il faut savoir avant d'acheter."
              link="/encyclopedia"
              linkText="Explorer l'encyclopédie →"
            />

            <ServiceCard
              icon="❤️"
              title="Favoris & Alertes"
              description="Sauvegardez vos annonces préférées et recevez des alertes en temps réel quand de nouveaux véhicules correspondant à vos critères sont publiés."
              link={isAuthenticated ? "/favorites" : "/register"}
              linkText={isAuthenticated ? "Voir mes favoris →" : "S'inscrire pour y accéder →"}
            />

            <ServiceCard
              icon="💬"
              title="Messagerie Intégrée"
              description="Communiquez directement avec nos experts pour affiner votre recherche, poser des questions techniques ou obtenir des conseils personnalisés."
              link={isAuthenticated ? "/messages" : "/register"}
              linkText={isAuthenticated ? "Mes messages →" : "S'inscrire pour y accéder →"}
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section style={{
        padding: '80px 20px',
        background: 'white',
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
        }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: 700,
            textAlign: 'center',
            margin: '0 0 16px 0',
            color: '#222222',
          }}>
            Comment ça marche ?
          </h2>
          <p style={{
            fontSize: '18px',
            textAlign: 'center',
            color: '#6B7280',
            margin: '0 0 64px 0',
          }}>
            Trouvez votre véhicule en 4 étapes simples
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '32px',
            alignItems: 'center',
          }}>
            <StepCard
              number="1"
              title="Définissez vos critères"
              description="Renseignez votre budget, le type de véhicule souhaité, le kilométrage maximal, l'année minimum et d'autres filtres précis."
            />

            <ArrowSeparator />

            <StepCard
              number="2"
              title="Notre IA recherche pour vous"
              description="En quelques secondes, nous parcourons des milliers d'annonces sur plusieurs plateformes et ne gardons que celles qui correspondent."
            />

            <ArrowSeparator />

            <StepCard
              number="3"
              title="Consultez et comparez"
              description="Visualisez tous les résultats au même endroit, ajoutez vos favoris, et demandez l'aide d'un expert si besoin."
            />

            <ArrowSeparator />

            <StepCard
              number="4"
              title="Trouvez votre véhicule"
              description="Contactez le vendeur directement via le lien de l'annonce et finalisez votre achat en toute confiance."
            />
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section style={{
        padding: '64px 20px',
        background: 'linear-gradient(135deg, #1F2937 0%, #111827 100%)',
        color: 'white',
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '40px',
            textAlign: 'center',
          }}>
            <StatCard number="500K+" label="Annonces analysées" />
            <StatCard number="3" label="Plateformes connectées" />
            <StatCard number="24/7" label="Veille automatique" />
            <StatCard number="100%" label="Gratuit" />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section style={{
        padding: '80px 20px',
        background: 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
        textAlign: 'center',
      }}>
        <div style={{
          maxWidth: '700px',
          margin: '0 auto',
        }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: 700,
            margin: '0 0 16px 0',
            color: '#222222',
          }}>
            Prêt à trouver votre prochaine voiture ?
          </h2>
          <p style={{
            fontSize: '18px',
            color: '#6B7280',
            margin: '0 0 40px 0',
            lineHeight: 1.6,
          }}>
            Rejoignez des milliers d'utilisateurs qui ont simplifié leur recherche
            de véhicule grâce à notre plateforme.
          </p>
          <div style={{
            display: 'flex',
            gap: '16px',
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}>
            <Link
              to="/search"
              style={{
                padding: '16px 32px',
                background: '#4F46E5',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '12px',
                fontSize: '18px',
                fontWeight: 600,
                transition: 'all 0.2s',
                boxShadow: '0 4px 12px rgba(79, 70, 229, 0.3)',
              }}
              onMouseEnter={(e) => {
                e.target.style.background = '#4338CA'
                e.target.style.transform = 'translateY(-2px)'
                e.target.style.boxShadow = '0 8px 24px rgba(79, 70, 229, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = '#4F46E5'
                e.target.style.transform = 'translateY(0)'
                e.target.style.boxShadow = '0 4px 12px rgba(79, 70, 229, 0.3)'
              }}
            >
              Lancer une recherche
            </Link>
            {!isAuthenticated && (
              <Link
                to="/register"
                style={{
                  padding: '16px 32px',
                  background: 'white',
                  color: '#4F46E5',
                  textDecoration: 'none',
                  borderRadius: '12px',
                  fontSize: '18px',
                  fontWeight: 600',
                  border: '2px solid #4F46E5',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = '#4F46E5'
                  e.target.style.color = 'white'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'white'
                  e.target.style.color = '#4F46E5'
                }}
              >
                Créer un compte
              </Link>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}

function ServiceCard({ icon, title, description, link, linkText }) {
  return (
    <div
      style={{
        background: 'white',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
        transition: 'all 0.3s',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-8px)'
        e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.15)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = '0 4px 24px rgba(0, 0, 0, 0.08)'
      }}
    >
      <div style={{
        fontSize: '48px',
        marginBottom: '16px',
      }}>
        {icon}
      </div>
      <h3 style={{
        fontSize: '22px',
        fontWeight: 600,
        margin: '0 0 12px 0',
        color: '#222222',
      }}>
        {title}
      </h3>
      <p style={{
        fontSize: '15px',
        color: '#6B7280',
        lineHeight: 1.6,
        margin: '0 0 20px 0',
        flex: 1,
      }}>
        {description}
      </p>
      <Link
        to={link}
        style={{
          color: '#4F46E5',
          textDecoration: 'none',
          fontWeight: 600,
          fontSize: '15px',
          display: 'inline-flex',
          alignItems: 'center',
        }}
        onMouseEnter={(e) => e.target.style.textDecoration = 'underline'}
        onMouseLeave={(e) => e.target.style.textDecoration = 'none'}
      >
        {linkText}
      </Link>
    </div>
  )
}

function StepCard({ number, title, description }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{
        width: '72px',
        height: '72px',
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto 20px auto',
        fontSize: '32px',
        fontWeight: 700,
        color: 'white',
        boxShadow: '0 4px 16px rgba(79, 70, 229, 0.3)',
      }}>
        {number}
      </div>
      <h3 style={{
        fontSize: '20px',
        fontWeight: 600,
        margin: '0 0 12px 0',
        color: '#222222',
      }}>
        {title}
      </h3>
      <p style={{
        fontSize: '14px',
        color: '#6B7280',
        lineHeight: 1.6,
        margin: 0,
      }}>
        {description}
      </p>
    </div>
  )
}

function ArrowSeparator() {
  return (
    <div style={{
      textAlign: 'center',
      fontSize: '32px',
      color: '#4F46E5',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      →
    </div>
  )
}

function StatCard({ number, label }) {
  return (
    <div>
      <div style={{
        fontSize: '48px',
        fontWeight: 700,
        marginBottom: '8px',
        background: 'linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
      }}>
        {number}
      </div>
      <div style={{
        fontSize: '16px',
        opacity: 0.9,
      }}>
        {label}
      </div>
    </div>
  )
}
