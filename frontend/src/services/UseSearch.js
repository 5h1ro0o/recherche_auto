import { useQuery } from '@tanstack/react-query'
import { apiPost } from './api'

export function useSearch(q, page){
  return useQuery(['search', q, page], async () => {
    const payload = { q, page, size: 10 }
    return await apiPost('/search', payload)
  }, { enabled: false })
}