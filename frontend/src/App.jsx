import React from 'react'
import { Outlet, Link } from 'react-router-dom'

export default function App(){
  return (
    <div className="app-root">
      <header className="app-header">
        <Link to="/" className="logo">Voiture Search</Link>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">Prototype — données de test</footer>
    </div>
  )
}