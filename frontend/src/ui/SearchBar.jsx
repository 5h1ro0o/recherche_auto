import React, { useState } from 'react'

export default function SearchBar({ onSearch, defaultValue='' }){
  const [value, setValue] = useState(defaultValue)
  return (
    <div className="search-bar">
      <input value={value} onChange={e=>setValue(e.target.value)} placeholder="Ex: volkswagen golf" />
      <button onClick={()=>onSearch(value)}>Rechercher</button>
    </div>
  )
}