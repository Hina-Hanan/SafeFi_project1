import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

type RiskScore = { protocol: string; score: number }

export function useRiskScore(protocol: string) {
  return useQuery<RiskScore>({
    queryKey: ['risk', protocol],
    queryFn: async () => {
      const { data } = await axios.get(`/api/risk/score`, { params: { protocol } })
      return data
    },
  })
}



