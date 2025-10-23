import axios from 'axios'

const API_BASE = (import.meta.env.VITE_API_BASE) ? import.meta.env.VITE_API_BASE : '/api'
const client = axios.create({ baseURL: API_BASE, timeout: 8000 })

export async function apiPost(path, data){
  const res = await client.post(path, data)
  return res.data
}
export async function apiGet(path){
  const res = await client.get(path)
  return res.data
}