# Rendered Architecture Diagrams

| Asset | Purpose |
|---|---|
| `high-level-architecture.svg` | Source, edge, platform, and Supabase trust/data boundaries. |
| `stream-fanout.svg` | Video stream manager fanout and independent face/visual/storage pipelines. |
| `context-fusion.svg` | Event-time fusion of asynchronous observations and event revisions. |

These SVG files are checked into source control so agents can inspect, render, and update diagrams without a proprietary editor. Every diagram change must be reviewed with the affected architecture text and ADR.
