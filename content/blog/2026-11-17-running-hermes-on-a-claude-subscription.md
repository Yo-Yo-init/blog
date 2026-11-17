---
title: "Running My Orchestrator on a Claude Pro Subscription"
date: 2026-11-17
author: Pepper
summary: "How I moved just my orchestrator agent to Claude Sonnet 5.5 using the experimental Claude Subscription DirectSDK plugin, which bills my existing Pro subscription instead of a per-token API key."
tags: [homelab, hermes-agent, claude, llm]
image: /static/images/thumbnails/running-hermes-on-a-claude-subscription.svg
category: ai
draft: false
---

# Running My Orchestrator on a Claude Pro Subscription

Yesterday I wrote about which model runs which of the five agents in my [Hermes team](/blog/which-llm-for-which-agent-november-2026). The orchestrator runs Xiaomi's MiMo-V2.6-Pro on DeepInfra, and I mentioned that if money were no object I would put Claude Sonnet 5.5 there. Money is an object, but I also pay for a Claude Pro subscription every month and mostly use it in a browser tab. So today I asked a rude question: can the subscription pay for my agent instead?

The answer turns out to be yes, through an official Hermes plugin called Claude Subscription DirectSDK, which is marked Experimental for good reasons I'll get into. Today I moved only the orchestrator to Sonnet 5.5. The other four agents are untouched and still run on DeepInfra. Here is how it went, snags included, because there were four and each one taught me something.

## What the plugin actually is

The plugin has the id `claude-subscription-directsdk-experimental` and lives in [Nous Research's official plugins catalog](https://github.com/NousResearch/hermes-official-plugins). It needs Hermes 0.21.4 or newer; I'm on 0.23.0. The clever part is what it doesn't do: it never talks to Anthropic's API with a key, and it never sees an API key at all.

Instead, for every request it launches the unmodified official Claude Code CLI, the same `claude` binary you'd use in a terminal, and uses whatever Claude account that CLI is logged into. Hermes keeps running its normal agent loop with its own tools, approvals, memory and context compaction. Per the plugin's README, each request starts a fresh CLI process in a private temp directory, and Claude Code's own tools, skills, CLAUDE.md files and auto-memory are switched off so Hermes stays in charge. A small local relay forwards only the first upstream request of each call and rejects any extras, so the CLI can't quietly run additional generations behind Hermes' back. The plugin also never reads the CLI's credential files, and it strips any `ANTHROPIC_API_KEY` style variables out of the environment it hands the child process, so there's no silent fallback to key-based billing.

Billing happens against the subscription's Agent SDK allowance, metered in 5-hour windows, and the provider simply inherits the logged-in account. The README says the plugin runs the CLI under the caller name `hermes-agent`, which it measured at roughly 1.7 times less window use than the default `sdk-cli` name. That was measured on a Max plan with Opus 5.5, and Anthropic hasn't documented the weighting, so treat it as one person's data point. The README also notes that the cost figures it shows are list-price equivalents, not what actually leaves your bank account. One thing worth checking: per the README, Sonnet 5.5 is covered by Pro, but some models (Fable 5.x, and Opus with a 1M context) bill usage credits on Pro, so I stayed on Sonnet.

## The install, snags included

I checked prerequisites first: Hermes 0.23.0, Node and npm present, and no stray `ANTHROPIC_*` or `CLAUDE_*` environment variables lying around that could confuse things. Then came snag one.

`npm install -g @anthropic-ai/claude-code` completed without errors, but `claude --version` answered with `claude native binary not installed`. It took me a moment to work out that npm had blocked the package's postinstall script by default on this Node version, and the binary is what the postinstall downloads. The fix was to allow the script for this one package:

```bash
npm install -g --allow-scripts=@anthropic-ai/claude-code @anthropic-ai/claude-code
claude --version    # 2.1.326 (Sonnet needs 2.1.284 or newer)
```

Snag two was smaller. `hermes plugins install claude-subscription-directsdk` pulled it from the pinned catalog happily but left it disabled, so I also needed:

```bash
hermes plugins enable claude-subscription-directsdk-experimental
```

Hermes reloaded its plugins live, which was nice.

Then configuration. Three commands:

```bash
hermes config set model.provider claude-subscription-directsdk-experimental
hermes config set model.default sonnet
hermes config set model.context_length 1048576
```

The short alias `sonnet` resolves to Sonnet 5.5 with a 1M-token context window. When I changed the provider, Hermes cleared my old custom endpoint settings (`base_url` and `api_mode`) automatically, because those belonged to the DeepInfra route. It told me it was doing so, which I appreciated; a config file that quietly forgets things is how 2 a.m. debugging sessions start.

## Decide where the side jobs run, or they'll drain you

This section is the one I'd want you to actually read. Hermes runs small side jobs on the main model unless told otherwise: context compression, session titles, vision analysis. After the switch, every one of those would have been billed against my Pro subscription window. That's a fine use of a subscription if you like it, but I pay per token for the cheap stuff and wanted the subscription budget to go to the turns that matter.

So I pointed compression and title generation at DeepSeek-V4.1-Flash-1017 on DeepInfra. Why DeepSeek and not GLM-5.3-Flash, which my blog agent uses? Both have 1M context and both are very cheap, but DeepSeek scores higher on the coding and agentic benchmarks in DeepInfra's own [model page](https://deepinfra.com/deepseek-ai/DeepSeek-V4.1-Flash-1017), and it's already in use by three of my other agents, so the fleet gains no new model to keep track of.

Here I hit the snag I'm proudest of avoiding. I first wrote `provider: main` in the auxiliary config, reasoning that "main" is a word that means something everywhere. `hermes doctor` flagged it as an unknown provider and warned that the task "silently runs on the main model". That is the exact opposite of what I was trying to achieve, and nothing else in the setup would have warned me. The built-in `deepinfra` provider name resolved correctly, and after the fix doctor reported compression and title generation pointing at the DeepInfra endpoint. Moral: run `hermes doctor` after touching auxiliary routing.

The fallback got the same treatment. I set `fallback_model` to provider `deepinfra`, model `XiaomiMiMo/MiMo-V2.6-Pro`, so a rate limit or an outage drops back to yesterday's orchestrator model instead of failing the turn. I used `main` there at first too, then switched to `deepinfra`, because doctor's output said nothing about the fallback entry and I did not want an untested safety net. `hermes fallback list` shows primary `sonnet`, then the MiMo fallback.

One more hardening step. per the README, Hermes' stall watchdog can be off for local process-based providers on some 1M model ids, so a hung call could otherwise wait out the full read timeout. I set `providers.claude-subscription-directsdk-experimental.stale_timeout_seconds: 900` so a stuck CLI process gets cut off after fifteen minutes.

## Login, restart, and the snag that wasn't

Logging in was snag four. `claude auth login` failed with `claude: command not found`, because npm had installed the CLI under Hermes' own node tools directory, which is on Hermes' PATH but not my interactive shell's. The plugin searches a list of directories including `~/.local/bin`, so I symlinked the binary there and it worked from both places. Then `claude auth login` opened the browser OAuth flow, which I completed by hand, and `claude auth status` confirmed I was logged in with subscription type `pro`.

Finally: `hermes gateway restart`, which has to be run from outside the running gateway. The log then showed `Model context warmed: sonnet -> 1000000 tokens`, and we were live.

The thing that didn't go wrong deserves its own paragraph. My first message to the orchestrator happened before I had logged in. The Claude call failed with an authentication error, "Claude Code is installed but has no usable login", and Hermes automatically switched that single turn to the MiMo fallback and answered normally. I saw nothing break from the chat side; I only found the error in the log afterwards. So the fallback I had set up earlier in the same session got tested by accident, in real conditions, and passed. That's a better outcome than any test I would have written on purpose.

## Early numbers, with honest caveats

These come from my gateway log on day one, for the orchestrator session only. The conversation prompt is about 92K tokens per turn, because it's a long-lived chat with a lot of context in it.

| Call | Input tokens | Cache read |
|---|---|---|
| 1 (cold start) | 91,709 | written, not read |
| 2 | 96,599 | 95% |
| 3 | 97,553 | 99% |
| 4 | 117,567 | 83% (a large tool result arrived) |

Latency ran 4.7 to 7.3 seconds per call. Vision requests auto-detect the main provider, so image analysis now also goes through the subscription; per the plugin README, pinned routes declare vision and send images natively.

The cache numbers matter because the README mentions an earlier long-context test showing poor cache reuse (3.66% on a 187K-token request), which was fixed by disabling the native reminder, after which follow-up requests averaged about 98% cache reads. My session behaves like the fixed version, which is reassuring.

Now the caveats, plainly. It is day one. I send roughly 40 orchestrator turns a day and I have no multi-day data on how that interacts with the Pro 5-hour window, so I will be watching `/usage` this week. I'm not claiming cost savings. The honest framing is this: I've traded per-token pricing for a fixed monthly cost with a usage ceiling, and I don't yet know whether Pro's allowance is enough for my orchestrator. If it isn't, the options are a bigger plan or moving back.

## The config, trimmed to the relevant parts

```yaml
# orchestrator profile config.yaml
model:
  default: sonnet
  provider: claude-subscription-directsdk-experimental
  context_length: 1048576
auxiliary:
  compression:
    provider: deepinfra
    model: deepseek-ai/DeepSeek-V4.1-Flash-1017
  title_generation:
    provider: deepinfra
    model: deepseek-ai/DeepSeek-V4.1-Flash-1017
fallback_model:
  provider: deepinfra
  model: XiaomiMiMo/MiMo-V2.6-Pro
providers:
  claude-subscription-directsdk-experimental:
    stale_timeout_seconds: 900
```

No API key appears here. The Claude side uses the CLI login, and the DeepInfra side authenticates through the `DEEPINFRA_API_KEY` environment variable. If I want to roll back, it's `hermes config set model.provider custom`, `hermes config set model.default XiaomiMiMo/MiMo-V2.6-Pro`, restore the DeepInfra base_url, restart the gateway. I haven't run the full rollback, so treat it as untested but short.

## Should you do this?

Three questions. Do you already pay for Claude Pro or Max? Is the agent you're moving one where a stronger model pays for itself in fewer retries and better tool calls? And are you comfortable running something the author explicitly calls "a review build, not a full-parity or production-readiness claim"? The README also warns that text arriving after tool rounds can come as one block instead of streaming smoothly (their issue #33).

If those answers are yes, the parts that cost me the most time were the two things nothing warned me about: the npm postinstall block and the `provider: main` trap in auxiliary routing. Keep the side jobs off the subscription, keep a fallback on a per-token provider, and run `hermes doctor` after every routing change.

If your agent does hundreds of turns a day, do the arithmetic on your plan's allowance first. And if you don't have a subscription at all, this post gives you nothing to save money on, which is fine.

*Models, plugins and plan limits move fast. Everything above reflects my setup as of November 17, 2026.*

*Sources: [Claude Subscription DirectSDK on the Hermes marketplace](https://hermes-agent.nousresearch.com/marketplace/claude-subscription-directsdk), [Hermes Official Plugins on GitHub](https://github.com/NousResearch/hermes-official-plugins) (plugin directory: `claude-subscription-directsdk`), [DeepSeek-V4.1-Flash-1017 on DeepInfra](https://deepinfra.com/deepseek-ai/DeepSeek-V4.1-Flash-1017).*
