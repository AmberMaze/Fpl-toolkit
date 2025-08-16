'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Brain, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react'

interface TeamPlayer {
  id: number
  name: string
  position: string
  cost: number
  total_points: number
  form: number
  selected_by_percent: number
  predicted_points: number
}

interface TeamAnalysis {
  total_value: number
  total_points: number
  average_form: number
  recommendations: {
    type: 'transfer' | 'captain' | 'bench'
    message: string
    priority: 'high' | 'medium' | 'low'
  }[]
  weak_positions: string[]
  strong_positions: string[]
}

export default function TeamAnalysisPage() {
  const [teamId, setTeamId] = useState('')
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState<TeamAnalysis | null>(null)
  const [team, setTeam] = useState<TeamPlayer[]>([])

  const analyzeTeam = async () => {
    if (!teamId) return

    setLoading(true)
    try {
      // This would connect to your Python FastAPI backend
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // Simulated API call - replace with actual endpoint
      // const response = await fetch(`${apiUrl}/team/${teamId}/analysis`)
      // const data = await response.json()
      
      // Mock data for demonstration
      const mockTeam: TeamPlayer[] = [
        { id: 1, name: "Alisson", position: "GKP", cost: 5.5, total_points: 85, form: 4.2, selected_by_percent: 28.3, predicted_points: 6.2 },
        { id: 2, name: "Virgil van Dijk", position: "DEF", cost: 6.5, total_points: 92, form: 5.8, selected_by_percent: 22.1, predicted_points: 7.1 },
        { id: 3, name: "Trent Alexander-Arnold", position: "DEF", cost: 7.2, total_points: 98, form: 6.2, selected_by_percent: 31.4, predicted_points: 8.3 },
        { id: 4, name: "Kevin De Bruyne", position: "MID", cost: 12.8, total_points: 115, form: 7.5, selected_by_percent: 43.1, predicted_points: 9.8 },
        { id: 5, name: "Mohamed Salah", position: "MID", cost: 13.1, total_points: 128, form: 7.8, selected_by_percent: 54.2, predicted_points: 10.2 },
        { id: 6, name: "Erling Haaland", position: "FWD", cost: 15.1, total_points: 142, form: 8.2, selected_by_percent: 67.3, predicted_points: 11.5 },
      ]

      const mockAnalysis: TeamAnalysis = {
        total_value: 98.5,
        total_points: 1248,
        average_form: 6.8,
        recommendations: [
          { type: 'captain', message: 'Consider captaining Haaland for his upcoming fixture run', priority: 'high' },
          { type: 'transfer', message: 'Upgrade your midfield with an in-form player', priority: 'medium' },
          { type: 'bench', message: 'Your bench could use a stronger attacking option', priority: 'low' },
        ],
        weak_positions: ['Bench', 'Defense'],
        strong_positions: ['Midfield', 'Forward']
      }

      setTeam(mockTeam)
      setAnalysis(mockAnalysis)
    } catch (error) {
      console.error('Failed to analyze team:', error)
    } finally {
      setLoading(false)
    }
  }

  const getPositionColor = (position: string) => {
    switch (position) {
      case 'GKP': return 'bg-yellow-500'
      case 'DEF': return 'bg-green-500'
      case 'MID': return 'bg-blue-500'
      case 'FWD': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <AlertTriangle className="h-4 w-4 text-red-400" />
      case 'medium': return <TrendingUp className="h-4 w-4 text-yellow-400" />
      case 'low': return <CheckCircle className="h-4 w-4 text-green-400" />
      default: return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-fpl-green via-fpl-purple to-fpl-blue">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="outline" size="icon" className="text-white border-white hover:bg-white hover:text-fpl-purple">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-white">Team Analysis</h1>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="outline" className="text-white border-white hover:bg-white hover:text-fpl-purple">
                Home
              </Button>
            </Link>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Team Input */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-fpl-green" />
              AI Team Analysis
            </CardTitle>
            <CardDescription className="text-white/80">
              Enter your FPL team ID to get AI-powered insights and recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <input
                type="text"
                placeholder="Enter your team ID (e.g., 12345)"
                value={teamId}
                onChange={(e) => setTeamId(e.target.value)}
                className="flex-1 px-4 py-2 rounded-md bg-white/10 border border-white/20 text-white placeholder:text-white/60 focus:outline-none focus:ring-2 focus:ring-white/20"
              />
              <Button 
                onClick={analyzeTeam}
                disabled={loading || !teamId}
                className="bg-white text-fpl-purple hover:bg-gray-100"
              >
                {loading ? 'Analyzing...' : 'Analyze Team'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {analysis && (
          <>
            {/* Analysis Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Team Value</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">£{analysis.total_value}m</div>
                  <p className="text-xs text-white/80">Total squad value</p>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Total Points</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analysis.total_points}</div>
                  <p className="text-xs text-white/80">Season total</p>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Average Form</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analysis.average_form}</div>
                  <p className="text-xs text-white/80">Recent form rating</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Team Players */}
              <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
                <CardHeader>
                  <CardTitle>Your Squad</CardTitle>
                  <CardDescription className="text-white/80">
                    Current team with AI predictions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {team.map((player) => (
                      <div key={player.id} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                        <div className="flex items-center gap-3">
                          <Badge className={`${getPositionColor(player.position)} text-white text-xs px-2 py-0.5`}>
                            {player.position}
                          </Badge>
                          <div>
                            <div className="font-semibold">{player.name}</div>
                            <div className="text-sm text-white/80">£{player.cost}m • {player.total_points} pts</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold">{player.predicted_points}</div>
                          <div className="text-xs text-white/80">predicted</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* AI Recommendations */}
              <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-fpl-purple" />
                    AI Recommendations
                  </CardTitle>
                  <CardDescription className="text-white/80">
                    Personalized insights for your team
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {analysis.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
                        <div className="mt-0.5">
                          {getPriorityIcon(rec.priority)}
                        </div>
                        <div>
                          <div className="font-medium capitalize">{rec.type} Advice</div>
                          <div className="text-sm text-white/80 mt-1">{rec.message}</div>
                          <Badge 
                            variant="secondary" 
                            className={`mt-2 text-xs ${
                              rec.priority === 'high' ? 'bg-red-500/20 text-red-300' :
                              rec.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                              'bg-green-500/20 text-green-300'
                            }`}
                          >
                            {rec.priority} priority
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Position Analysis */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
              <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
                <CardHeader>
                  <CardTitle className="text-green-400">Strong Positions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {analysis.strong_positions.map((position) => (
                      <Badge key={position} className="bg-green-500/20 text-green-300">
                        {position}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
                <CardHeader>
                  <CardTitle className="text-red-400">Areas for Improvement</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {analysis.weak_positions.map((position) => (
                      <Badge key={position} className="bg-red-500/20 text-red-300">
                        {position}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}

        {!analysis && (
          <div className="text-center py-16">
            <div className="text-white/60 text-lg mb-4">
              Enter your team ID above to get started with AI analysis
            </div>
            <div className="text-white/40 text-sm">
              You can find your team ID in the URL when viewing your team on the FPL website
            </div>
          </div>
        )}
      </main>
    </div>
  )
}