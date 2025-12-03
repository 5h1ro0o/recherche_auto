import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function HomePage() {
  const { isAuthenticated } = useAuth()

  return (
    <div>
      {/* Hero Section */}
      <section style={{
        background: 'var(--white)',
        position: 'relative',
        overflow: 'hidden',
        borderBottom: '1px solid var(--border-light)'
      }}>
        {/* Gloss overlay */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '400px',
          background: 'var(--gloss-overlay)',
          pointerEvents: 'none'
        }} />

        <div style={{
          maxWidth: 'var(--container-xl)',
          margin: '0 auto',
          padding: 'var(--space-20) var(--space-6)',
          textAlign: 'center',
          position: 'relative',
          zIndex: 1
        }}>
          <h1 style={{
            fontSize: '56px',
            fontWeight: 'var(--font-weight-bold)',
            margin: '0 0 var(--space-6) 0',
            lineHeight: 1.1,
            color: 'var(--text-primary)',
            letterSpacing: '-0.03em'
          }}>
            Trouvez votre véhicule idéal
          </h1>
          <p style={{
            fontSize: '20px',
            margin: '0 0 var(--space-10) 0',
            color: 'var(--text-secondary)',
            lineHeight: 1.6,
            maxWidth: '800px',
            marginLeft: 'auto',
            marginRight: 'auto',
            fontWeight: 'var(--font-weight-medium)'
          }}>
            La première plateforme française qui combine recherche intelligente multi-sources
            et accompagnement personnalisé par des experts automobiles
          </p>
          <div style={{
            display: 'flex',
            gap: 'var(--space-4)',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Link
              to="/search"
              className="btn btn-primary"
              style={{
                padding: 'var(--space-4) var(--space-8)',
                fontSize: '16px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontWeight: 'var(--font-weight-semibold)'
              }}
            >
              Commencer ma recherche
            </Link>
            {!isAuthenticated && (
              <Link
                to="/register"
                className="btn btn-secondary"
                style={{
                  padding: 'var(--space-4) var(--space-8)',
                  fontSize: '16px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  fontWeight: 'var(--font-weight-semibold)'
                }}
              >
                Créer mon compte
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section style={{
        padding: 'var(--space-20) var(--space-6)',
        background: 'var(--gray-50)'
      }}>
        <div style={{
          maxWidth: 'var(--container-2xl)',
          margin: '0 auto'
        }}>
          <h2 style={{
            fontSize: '40px',
            fontWeight: 'var(--font-weight-semibold)',
            textAlign: 'center',
            margin: '0 0 var(--space-4) 0',
            color: 'var(--text-primary)',
            letterSpacing: '-0.02em'
          }}>
            Nos Services
          </h2>
          <p style={{
            fontSize: '18px',
            textAlign: 'center',
            color: 'var(--text-secondary)',
            margin: '0 0 var(--space-12) 0',
            fontWeight: 'var(--font-weight-medium)'
          }}>
            Tout ce dont vous avez besoin pour trouver votre véhicule
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
            gap: 'var(--space-6)'
          }}>
            <ServiceCard
              title="Recherche Multi-Sources"
              description="Accédez simultanément à des milliers d'annonces provenant de LeBonCoin, AutoScout24 et bien d'autres plateformes. Un seul formulaire, tous les résultats."
              link="/search"
              linkText="Essayer maintenant"
            />

            <ServiceCard
              title="Filtres Intelligents"
              description="Notre IA analyse vos critères et vous propose uniquement les véhicules qui correspondent vraiment à vos besoins : budget, kilométrage, année, carburant et plus encore."
              link="/search"
              linkText="Découvrir les filtres"
            />

            <ServiceCard
              title="Mode Assisté"
              description="Vous ne savez pas par où commencer ? Nos experts automobiles analysent votre demande et vous proposent une sélection personnalisée de véhicules adaptés à votre profil."
              link={isAuthenticated ? "/assisted" : "/register"}
              linkText={isAuthenticated ? "Faire une demande" : "S'inscrire pour y accéder"}
            />

            <ServiceCard
              title="Encyclopédie Auto"
              description="Consultez notre base de connaissances complète sur les marques, modèles, motorisations et conseils d'achat. Tout ce qu'il faut savoir avant d'acheter."
              link="/encyclopedia"
              linkText="Explorer l'encyclopédie"
            />

            <ServiceCard
              title="Favoris & Alertes"
              description="Sauvegardez vos annonces préférées et recevez des alertes en temps réel quand de nouveaux véhicules correspondant à vos critères sont publiés."
              link={isAuthenticated ? "/favorites" : "/register"}
              linkText={isAuthenticated ? "Voir mes favoris" : "S'inscrire pour y accéder"}
            />

            <ServiceCard
              title="Messagerie Intégrée"
              description="Communiquez directement avec nos experts pour affiner votre recherche, poser des questions techniques ou obtenir des conseils personnalisés."
              link={isAuthenticated ? "/messages" : "/register"}
              linkText={isAuthenticated ? "Mes messages" : "S'inscrire pour y accéder"}
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section style={{
        padding: 'var(--space-20) var(--space-6)',
        background: 'var(--white)'
      }}>
        <div style={{
          maxWidth: 'var(--container-2xl)',
          margin: '0 auto'
        }}>
          <h2 style={{
            fontSize: '40px',
            fontWeight: 'var(--font-weight-semibold)',
            textAlign: 'center',
            margin: '0 0 var(--space-4) 0',
            color: 'var(--text-primary)',
            letterSpacing: '-0.02em'
          }}>
            Comment ça marche ?
          </h2>
          <p style={{
            fontSize: '18px',
            textAlign: 'center',
            color: 'var(--text-secondary)',
            margin: '0 0 var(--space-16) 0',
            fontWeight: 'var(--font-weight-medium)'
          }}>
            Trouvez votre véhicule en 4 étapes simples
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 'var(--space-8)',
            alignItems: 'start'
          }}>
            <StepCard
              number="1"
              title="Définissez vos critères"
              description="Renseignez votre budget, le type de véhicule souhaité, le kilométrage maximal, l'année minimum et d'autres filtres précis."
            />

            <StepCard
              number="2"
              title="Notre IA recherche pour vous"
              description="En quelques secondes, nous parcourons des milliers d'annonces sur plusieurs plateformes et ne gardons que celles qui correspondent."
            />

            <StepCard
              number="3"
              title="Consultez et comparez"
              description="Visualisez tous les résultats au même endroit, ajoutez vos favoris, et demandez l'aide d'un expert si besoin."
            />

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
        padding: 'var(--space-16) var(--space-6)',
        background: 'var(--gray-900)',
        color: 'var(--white)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Subtle gloss */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '200px',
          background: 'linear-gradient(180deg, rgba(255,255,255,0.02) 0%, transparent 100%)',
          pointerEvents: 'none'
        }} />

        <div style={{
          maxWidth: 'var(--container-2xl)',
          margin: '0 auto',
          position: 'relative',
          zIndex: 1
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 'var(--space-10)',
            textAlign: 'center'
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
        padding: 'var(--space-20) var(--space-6)',
        background: 'var(--gray-50)',
        textAlign: 'center'
      }}>
        <div style={{
          maxWidth: '700px',
          margin: '0 auto'
        }}>
          <h2 style={{
            fontSize: '40px',
            fontWeight: 'var(--font-weight-semibold)',
            margin: '0 0 var(--space-4) 0',
            color: 'var(--text-primary)',
            letterSpacing: '-0.02em'
          }}>
            Prêt à trouver votre prochaine voiture ?
          </h2>
          <p style={{
            fontSize: '18px',
            color: 'var(--text-secondary)',
            margin: '0 0 var(--space-10) 0',
            lineHeight: 1.6,
            fontWeight: 'var(--font-weight-medium)'
          }}>
            Rejoignez des milliers d'utilisateurs qui ont simplifié leur recherche
            de véhicule grâce à notre plateforme.
          </p>
          <div style={{
            display: 'flex',
            gap: 'var(--space-4)',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Link
              to="/search"
              className="btn btn-primary"
              style={{
                padding: 'var(--space-4) var(--space-8)',
                fontSize: '16px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontWeight: 'var(--font-weight-semibold)'
              }}
            >
              Lancer une recherche
            </Link>
            {!isAuthenticated && (
              <Link
                to="/register"
                className="btn btn-secondary"
                style={{
                  padding: 'var(--space-4) var(--space-8)',
                  fontSize: '16px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  fontWeight: 'var(--font-weight-semibold)'
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

function ServiceCard({ title, description, link, linkText }) {
  return (
    <div
      style={{
        background: 'var(--white)',
        border: '1px solid var(--border-light)',
        padding: 'var(--space-8)',
        boxShadow: 'var(--shadow-gloss-sm)',
        transition: 'all var(--transition-base)',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'hidden'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)'
        e.currentTarget.style.boxShadow = 'var(--shadow-gloss-lg)'
        e.currentTarget.style.borderColor = 'var(--border-medium)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = 'var(--shadow-gloss-sm)'
        e.currentTarget.style.borderColor = 'var(--border-light)'
      }}
    >
      {/* Top gloss bar */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '2px',
        background: 'var(--red-accent)',
        opacity: 0
      }} />

      <h3 style={{
        fontSize: '20px',
        fontWeight: 'var(--font-weight-semibold)',
        margin: '0 0 var(--space-3) 0',
        color: 'var(--text-primary)',
        letterSpacing: '-0.01em'
      }}>
        {title}
      </h3>
      <p style={{
        fontSize: '15px',
        color: 'var(--text-secondary)',
        lineHeight: 1.6,
        margin: '0 0 var(--space-5) 0',
        flex: 1,
        fontWeight: 'var(--font-weight-regular)'
      }}>
        {description}
      </p>
      <Link
        to={link}
        style={{
          color: 'var(--red-accent)',
          textDecoration: 'none',
          fontWeight: 'var(--font-weight-semibold)',
          fontSize: '14px',
          display: 'inline-flex',
          alignItems: 'center',
          gap: 'var(--space-2)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          transition: 'all var(--transition-fast)'
        }}
        onMouseEnter={(e) => {
          e.target.style.gap = 'var(--space-3)'
        }}
        onMouseLeave={(e) => {
          e.target.style.gap = 'var(--space-2)'
        }}
      >
        {linkText}
        <span style={{ fontSize: '12px' }}>→</span>
      </Link>
    </div>
  )
}

function StepCard({ number, title, description }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{
        width: '80px',
        height: '80px',
        background: 'var(--gray-900)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto var(--space-5) auto',
        fontSize: '36px',
        fontWeight: 'var(--font-weight-bold)',
        color: 'var(--white)',
        boxShadow: 'var(--shadow-gloss-md)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Gloss effect */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '40px',
          background: 'linear-gradient(180deg, rgba(255,255,255,0.1) 0%, transparent 100%)',
          pointerEvents: 'none'
        }} />
        <span style={{ position: 'relative', zIndex: 1 }}>{number}</span>
      </div>
      <h3 style={{
        fontSize: '18px',
        fontWeight: 'var(--font-weight-semibold)',
        margin: '0 0 var(--space-3) 0',
        color: 'var(--text-primary)',
        letterSpacing: '-0.01em'
      }}>
        {title}
      </h3>
      <p style={{
        fontSize: '14px',
        color: 'var(--text-secondary)',
        lineHeight: 1.6,
        margin: 0,
        fontWeight: 'var(--font-weight-regular)'
      }}>
        {description}
      </p>
    </div>
  )
}

function StatCard({ number, label }) {
  return (
    <div>
      <div style={{
        fontSize: '56px',
        fontWeight: 'var(--font-weight-bold)',
        marginBottom: 'var(--space-2)',
        color: 'var(--white)',
        letterSpacing: '-0.02em'
      }}>
        {number}
      </div>
      <div style={{
        fontSize: '16px',
        opacity: 0.8,
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        fontWeight: 'var(--font-weight-medium)',
        color: 'var(--white)'
      }}>
        {label}
      </div>
    </div>
  )
}
