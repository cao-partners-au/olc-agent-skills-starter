# REA: reverse-engineering tools (project use only)

**What it is.** REA ("Reverse Engineer Anything") connects your AI agent to professional reverse-engineering tools (Ghidra, Hopper, IDA and others), so it can take apart software you don't have the source code for and explain how a feature works. It covers desktop apps, Electron apps (desktop apps built with web technology), Android apps, .NET programs, websites, network captures and many specialist formats. Source: [morluto/rea](https://github.com/morluto/rea), npm package `rea-agents`, MIT licence.

## Should you install it?

**Not as an everyday tool.** Only for a specific project that needs it, and remove it afterwards.

Why it's useful if you're building your own CRM or internal tools:
- **Integrating with software that has no API.** For example, a licensed desktop app your business runs on, where you need to understand how it stores or exports data.
- **Debugging a vendor's app or SDK** that misbehaves in your own setup.
- **Checking a downloaded tool** to see what it does before you trust it.

What it won't do well:
- **Copy a SaaS product's features.** Products like GoHighLevel run their real logic on their servers, which REA can't see. For a website it adds little beyond what your agent can already do in a browser. The right way to borrow a competitor's feature is to copy how it behaves and build your own version.

## Rules before you use it

1. **Only on software you own or are allowed to analyse.** Most software licences and SaaS terms of service forbid reverse engineering. REA's own disclaimer says it won't help copy proprietary code, bypass licence checks or access controls. If in doubt, check the licence or ask the vendor.
2. **Install per project, not globally.** Its setup adds a large set of tools and instructions to your agent configuration. Loaded everywhere, that costs context in every session and invites your agent to use it when it shouldn't.
3. **Pin the version.** It changes very quickly and suggests always running the latest. Pick a version, use it for the project, and note it.
4. **Keep it contained.** It drives other installed programs and can install Hopper for you. Approve each change it proposes.
5. **Remove it when the project is done.**

## Setup for one project

```bash
cd ~/code/your-project
npx rea-agents@6.8.0 setup        # choose your agent, review the proposed changes, approve
```

Setup adds REA's tool server and its workflow instructions to your agent's configuration, and backs up the existing configuration. Restart your agent. Native-app analysis also needs one of Ghidra, Hopper, IDA or Kuna installed.

Without changing your agent at all, you can also run single analyses from the terminal, for example on an Electron app you're allowed to inspect:

```bash
npx -y rea-agents@6.8.0 analyze-javascript-application /absolute/path/to/app --json
```

## Removing it

Run the setup again and remove REA from your agent, or restore the configuration backup setup made. Then confirm your agent's tool list no longer shows REA. Full instructions: [REA installation docs](https://github.com/morluto/rea/blob/main/docs/getting-started/installation.md).
