import React, { useState } from 'react'
import SearchBar from '../ui/SearchBar'
import Results from '../ui/Results'
import { useSearch } from '../services/useSearch'

export default function SearchPage(){
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading, isError, refetch } = useSearch(q, page)

  function onSearch(term){
    setQ(term)
    setPage(1)
    refetch()
  }

  return (
    <div>
      <SearchBar onSearch={onSearch} defaultValue={q} />
      {isError && <div className="error">Erreur lors de la recherche</div>}
      <Results
        loading={isLoading}
        results={data?.hits || []}
        total={data?.total || 0}
        page={page}
        onPageChange={setPage}
      />
    </div>
  )
}