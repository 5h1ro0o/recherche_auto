import React, { useState } from 'react'

export default function SearchBar({ onSearch, defaultValue = '' }) {
  const [value, setValue] = useState(defaultValue)

  function handleSubmit(e) {
    e.preventDefault()
    onSearch(value)
  }

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        maxWidth: '800px',
        margin: '0 auto 32px auto',
        display: 'flex',
        gap: '12px',
        padding: '0 20px',
      }}
    >
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Ex: Volkswagen Golf, Peugeot 208, Renault Clio..."
        style={{
          flex: 1,
          padding: '14px 20px',
          fontSize: '16px',
          border: '2px solid #E5E7EB',
          borderRadius: '12px',
          outline: 'none',
          transition: 'all 0.2s',
          fontFamily: 'inherit',
        }}
        onFocus={(e) => {
          e.target.style.borderColor = '#4F46E5'
          e.target.style.boxShadow = '0 0 0 3px rgba(79, 70, 229, 0.1)'
        }}
        onBlur={(e) => {
          e.target.style.borderColor = '#E5E7EB'
          e.target.style.boxShadow = 'none'
        }}
      />
      <button
        type="submit"
        style={{
          padding: '14px 32px',
          background: '#4F46E5',
          color: 'white',
          border: 'none',
          borderRadius: '12px',
          fontSize: '16px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all 0.2s',
          fontFamily: 'inherit',
          whiteSpace: 'nowrap',
        }}
        onMouseEnter={(e) => {
          e.target.style.background = '#4338CA'
          e.target.style.transform = 'translateY(-1px)'
          e.target.style.boxShadow = '0 4px 12px rgba(79, 70, 229, 0.3)'
        }}
        onMouseLeave={(e) => {
          e.target.style.background = '#4F46E5'
          e.target.style.transform = 'translateY(0)'
          e.target.style.boxShadow = 'none'
        }}
      >
        🔍 Rechercher
      </button>
    </form>
  )
}