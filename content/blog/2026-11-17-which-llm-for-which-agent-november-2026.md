---
title: "Which LLM for Which Agent? My Hermes Team, November 2026 Edition"
date: 2026-11-17
author: Pepper
summary: "Which model runs each of my five Hermes agents and why: the dream picks, the cheap models I actually run, and what each team costs per month — a mid-November 2026 snapshot."
tags: [homelab, hermes-agent, llm, deepinfra]
image: /static/images/thumbnails/which-llm-for-which-agent-november-2026.svg
hero_alt: "Line drawing of a balance scale with one large gem on one pan and five small chips on the other."
draft: false
---


Quick disclaimer before anything else: this post has a shelf life of about a month. Since September alone we've had new Claude, GPT, Gemini, Kimi and DeepSeek releases, and prices keep moving with them. Google's Gemini 4 prices double on December 1. Treat everything below as a snapshot of mid-November 2026, not gospel. If you're reading this in the spring, half these models have probably been replaced.

With that out of the way: people keep asking what model runs my [Hermes Agent](https://github.com/NousResearch/hermes-agent) setup. The answer is a different one for each agent, because each one fails in a different way.

For anyone new here, it's one Hermes install on a small control box in the lab, hooked into Discord, split into five profiles:

- **Orchestrator** takes my plain-English requests, writes a plan and a dry run, waits for my OK, then hands the work off.
- **Homelab** runs the Docker VM and the media server (configs, Ansible, updates, health checks).
- **Blog** drafts posts from my notes.
- **Librarian** keeps our wiki and answers questions with citations.
- **Study** is my CCNA coach.

For each one I'll give the model I'd use if money didn't matter, and the one I actually run. My rule for the second list was keeping the whole team well under $20 a month.

## Where the money actually goes

Every turn, Hermes re-sends the system prompt, tool definitions, memory and conversation history. For me that's around 15k input tokens per turn, and replies are usually under 1k. So you're mostly paying to re-read context, which makes the cached-input price the number that matters most. My estimates assume about 80% of input hits the cache and this daily load: orchestrator 40 turns, homelab 30, blog 20, librarian 60, study 40.

## The picks

**Orchestrator.** If money were no object I'd run Claude Sonnet 5.5 ($2 in / $10 out). The r/hermesagent crowd has rated Claude the most reliable at tool calling for a while ([Agent37](https://www.agent37.com/blog/best-model-for-hermes-agent)), and Sonnet 5.5 is fast, which you notice when you're reading replies on your phone. I actually run Xiaomi's MiMo-V2.6-Pro on DeepInfra ($0.435 / $0.87, cached $0.0036). I started on GPT-6 Luna, but my orchestrator writes the plans I approve, and Luna wasn't really up to that. MiMo sits in the 97th percentile on PricePerToken's intelligence index ([PricePerToken](https://pricepertoken.com/pricing-page/model/xiaomi-mimo-v2.6-pro)) and was built for multi-step agent work. That's about $2.45 a month versus about $19.70.

**Homelab.** This is the agent that touches real servers, so it's where I'd spend first. The best choice right now is Claude Opus 5.5 ($4 / $20), which leads the current terminal and coding boards ([Vellum](https://www.vellum.ai/llm-leaderboard), [BenchLeader](https://www.benchleader.com/)). I run DeepSeek V4.1 Flash, pinned to the `-1017` snapshot so it doesn't change on me ($0.20 / $0.60, cached $0.006). DeepSeek reports it matching proprietary flagships on agentic coding ([arXiv](https://arxiv.org/pdf/2609.19969)). I'm comfortable running a cheap model here because of the approval loop: nothing changes without a dry run I've signed off on, and Homelab backs up before it acts and checks the result after. About $1 a month versus about $27.

**Blog.** Opus 5.5 again. It's at the top of the human-voted Arena creative writing board ([Chapter](https://blog.chapter.pub/best-llm-for-creative-writing/)). I run GLM-5.3-Flash ($0.15 / $0.50), which Capital & Compute calls the best value for Hermes overall ([Capital & Compute](https://capitalandcompute.net/md/best-models-for-hermes-agent.md)). Its prose is a little flat, but I rewrite everything anyway, this post included. About $0.75 versus about $18.

**Librarian.** The worst thing a wiki agent can do is make something up with confidence, so I'd pick Gemini 4 Argon. It had the lowest hallucination rate on Artificial Analysis's AA-Omniscience test among models that answer most questions correctly ([Suprmind](https://suprmind.ai/hub/de/?page_id=3793)). It's $2 / $10 now and $4 / $20 from December 1 ([FourWeekMBA](https://fourweekmba.com/ai-gemini-4-models-explained-carbon-argon-hydrogen-prices/)). I run DeepSeek V4.1 Flash 1017. At $0.006 per million cached tokens, re-reading the wiki all day costs basically nothing, and DeepInfra has it at 51% off right now ([DeepInfra](https://deepinfra.com/deepseek-ai/DeepSeek-V4.1-Flash-1017)). About $2 versus about $55, which makes the Librarian my most expensive agent on the dream list.

**Study.** Gemini 4 Carbon currently tops the general intelligence rankings ([PricePerToken](https://pricepertoken.com/pricing-page/model/google-gemini-4-carbon), [BenchLM](https://benchlm.ai/agentic)), and it reads screenshots, which is handy for Packet Tracer labs. It's on the same December price change as Argon. I run DeepSeek V4.1 Flash 1017 here too. It handles images, and its GPQA Diamond score (a test of graduate-level science questions) is 90.9%, which is a lot of reasoning for the money. I still check anything that sounds off against Cisco's docs. About $1.40 versus about $36.

## The totals

| Agent | If money didn't matter | /mo | What I run | /mo |
|---|---|---|---|---|
| Orchestrator | Claude Sonnet 5.5 | $19.70 | MiMo-V2.6-Pro | $2.45 |
| Homelab | Claude Opus 5.5 | $27.40 | DeepSeek V4.1 Flash 1017 | $1.05 |
| Blog | Claude Opus 5.5 | $18.25 | GLM-5.3-Flash | $0.75 |
| Librarian | Gemini 4 Argon | $54.70 | DeepSeek V4.1 Flash 1017 | $2.05 |
| Study | Gemini 4 Carbon | $36.50 | DeepSeek V4.1 Flash 1017 | $1.40 |
| **Total** | | **~$156** | | **~$7.70** |

The fancy team costs about 20 times more, and for a homelab it's nowhere near 20 times better. One caveat: these numbers depend on caching. If your cache keeps missing, my setup goes from about $7.70 to about $24 a month, and the fancy one to nearly $390. Keep each profile's toolset small and put recurring work on cron instead of letting agents loop.

If I had another $20 a month to spend, it would go to Homelab first (Sonnet or Opus 5.5), then to the full GLM-5.3 for final blog drafts.

## Wiring it up

The thing that tripped me up: by default Hermes sends every subagent to the same model, set by one global `delegation.model` ([GitHub #15789](https://github.com/NousResearch/hermes-agent/issues/15789)). To give each agent its own model, make each one a [profile](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) with its own `config.yaml`. Then add a small delegation plugin that routes tasks to profiles. Hermes doesn't include one, but [the developer docs have a ~20-line example](https://hermes-agent.nousresearch.com/docs/developer-guide/delegation-provider-plugin). DeepInfra is a [built-in provider](https://docs.deepinfra.com/integrations/hermes-agent) (I wire mine through its OpenAI-compatible endpoint), so all five agents run on one API key.

Two settings worth copying. DeepSeek V4.x has thinking turned off by default on DeepInfra ([Hermes docs](https://hermes-agent.nousresearch.com/docs/integrations/providers)), so turn it on. And point the auxiliary slots (compression, titles and so on) at something cheap, or they quietly run on your main model:

```yaml
# ~/.hermes/profiles/homelab/config.yaml
model:
  default: deepseek-ai/DeepSeek-V4.1-Flash-1017
  provider: custom
  base_url: https://api.deepinfra.com/v1/openai
  api_key: ${DEEPINFRA_API_KEY}
  api_mode: chat_completions
agent:
  reasoning_effort: high
auxiliary:
  compression: { provider: custom, model: zai-org/GLM-5.3-Flash }
```

## Last thing

The biggest lesson from all this is that the harness matters as much as the model. The plan, dry run, approve, back up, verify loop is why I trust a one-dollar model on my servers.

Start cheap, watch your usage page for a week, then upgrade one agent at a time, starting with the one that can break something. And check back in a month or two, because I'll probably be running something different by then.

*Prices checked November 17, 2026. More sources: [DeepSeek V4.1 Flash pricing](https://deepinfra.com/blog/deepseek-v4-1-flash-pricing-guide), [MiMo-V2.6-Pro](https://deepinfra.com/blog/mimo-v2-6-pro-deepinfra), [GLM-5.3-Flash](https://deepinfra.com/zai-org/GLM-5.3-Flash/voice), [Opus 5.5 pricing](https://betanews.com/article/claude-opus-5-5-launch-price-cut/), [Sonnet 5.5 pricing](https://smartscope.blog/en/blog/claude-sonnet-5-5-same-price-30-faster-2026/).*