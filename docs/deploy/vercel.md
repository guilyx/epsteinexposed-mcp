# Deploy to Vercel

Deploy the documentation site to [Vercel](https://vercel.com) for instant, globally-distributed access.

## Prerequisites

- A [Vercel](https://vercel.com) account
- The repository connected to Vercel (GitHub integration)

## Option A: One-Click Import

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import the `guilyx/epstein-files-mcp` repository
3. Configure the build settings:

| Setting            | Value              |
|--------------------|--------------------|
| Framework Preset   | VitePress          |
| Root Directory     | `docs`             |
| Build Command      | `npm run build`    |
| Output Directory   | `.vitepress/dist`  |
| Install Command    | `npm ci`           |
| Node.js Version    | 22.x               |

4. Click **Deploy**

## Option B: Vercel CLI

```bash
# Install the Vercel CLI
npm i -g vercel

# From the repo root
cd docs
vercel
```

Follow the prompts. Vercel auto-detects VitePress.

## Configuration

The `docs/vercel.json` handles SPA routing:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".vitepress/dist",
  "installCommand": "npm ci",
  "framework": "vitepress",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

## Auto-Deploy

Once connected, Vercel will:

- **Auto-deploy** on every push to `main`
- **Preview deploy** on every pull request
- Provide a unique URL for each deployment

## Custom Domain

1. Go to your project in the Vercel dashboard
2. Navigate to **Settings → Domains**
3. Add your custom domain
4. Update your DNS records as instructed

## Environment Variables

No environment variables are required for the docs site. The documentation is fully static.
