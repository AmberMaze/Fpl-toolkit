# FPL Toolkit Frontend

A modern Next.js frontend for the FPL Toolkit, optimized for deployment on Vercel.

## 🚀 Features

- **Next.js 14** with App Router and TypeScript
- **Tailwind CSS** for styling with custom FPL-themed colors
- **Responsive Design** optimized for mobile and desktop
- **API Integration** with the Python FastAPI backend
- **AI-Powered Interface** for team analysis and recommendations
- **Vercel-Ready** deployment configuration

## 📋 Prerequisites

- Node.js 18+ and npm
- Running FPL Toolkit Python backend (see parent directory)

## 🛠️ Development Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Configuration

Create `.env.local` file:

```bash
# API Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Disable telemetry
NEXT_TELEMETRY_DISABLED=1
```

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🏗️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## 🌐 Deployment

### Deploy to Vercel

1. **Connect Repository**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy
   vercel
   ```

2. **Environment Variables**
   Set in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api.render.com
   ```

3. **Auto-Deploy**
   Vercel will automatically deploy on every push to main branch.

### Deploy with Docker

```bash
# Build
docker build -t fpl-toolkit-frontend .

# Run
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://your-backend fpl-toolkit-frontend
```

## 📱 Pages & Features

### Home Page (`/`)
- Hero section with feature overview
- Technology stack showcase
- Navigation to main features

### Dashboard (`/dashboard`)
- FPL statistics overview
- Top performers and trending players
- Quick action buttons

### Team Analysis (`/team-analysis`)
- AI-powered team analysis
- Player recommendations
- Squad overview with predictions
- Position strength analysis

## 🔧 API Integration

The frontend connects to the Python FastAPI backend via:

```typescript
// Example API usage
import { fplApi } from '@/lib/api'

const players = await fplApi.getPlayers({ position: 'MID', limit: 10 })
const analysis = await fplApi.getTeamAdvisor(teamId, { budget: 100 })
```

### Available API Methods

- `getPlayers()` - Fetch player data
- `getTeamAdvisor()` - Get AI recommendations
- `analyzeTransferScenario()` - Transfer analysis
- `comparePlayerProjections()` - Player comparisons

## 🎨 Styling & Design

### Color Scheme
- **FPL Green**: `#38ef7d` to `#11998e`
- **FPL Purple**: `#667eea` to `#764ba2`
- **FPL Blue**: `#4facfe` to `#00f2fe`

### Components
- Reusable UI components in `/src/components/ui/`
- Responsive grid layouts
- Glass-morphism effects with backdrop blur
- Gradient backgrounds matching FPL branding

## 📁 Project Structure

```
frontend/
├── public/
│   ├── logo.svg           # FPL Toolkit logo
│   ├── manifest.json      # PWA manifest
│   └── robots.txt         # SEO configuration
├── src/
│   ├── app/
│   │   ├── dashboard/     # Dashboard page
│   │   ├── team-analysis/ # Team analysis page
│   │   ├── globals.css    # Global styles
│   │   ├── layout.tsx     # Root layout
│   │   └── page.tsx       # Home page
│   ├── components/
│   │   └── ui/            # Reusable UI components
│   ├── lib/
│   │   ├── api.ts         # API client
│   │   └── utils.ts       # Utility functions
│   └── types/
│       └── fpl.ts         # TypeScript type definitions
├── next.config.js         # Next.js configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
└── vercel.json            # Vercel deployment configuration
```

## 🔗 Integration with Backend

The frontend is designed to work seamlessly with the Python FastAPI backend:

1. **API Endpoints**: All backend endpoints are accessible via the API client
2. **CORS**: Configured to work with the backend's CORS settings
3. **Environment Variables**: Backend URL configurable via environment variables
4. **Error Handling**: Graceful degradation when backend is unavailable

## 🚀 Production Considerations

### Performance
- Static generation where possible
- Image optimization with Next.js Image component
- Automatic code splitting
- Tree shaking for minimal bundle size

### SEO
- Server-side rendering
- Meta tags optimization
- Structured data markup
- XML sitemap generation

### Security
- Environment variable validation
- XSS protection headers
- CSRF protection
- Secure cookie settings

## 📖 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Vercel Deployment](https://vercel.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.