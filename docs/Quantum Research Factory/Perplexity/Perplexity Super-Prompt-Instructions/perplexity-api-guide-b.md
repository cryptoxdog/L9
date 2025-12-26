<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# I need a comprehensive instruction manual on how to send queries to perplexity using API and an agent for semi autonomous research include the different types of search explaining what they are and went to use each research. Best practices how to do research this way for maximum scale, maximum leverage minimum manual labor, maximum autonomy, and make sure there are examples of each of the query types.

Output:downloadable markdown

I've created a comprehensive instruction manual on using Perplexity's API for semi-autonomous research. The downloadable markdown file covers everything you need to build scalable research agents with maximum automation and minimum manual labor.

## What's Included in the Manual:

### 📚 Core Content

**1. Complete Model Guide** - Detailed breakdown of all 5 Sonar models (Sonar, Sonar Pro, Sonar Reasoning, Sonar Reasoning Pro, and Sonar Deep Research) with specific use cases, cost comparisons, and when to use each.[^1][^2][^3][^4][^5]

**2. Search Types Explained**:

- **Auto Search** - Automatically routes to fast or pro search based on complexity
- **Fast Search** - Optimized for speed and simple queries
- **Pro Search** - Deep analysis with extensive citations
- **Search API** - Direct web search without AI synthesis
- **Deep Research** - Autonomous multi-step research across hundreds of sources[^2][^6][^7][^8]

**3. Semi-Autonomous Research Architectures**:

- Multi-agent parallel research (3x faster than sequential)
- Iterative deep dive patterns
- Autonomous research with quality control loops[^5][^9][^10]


### 💻 10+ Production-Ready Code Examples

Each example includes complete working code for:

1. Simple fact lookup (Sonar)
2. Comprehensive research (Sonar Pro)
3. Logical analysis with reasoning (Sonar Reasoning Pro)
4. Autonomous deep research reports (Sonar Deep Research)
5. Multi-query batch searches
6. Domain-filtered academic research
7. Regional searches with country filters
8. Streaming responses for real-time display
9. Error handling with exponential backoff
10. Async batch processing for maximum throughput[^11][^6][^12][^13]

### ⚡ Best Practices for Maximum Scale

**Rate Limit Management**:

- Sonar models: 50 requests/minute
- Deep Research: 5 requests/minute
- Search API: 3 requests/second with burst capacity[^14][^13]

**Cost Optimization Strategies**:

- Intelligent query routing (automatically select cheapest suitable model)
- Caching to avoid redundant calls
- Multi-query batching (5 queries in 1 API call saves 80% on costs)
- Progressive enhancement (start cheap, upgrade if needed)[^6][^15][^8]

**Batch Processing**:

- Async operations with controlled concurrency
- Token bucket algorithm for rate limiting
- Exponential backoff for error recovery[^13][^16][^6]


### 🛡️ Error Handling \& Recovery

Complete error handling patterns for:

- Rate limit errors (429)
- Connection failures
- Authentication issues
- Validation errors
- Automatic retry with exponential backoff[^16][^17]


### 🏗️ Advanced Patterns

1. **Progressive Enhancement Research** - Start with fast model, progressively enhance based on quality assessment
2. **Fact-Checking with Cross-Validation** - Validate claims across multiple sources
3. **Continuous Learning Agent** - Builds persistent knowledge base over time[^9][^10]

### 💰 Cost \& Performance Matrix

| Model | Speed | Citations | Cost/Query | Best For |
| :-- | :-- | :-- | :-- | :-- |
| Sonar | ⚡⚡⚡⚡⚡ | ⭐⭐ | \$0.005 | Quick facts |
| Sonar Pro | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | \$0.020 | Deep citations |
| Sonar Reasoning Pro | ⚡⚡ | ⭐⭐⭐⭐ | \$0.030 | Complex analysis |
| Sonar Deep Research | ⚡ | ⭐⭐⭐⭐⭐ | \$0.50-\$2 | Autonomous reports |

[^3][^18][^15][^8][^5]

The manual is designed for developers building production research systems. Each code example is production-ready with proper error handling, rate limiting, and cost optimization built in. Download the markdown file to get started building your semi-autonomous research agent!
<span style="display:none">[^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40][^41]</span>

<div align="center">⁂</div>

[^1]: https://ai-sdk.dev/providers/ai-sdk-providers/perplexity

[^2]: https://docs.perplexity.ai/guides/search-quickstart

[^3]: https://docs.perplexity.ai/getting-started/models/models/sonar

[^4]: https://docs.perplexity.ai/getting-started/models/models/sonar-deep-research

[^5]: https://www.perplexity.ai/hub/blog/perplexity-sonar-dominates-new-search-arena-evolution

[^6]: https://docs.perplexity.ai/guides/search-best-practices

[^7]: https://docs.perplexity.ai/api-reference/search-post

[^8]: https://docs.perplexity.ai/guides/pro-search-quickstart

[^9]: https://inference-docs.cerebras.ai/cookbook/agents/build-your-own-perplexity

[^10]: https://www.reddit.com/r/perplexity_ai/comments/1inv2ey/i_built_a_deep_research_agent_with_perplexity_api/

[^11]: https://docs.perplexity.ai/guides/perplexity-sdk-search

[^12]: https://docs.perplexity.ai/guides/streaming-responses

[^13]: https://docs.perplexity.ai/guides/perplexity-sdk-best-practices

[^14]: https://docs.perplexity.ai/guides/rate-limits-usage-tiers

[^15]: https://www.photonpay.com/hk/blog/article/perplexity-ai-pricing?lang=en

[^16]: https://docs.perplexity.ai/guides/perplexity-sdk-error-handling

[^17]: https://www.hostingseekers.com/blog/fix-perplexity-api-errors-tutorial/

[^18]: https://www.datastudios.org/post/all-perplexity-models-available-in-2025-complete-list-with-sonar-family-gpt-5-claude-gemini-and

[^19]: https://community.clay.com/x/support/rs5vevcvh174/troubleshooting-perplexity-ai-api-429-rate-limit-e

[^20]: https://docs.superblocks.com/integrations/integrations-library/perplexity

[^21]: https://docs.perplexity.ai/feature-roadmap

[^22]: https://www.typingmind.com/guide/use-perplexity-api-key-to-chat-with-ai

[^23]: https://www.apideck.com/blog/how-to-get-your-perplexity-api-key

[^24]: https://www.sparka.ai/compare/perplexity/sonar-reasoning-pro

[^25]: https://apidog.com/blog/perplexity-search-api/

[^26]: https://www.perplexity.ai/help-center/en/articles/10354919-what-advanced-ai-models-are-included-in-my-subscription

[^27]: https://docs.uipath.com/integration-service/automation-cloud/latest/user-guide/uipath-perplexity-perplexity-authentication

[^28]: https://docs.ag2.ai/latest/docs/user-guide/reference-tools/perplexity-search/

[^29]: https://brightdata.com/blog/web-data/web-scraping-with-perplexity

[^30]: https://apidog.com/blog/perplexity-ai-api/

[^31]: https://docs.perplexity.ai/cookbook/examples/README

[^32]: https://www.youtube.com/watch?v=xzmqSXL0jRU

[^33]: https://docs.perplexity.ai/guides/pro-search-stream-mode-guide

[^34]: https://www.reddit.com/r/perplexity_ai/comments/1jbky3f/ridiculous_api_cost_of_perplexity_ai/

[^35]: https://www.youtube.com/watch?v=46XRqjOjzE0

[^36]: https://docs.perplexity.ai/getting-started/quickstart

[^37]: https://www.kerlig.com/blog/perplexity-deep-research

[^38]: https://savemyleads.com/blog/useful/sonar-by-perplexity

[^39]: https://www.twelvelabs.io/blog/video-deep-research

[^40]: https://www.reddit.com/r/perplexity_ai/comments/1bk89zz/perplexity_team_you_have_a_serious_user_error/

[^41]: https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research

