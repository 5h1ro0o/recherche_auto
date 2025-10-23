import React from 'react'
import { useParams } from 'react-router-dom'
import useSWR from 'swr'
import { apiGet } from '../services/api'

export default function VehiclePage(){
  const { id } = useParams()
  const { data, error } = useSWR(id ? `/vehicles/${id}` : null, () => apiGet(`/vehicles/${id}`))

  if(error) return <div className="error">Erreur chargement véhicule</div>
  if(!data) return <div>Chargement...</div>

  const v = data
  return (
    <div className="vehicle-detail">
      <h2>{v.title || `${v.make} ${v.model}`}</h2>
      <div>Prix : {v.price ? v.price + ' €' : '—'}</div>
      <div>Année : {v.year}</div>
      <div>Kilométrage : {v.mileage}</div>
      <div>VIN : {v.vin || '—'}</div>
      <div className="images">{(v.images || []).map((u,i)=>(<img key={i} src={u} alt="photo"/>))}</div>
    </div>
  )
}