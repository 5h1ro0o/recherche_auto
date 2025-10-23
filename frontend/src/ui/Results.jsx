import React from 'react'
import { Link } from 'react-router-dom'

export default function Results({ loading, results, total, page=1, onPageChange }){
  return (
    <div>
      <div className="results-meta">{total} résultat(s)</div>
      {loading && <div>Chargement...</div>}
      {!loading && results.length === 0 && <div>Aucun résultat</div>}
      <div className="results-grid">
        {results.map(r => (
          <Link key={r.id} to={`/vehicle/${encodeURIComponent(r.id)}`} className="result-card">
            <div className="result-title">{r.source?.title || `${r.source?.make || ''} ${r.source?.model || ''}`}</div>
            <div className="result-sub">{r.source?.price ? r.source.price + ' €' : ''}</div>
          </Link>
        ))}
      </div>
      <div className="pagination">
        {page > 1 && <button onClick={()=>onPageChange(page-1)}>Préc.</button>}
        <span>Page {page}</span>
        {results.length > 0 && <button onClick={()=>onPageChange(page+1)}>Suiv.</button>}
      </div>
    </div>
  )
}