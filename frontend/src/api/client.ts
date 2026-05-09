import axios from 'axios'

const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL ?? '/api',
    withCredentials: true,  // send HttpOnly cookie on every request
})

export default client
