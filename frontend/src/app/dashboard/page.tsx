'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, TrendingUp, Users, Target, Brain } from 'lucide-react'

interface Player {
  id: number
  name: string
  team_id: number
  position: string
  cost: number
  total_points: number
  form: number
  selected_by_percent: number
  status: string
}

interface DashboardStats {
  total_players: number
  average_cost: number
  top_performers: Player[]
  trending_players: Player[]
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // This would connect to your Python FastAPI backend
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        
        // Simulated API call - replace with actual endpoint
        // const response = await fetch(`${apiUrl}/players?limit=5`)
        // const data = await response.json()
        
        // Mock data for demonstration
        const mockData: DashboardStats = {
          total_players: 635,
          average_cost: 5.8,
          top_performers: [
            { id: 1, name: "Erling Haaland", team_id: 11, position: "FWD", cost: 15.1, total_points: 142, form: 8.2, selected_by_percent: 67.3, status: "a" },
            { id: 2, name: "Mohamed Salah", team_id: 12, position: "MID", cost: 13.1, total_points: 128, form: 7.8, selected_by_percent: 54.2, status: "a" },
            { id: 3, name: "Kevin De Bruyne", team_id: 11, position: "MID", cost: 12.8, total_points: 115, form: 7.5, selected_by_percent: 43.1, status: "a" },
          ],
          trending_players: [
            { id: 4, name: "Bukayo Saka", team_id: 1, position: "MID", cost: 9.2, total_points: 98, form: 8.5, selected_by_percent: 34.7, status: "a" },
            { id: 5, name: "Ivan Toney", team_id: 4, position: "FWD", cost: 8.1, total_points: 87, form: 9.2, selected_by_percent: 28.9, status: "a" },
          ]
        }
        
        setStats(mockData)
      } catch (err) {
        setError('Failed to fetch dashboard data')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const getPositionColor = (position: string) => {
    switch (position) {
      case 'GKP': return 'bg-yellow-500'
      case 'DEF': return 'bg-green-500'
      case 'MID': return 'bg-blue-500'
      case 'FWD': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-fpl-green via-fpl-purple to-fpl-blue flex items-center justify-center">
        <div className="text-white text-xl">Loading dashboard...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-fpl-green via-fpl-purple to-fpl-blue flex items-center justify-center">
        <div className="text-white text-xl">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-fpl-green via-fpl-purple to-fpl-blue">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="outline" size="icon" className="text-white border-white hover:bg-white hover:text-fpl-purple">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-white">FPL Dashboard</h1>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/team-analysis">
              <Button className="bg-white text-fpl-purple hover:bg-gray-100">
                Team Analysis
              </Button>
            </Link>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Players</CardTitle>
              <Users className="h-4 w-4 text-fpl-green" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.total_players}</div>
              <p className="text-xs text-white/80">Available in the game</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Cost</CardTitle>
              <Target className="h-4 w-4 text-fpl-purple" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">£{stats?.average_cost}m</div>
              <p className="text-xs text-white/80">Per player</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">AI Analysis</CardTitle>
              <Brain className="h-4 w-4 text-fpl-blue" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Active</div>
              <p className="text-xs text-white/80">Ready for insights</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Performers */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-fpl-green" />
                Top Performers
              </CardTitle>
              <CardDescription className="text-white/80">
                Highest scoring players this season
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats?.top_performers.map((player, index) => (
                  <div key={player.id} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                    <div className="flex items-center gap-3">
                      <div className="text-lg font-bold text-white/60">#{index + 1}</div>
                      <div>
                        <div className="font-semibold">{player.name}</div>
                        <div className="flex items-center gap-2">
                          <Badge className={`${getPositionColor(player.position)} text-white text-xs px-2 py-0.5`}>
                            {player.position}
                          </Badge>
                          <span className="text-sm text-white/80">£{player.cost}m</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold">{player.total_points}</div>
                      <div className="text-sm text-white/80">points</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Trending Players */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-fpl-purple" />
                Trending Players
              </CardTitle>
              <CardDescription className="text-white/80">
                Players with best recent form
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats?.trending_players.map((player, index) => (
                  <div key={player.id} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                    <div className="flex items-center gap-3">
                      <div className="text-lg font-bold text-white/60">#{index + 1}</div>
                      <div>
                        <div className="font-semibold">{player.name}</div>
                        <div className="flex items-center gap-2">
                          <Badge className={`${getPositionColor(player.position)} text-white text-xs px-2 py-0.5`}>
                            {player.position}
                          </Badge>
                          <span className="text-sm text-white/80">£{player.cost}m</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold">{player.form}</div>
                      <div className="text-sm text-white/80">form</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 text-center">
          <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/team-analysis">
              <Button size="lg" className="bg-white text-fpl-purple hover:bg-gray-100">
                Analyze Team
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="text-white border-white hover:bg-white hover:text-fpl-purple">
              Find Transfers
            </Button>
            <Button size="lg" variant="outline" className="text-white border-white hover:bg-white hover:text-fpl-purple">
              Player Search
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}