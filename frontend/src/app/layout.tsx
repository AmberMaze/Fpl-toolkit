import './globals.css'

export const metadata = {
  title: 'FPL Toolkit',
  description: 'Fantasy Premier League analysis and decision support toolkit with AI-powered recommendations',
  keywords: 'fantasy premier league, FPL, football, soccer, analysis, AI, recommendations',
  authors: [{ name: 'Amber Bridgers' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  )
}