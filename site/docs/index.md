---
layout: home
hero:
  name: "Knowledge Base"
  text: "AI-Powered Documentation"
  tagline: Search, ask questions, and explore articles.
  actions:
    - theme: brand
      text: Explore Articles
      link: '#articles'
    - theme: alt
      text: Ask AI
      link: '#ai-chat'
features:
  - title: 📚 Article List
    details: "Browse all indexed documents."
  - title: 🤖 AI Assistant
    details: "Ask questions and get answers based on the docs."
---

<div id="ai-chat" style="margin: 3rem 0;">
  <AiChat />
</div>

<hr style="margin: 3rem 0; border: none; border-top: 1px solid var(--vp-c-divider);" />

<div id="articles" style="margin: 3rem 0;">
  <ArticleList />
</div>