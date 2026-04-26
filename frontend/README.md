# Frontend Application

Next.js frontend for AI-Powered Talent Scouting & Engagement Agent.

## Deployed URL

- `https://scout-fh5lj7zv8-nikhith221bs-projects.vercel.app/`

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create a `.env.local` file (do not commit this file to Git):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── app/
│   ├── api/          # API client functions
│   ├── components/   # React components
│   ├── lib/          # Utility functions
│   ├── globals.css   # Global styles
│   ├── layout.tsx    # Root layout
│   └── page.tsx      # Homepage
├── package.json
├── tailwind.config.js
└── next.config.js
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint