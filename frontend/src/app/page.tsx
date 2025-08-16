import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Trophy, TrendingUp, Brain, Smartphone, Database, Zap } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-fpl-green via-fpl-purple to-fpl-blue">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Trophy className="h-8 w-8 text-white" />
            <h1 className="text-2xl font-bold text-white">FPL Toolkit</h1>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="outline" className="text-white border-white hover:bg-white hover:text-fpl-purple">
                Dashboard
              </Button>
            </Link>
            <Link href="/team-analysis">
              <Button className="bg-white text-fpl-purple hover:bg-gray-100">
                Team Analysis
              </Button>
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-12">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            FPL Toolkit
          </h1>
          <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto">
            AI-powered Fantasy Premier League analysis and decision support toolkit with 
            mobile-friendly APIs and advanced analytics
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/dashboard">
              <Button size="lg" className="bg-white text-fpl-purple hover:bg-gray-100 text-lg px-8">
                Get Started
              </Button>
            </Link>
            <Link href="#features">
              <Button size="lg" variant="outline" className="text-white border-white hover:bg-white hover:text-fpl-purple text-lg px-8">
                Learn More
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <section id="features" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader>
              <Brain className="h-12 w-12 text-fpl-green mb-4" />
              <CardTitle>AI-Powered Advisor</CardTitle>
              <CardDescription className="text-white/80">
                Intelligent team analysis and transfer recommendations using advanced machine learning
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Smart transfer suggestions</li>
                <li>• Performance predictions</li>
                <li>• Risk assessment</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader>
              <TrendingUp className="h-12 w-12 text-fpl-purple mb-4" />
              <CardTitle>Advanced Analytics</CardTitle>
              <CardDescription className="text-white/80">
                Comprehensive fixture difficulty, player projections, and performance metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Fixture difficulty analysis</li>
                <li>• Expected goals (xG/xA)</li>
                <li>• Form tracking</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader>
              <Smartphone className="h-12 w-12 text-fpl-blue mb-4" />
              <CardTitle>Mobile-Friendly API</CardTitle>
              <CardDescription className="text-white/80">
                RESTful endpoints optimized for mobile access with efficient caching
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Compact JSON responses</li>
                <li>• CORS enabled</li>
                <li>• Responsive design</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader>
              <Database className="h-12 w-12 text-fpl-green mb-4" />
              <CardTitle>Database Integration</CardTitle>
              <CardDescription className="text-white/80">
                SQLite fallback with optional PostgreSQL support for robust data management
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Historical data tracking</li>
                <li>• Performance caching</li>
                <li>• Scalable architecture</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader>
              <Zap className="h-12 w-12 text-fpl-purple mb-4" />
              <CardTitle>Real-time Updates</CardTitle>
              <CardDescription className="text-white/80">
                Live data synchronization with the official FPL API
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Live score tracking</li>
                <li>• Price change alerts</li>
                <li>• Injury updates</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardHeader>
              <Trophy className="h-12 w-12 text-fpl-blue mb-4" />
              <CardTitle>Command Line Tools</CardTitle>
              <CardDescription className="text-white/80">
                Powerful CLI interface for automation and advanced analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li>• Automated reports</li>
                <li>• Batch processing</li>
                <li>• Script integration</li>
              </ul>
            </CardContent>
          </Card>
        </section>

        {/* Technology Stack */}
        <section className="text-center">
          <h2 className="text-3xl font-bold text-white mb-8">Built with Modern Technology</h2>
          <div className="flex flex-wrap justify-center gap-4">
            <Badge variant="secondary" className="bg-white/20 text-white text-lg py-2 px-4">
              Python FastAPI
            </Badge>
            <Badge variant="secondary" className="bg-white/20 text-white text-lg py-2 px-4">
              Next.js 14
            </Badge>
            <Badge variant="secondary" className="bg-white/20 text-white text-lg py-2 px-4">
              TypeScript
            </Badge>
            <Badge variant="secondary" className="bg-white/20 text-white text-lg py-2 px-4">
              Tailwind CSS
            </Badge>
            <Badge variant="secondary" className="bg-white/20 text-white text-lg py-2 px-4">
              SQLAlchemy
            </Badge>
            <Badge variant="secondary" className="bg-white/20 text-white text-lg py-2 px-4">
              AI/ML Models
            </Badge>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 mt-16 border-t border-white/20">
        <div className="text-center text-white/80">
          <p>&copy; 2024 FPL Toolkit. Built with ❤️ for the FPL community.</p>
          <div className="flex justify-center gap-6 mt-4">
            <Link href="/docs" className="hover:text-white">
              Documentation
            </Link>
            <Link href="/api" className="hover:text-white">
              API Reference
            </Link>
            <Link href="https://github.com/AmberMaze/Fpl-toolkit" className="hover:text-white">
              GitHub
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}