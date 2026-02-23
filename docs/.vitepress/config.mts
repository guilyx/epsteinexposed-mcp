import { defineConfig } from "vitepress";

export default defineConfig({
  title: "epsteinexposed-mcp",
  description: "MCP server for querying the Epstein Exposed public API",

  head: [
    [
      "link",
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,700;1,400&family=Special+Elite&display=swap",
      },
    ],
  ],

  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Guide", link: "/guide/getting-started" },
      { text: "Tools API", link: "/api/tools" },
    ],

    sidebar: [
      {
        text: "Guide",
        items: [
          { text: "Getting Started", link: "/guide/getting-started" },
          { text: "Architecture", link: "/guide/architecture" },
          { text: "Configuration", link: "/guide/configuration" },
        ],
      },
      {
        text: "API Reference",
        items: [
          { text: "MCP Tools", link: "/api/tools" },
          { text: "HTTP Client", link: "/api/client" },
        ],
      },
      {
        text: "Deploy",
        items: [
          { text: "Vercel", link: "/deploy/vercel" },
          { text: "Docker", link: "/deploy/docker" },
        ],
      },
    ],

    socialLinks: [
      { icon: "github", link: "https://github.com/guilyx/epsteinexposed-mcp" },
    ],

    footer: {
      message: "Released under the MIT License.",
      copyright: "© 2026 — epsteinexposed-mcp",
    },

    search: {
      provider: "local",
    },
  },
});
