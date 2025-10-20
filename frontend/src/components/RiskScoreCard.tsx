import { Card, CardContent, Typography } from '@mui/material'
import { useRiskScore } from '../hooks/useRiskScore'

export default function RiskScoreCard({ protocol }: { protocol: string }) {
  const { data, isLoading, error } = useRiskScore(protocol)

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Risk Score: {protocol}</Typography>
        {isLoading && <Typography>Loading...</Typography>}
        {error && <Typography color="error">Failed to load</Typography>}
        {data && <Typography variant="h4">{Math.round(data.score * 100)} / 100</Typography>}
      </CardContent>
    </Card>
  )
}



