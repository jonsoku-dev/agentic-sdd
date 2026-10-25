---
description: >
  Dual-audience (human + agent) guide for running agentic-sdd with pstack on
  Claude Code, Codex, and Cursor. Split into greenfield (new Spec Kit project)
  and brownfield (existing codebase / existing Spec Kit). Process authority
  stays Spec Kit; pstack is execution style inside phases.
---

# Host guide: greenfield & brownfield (Claude · Codex · Cursor)

**Readers:** humans setting up or supervising a run; agents executing
`/agentic-sdd` (or `$agentic-sdd`). Agents treat this as procedure, not
permission to expand scope or install tools beyond what `SKILL.md` already
authorizes.

**Related (do not duplicate here):**

| File | Role |
|------|------|
| [`SKILL.md`](../SKILL.md) | Entrypoint, autonomy, hard boundaries |
| [`pstack-integration.md`](pstack-integration.md) | Phase → pstack obligation map |
| [`phase-contract.md`](phase-contract.md) | What each Spec Kit phase may write |
| [`cursor-continuation.md`](cursor-continuation.md) | Cursor `sdd-continue` stop-hook |
| [`rea-closeout.md`](rea-closeout.md) | Mandatory post-converge REA |
| `setup-speckit-multi-agent` skill | Init / inspect / activate / multi-host setup |

---

## 1. Mental model (both field types)

```text
Final Goal          ← what the human asked for (unchanged until delivered)
agentic-sdd         ← owns phase order, continuity, recovery, REA
Spec Kit            ← owns artifacts (.specify/, specs|/.specify/specs/, constitution)
pstack              ← owns how a batch is designed/reviewed/verified inside a phase
Host (Claude/Codex/Cursor) ← invocation surface only; never a second spec tree
```

| Layer | Greenfield | Brownfield |
|-------|------------|------------|
| Spec Kit | Create `.specify/` + first feature | Reuse or add Spec Kit **without** rewriting the whole app |
| First feature | Product slice from Final Goal | **Bounded change** only (one capability / bug / seam) |
| Architecture | Invented in `plan`, constrained by constitution | **Reuse** existing layout, tests, patterns |
| pstack | Full map from day one | Prefer `/how` + `/why` before `/architect`; smaller diffs |
| Risk | Wrong shape early | Blast radius + regressions |

**Invariant:** one checkout = one writer. One canonical spec root
(`specs/` or legacy `.specify/specs/`). Never fork specs per agent.

---

## 2. One-time machine setup (humans)

Do this once per machine. Agents do **not** auto-install pstack as part of SDD
(unless the user explicitly asked to set up pstack).

### 2.1 agentic-sdd (all hosts)

Canonical path (already symlinked on this machine):

```text
~/.agents/skills/agentic-sdd/
  → ~/.claude/skills/agentic-sdd
  → ~/.codex/skills/agentic-sdd
  → ~/.cursor/skills/agentic-sdd
```

### 2.2 pstack by host

| Host | Install (prefer user / global scope) | Invoke |
|------|--------------------------------------|--------|
| **Cursor** | `/add-plugin pstack` or marketplace install | `/poteto-mode`, `/architect`, `/arena`, … |
| **Claude Code** | `claude plugin install pstack --marketplace michael-denyer/pstack-claude --scope user` | `/pstack:architect`, `/pstack:interrogate`, … |
| **Codex** | Same marketplace/port via Codex plugin commands (see port README) | `pstack:…` / `$…` per port docs |

Then once per host: Cursor `/setup-pstack`; Claude `/pstack:setup-pstack`.

### 2.3 Spec Kit CLI + multi-agent helper

- `specify` CLI available on PATH.
- For multi-host projects: `setup-speckit-multi-agent` (`scripts/speckit_multi_agent.py setup|inspect|activate|sdd`).

### 2.4 Verify before first real run

```bash
# Claude global pstack
claude plugin list | grep pstack
# expect pstack@pstack-claude (user)

# Spec Kit
specify --version
test -d ~/.agents/skills/agentic-sdd && echo agentic-sdd ok
```

---

## 3. GREENFIELD — new product / empty repo

**Definition:** no meaningful application code yet, or a brand-new directory.
You are allowed to choose stack and layout subject to constitution + Final Goal.

### 3.1 Human checklist (greenfield)

1. Create an empty directory (prefer `~/Projects/<name>`).
2. Init Spec Kit (pick the host you will primarily use, then add others):

```bash
cd ~/Projects
specify init my-app --non-interactive --integration claude
# add peers as needed:
cd my-app
specify integration install cursor-agent
specify integration install codex   # if available in your Spec Kit build
# multi-agent helper (optional but recommended):
# setup-speckit-multi-agent setup --project "$PWD" --default claude
```

3. Confirm `.specify/`, constitution template, and integration status:

```bash
specify integration status --json
```

4. Open the project in the chosen host and start:

| Host | What to type |
|------|----------------|
| Cursor | `/agentic-sdd` then Final Goal + “greenfield; full Spec Kit” |
| Claude | `/agentic-sdd` (or attach skill) + same Final Goal |
| Codex | `$agentic-sdd` + Final Goal |

5. Optional: `/setup-pstack` or `/pstack:setup-pstack` if not done machine-wide.
6. Walk away. Approve shell/MCP cards only. Expect `progress.md` updates.
7. Finish criteria: feature REA `pass` or `not-applicable`, Final Goal closed or next numbered feature started without a quiz.

### 3.2 Agent procedure (greenfield)

Mode: **delivery**. Full-autonomy grant inside Final Goal.

```text
1. Confirm greenfield: little/no app code; .specify/ present or setup skill required.
2. If .specify/ missing → stop mutating; tell human to run setup-speckit-multi-agent
   / specify init (do not invent a second process).
3. Pin Final Goal + first acceptance slice in feature artifacts.
4. Run Spec Kit in order (no phase quiz):
   constitution (if empty) → specify → [clarify] → plan → [checklist] → tasks
   → implement → [analyze] → converge → REA → next feature while Goal remains
5. Inside each phase, apply pstack map (pstack-integration.md):
   - plan: O-architect / O-arena
   - implement: O-poteto (+ O-swarm / O-arena when warranted)
   - converge: O-interrogate + multi-perspective-review
6. Flush progress.md every meaningful stage.
   Cursor: maintain <!-- sdd-continue: ... --> (cursor-continuation.md).
7. Do not ask “should I go to plan?” — advance automatically.
8. Hard stop only for destructive / secrets / scope / missing Spec Kit project.
```

### 3.3 Greenfield phase expectations

| Phase | Produce | pstack emphasis | Do not |
|-------|---------|-----------------|--------|
| constitution | Project principles | unslop on prose | Invent unrelated product scope |
| specify | Observable AC, non-goals | sharpen / in-your-own-words if fuzzy | Skip AC |
| plan | Smallest stack + verification contract | architect; arena if 2+ shapes | Over-scaffold frameworks |
| tasks | Ordered Txxx with checks | sequence-verifiable-units | Tasks without AC links |
| implement | Code meeting AC | poteto non-negotiables; prove-it-works | Free-standing poteto playbook replacing Spec Kit |
| converge | Gap list or clean | interrogate | Relax AC to go green |
| REA | Disposition recorded | (not pstack) | Mark finished without REA |

### 3.4 Greenfield prompts (copy/paste)

**Cursor / Claude:**

```text
/agentic-sdd
Final Goal: <one sentence product outcome>
Field: greenfield
Hosts available: Claude + Cursor (shared .specify/)
Constraints: <stack prefs if any; else choose and record>
Done when: <observable AC> + REA pass/not-applicable
Run unattended through Spec Kit phases. No phase quiz.
```

**Codex:**

```text
$agentic-sdd
Final Goal: ...
Field: greenfield
...
```

### 3.5 Greenfield anti-patterns

- Starting `/pstack:poteto-mode` as the **only** process (skips Spec Kit artifacts).
- Generating a huge monorepo before one verified vertical slice.
- Asking the human which phase is next.
- Creating agent-specific `specs-claude/` trees.

---

## 4. BROWNFIELD — existing codebase

**Definition:** real application code, tests, or deployables exist. Spec Kit may
be absent, partial, or already active. Default stance: **smallest change that
meets the Final Goal**; do not retro-specify the entire system.

### 4.1 Classify the brownfield case

| Case | Signal | First move |
|------|--------|------------|
| **B1** Spec Kit already active | `.specify/` + feature pointer | `inspect` / `sdd` → continue owning phase |
| **B2** Code yes, Spec Kit no | App exists; no `.specify/` | Human-authorized `specify init --here` / `setup --init-existing` on **clean** baseline |
| **B3** Spec Kit stale / wrong feature | Pointer ≠ branch or tasks empty vs dirty tree | Reconcile pointer before edits |
| **B4** Bug / regression | Broken existing behavior | Bug workflow if installed; else bounded feature |
| **B5** Cross-cutting refactor | Large blast radius | `figure-it-out` + show-me-your-work; still Spec Kit features |

Agents: for **B2**, do **not** run `--init-existing` / `--force` without explicit
user authorization. Point to `setup-speckit-multi-agent`.

### 4.2 Human checklist (brownfield)

#### B1 — Spec Kit already present

```bash
cd /path/to/repo
# optional multi-agent health:
# setup-speckit-multi-agent inspect --project "$PWD" --full
specify integration status --json
# activate the host you will write with:
# setup-speckit-multi-agent activate claude|cursor|codex --project "$PWD"
```

Then in that host:

```text
/agentic-sdd
Final Goal: <bounded outcome>
Field: brownfield
Continue active feature if aligned; else specify next numbered feature for this Goal.
Do not rewrite unrelated subsystems.
```

#### B2 — Add Spec Kit to an existing repo

1. Clean Git working tree (or explicitly accept dirty ownership).
2. Review what `specify init --here` / multi-agent `--init-existing` will write.
3. Authorize setup once:

```bash
# Example — prefer the project's established helper:
# setup-speckit-multi-agent setup --project "$PWD" --default cursor --init-existing
# Or:
specify init --here --force --non-interactive --integration cursor-agent
specify integration install claude
```

4. Commit the Spec Kit scaffolding as its own commit when policy allows.
5. Start `/agentic-sdd` with a **narrow** first feature (one seam), not “spec the app”.

#### B3 — Reconcile before coding

- Align `.specify/feature.json` (or equivalent) with the feature directory and
  branch policy.
- List dirty paths; one writer owns them.
- Only then continue implement / specify.

### 4.3 Agent procedure (brownfield)

```text
1. Resolve nearest .specify/; record revision + dirty owners.
2. Classify B1–B5. If B2 without authorization → blocked/missing setup, ask once.
3. Pin Final Goal; derive a BOUNDARY: admitted paths, non-goals, required checks
   from repo policy + existing tests.
4. Orient with evidence before design:
   - pstack O-sharpen if Goal text is fuzzy
   - Cursor /how|/why or Claude /pstack:how|/pstack:why on the touched subsystem
5. specify only the requested change (spec-kit-alignment: existing code).
6. plan must reuse architecture; call O-architect only when crossing a new boundary.
7. tasks: small verifiable units; prefer repo test commands already present.
8. implement: poteto non-negotiables; O-blast before risky merges; O-tdd when cheap.
9. converge + O-interrogate; never lower AC to match a defect.
10. REA closeout; then next numbered feature only for remaining Goal work.
```

### 4.4 Brownfield phase expectations

| Phase | Brownfield bias | pstack emphasis |
|-------|-----------------|-----------------|
| specify | Bound the change; link existing behaviors as context, not full rewrite | how / why first |
| plan | Reuse modules, test harness, CI | architect only if new seam; arena if two migrations compete |
| tasks | Map to existing packages/packages owners | sequence-verifiable-units |
| implement | Minimal diff; migrate callers then delete | poteto; blast-radius; correct on repeated mistakes |
| converge | Regressions + AC | interrogate; multi-perspective |
| bug path | assess → fix → test | tdd when local oracle exists |

### 4.5 Brownfield prompts (copy/paste)

**Continue existing Spec Kit feature:**

```text
/agentic-sdd
Final Goal: <same Goal as progress.md if present>
Field: brownfield (B1)
Read progress.md + active feature; continue owning phase.
No phase quiz. Preserve dirty ownership. Shared specs only.
```

**New bounded feature on existing app:**

```text
/agentic-sdd
Final Goal: <bounded user-visible outcome>
Field: brownfield
Admitted paths: <dirs/packages>
Non-goals: <do not refactor X>
Required checks: <existing test/lint commands>
Start specify for the next numbered feature. Reuse architecture.
```

**Bug:**

```text
/agentic-sdd
Mode: repair
Field: brownfield
Symptom: <repro>
Use Spec Kit bug workflow if installed; else bounded fix feature.
Verify with the failing case before and after.
```

### 4.6 Brownfield anti-patterns

- “While we’re here” refactors outside admitted paths.
- Re-specifying the entire legacy system as feature `001`.
- Ignoring existing tests and inventing a parallel harness by default.
- Claiming `/pstack:interrogate` consensus when pstack is not installed
  (use native multi-leaf review + record the limit).
- Switching hosts mid-feature without flushing `progress.md` and dirty owners.

---

## 5. Per-host cheat sheet

### 5.1 Cursor

| Item | Value |
|------|--------|
| Skill | `/agentic-sdd` (global `~/.cursor/skills/agentic-sdd`) |
| Spec Kit | `/speckit-*` or project `.cursor/skills/speckit-*` |
| pstack | Official marketplace `pstack` |
| Continuity | `progress.md` `sdd-continue` + stop-hook ([cursor-continuation.md](cursor-continuation.md)) |
| Implement leaves | Inline by default; `poteto-agent` when a single-loop trigger justifies a Task |
| Model sheet | `~/.cursor/rules/pstack-models.mdc` after `/setup-pstack` |

**Cursor-specific:** do not end a turn on a status report while Goal is open.
Keep the critical path in-thread; hook is backup.

### 5.2 Claude Code

| Item | Value |
|------|--------|
| Skill | `/agentic-sdd` or auto from `~/.claude/skills/agentic-sdd` |
| Spec Kit | `/speckit.*` / project `.claude/skills` |
| pstack | User-scope `pstack@pstack-claude` → `/pstack:<skill>` |
| Continuity | `progress.md` + Claude session loop (no Cursor stop-hook) |
| Compact | Flush `progress.md` before `/compact` |
| Model sheet | After `/pstack:setup-pstack` (port-specific path) |

**Detect pstack:**

```bash
claude plugin list | grep pstack
# or in-session: /plugin list
```

If missing: obligations-only; record `pstack: unavailable|claude` once; continue Spec Kit.

### 5.3 Codex

| Item | Value |
|------|--------|
| Skill | `$agentic-sdd` (`agents/openai.yaml`) |
| Spec Kit | `$speckit-*` |
| pstack | Codex plugin from same ports when installed |
| Continuity | File handoff in `progress.md` / feature artifacts |
| Activation | `setup-speckit-multi-agent activate codex --project PATH` before write |

Prefer `$speckit-*` over free-form chat for phase ownership.

### 5.4 Switching hosts mid-feature

1. Flush `progress.md` handoff block (see phase-contract).
2. Capture dirty path owners.
3. `activate` the target host when using the multi-agent helper.
4. Receiving agent verifies snapshot before writing.
5. Never copy specs into a host-only directory.

---

## 6. Shared runtime rules (agents)

1. **Spec Kit order wins** over any pstack playbook.
2. **No free-standing poteto-mode** that replaces phases — apply non-negotiables
   *inside* implement/fix batches (`/poteto-mode` or `/pstack:poteto-mode` skill text).
3. **Breadcrumb** in `progress.md`:

```text
pstack: O-architect|cursor|/architect → plan.md updated
pstack: O-poteto|claude|/pstack:poteto-mode → T012 verified
pstack: unavailable|codex → obligations-only
```

4. **Autonomy:** no phase quiz; reversible forks → recorded default.
5. **Hard boundaries:** destructive, secrets, scope beyond Final Goal, Spec Kit
   extension installs — confirm once / `blocked`.
6. **REA** after clean converge before feature close ([rea-closeout.md](rea-closeout.md)).
7. **Missing pstack ≠ failed SDD.** Continue with obligations.

---

## 7. Troubleshooting

| Symptom | Check | Fix |
|---------|-------|-----|
| Agent asks which phase next | Autonomy grant ignored | Re-invoke `/agentic-sdd`; cite this guide §6 |
| Claude has no `/pstack:*` | User-scope plugin missing | §2.2 Claude install |
| Cursor stops and never resumes | `sdd-continue` missing/stuck | Write machine line; see cursor-continuation |
| Two agents editing same tree | No activate / dirty owners | One writer; activate + flush |
| Brownfield “rewrite everything” | Wrong field type | Re-pin admitted paths; new numbered feature for extras |
| Init on dirty brownfield | `--init-existing` / `--force` | Clean baseline or explicit human authorize |
| Interrogate “consensus” alone | Single model | Record limit; still need Spec Kit evidence |
| Feature CLOSED but Goal open | Normal | specify next numbered feature; no quiz |

---

## 8. Quick decision tree

```text
Is there an application already?
├─ No  → GREENFIELD (§3)
│         Init Spec Kit → /agentic-sdd → full phase chain + pstack map
└─ Yes → BROWNFIELD (§4)
          ├─ .specify/ ok? → B1 continue
          ├─ no .specify/? → B2 human-authorized init, then narrow feature
          ├─ pointer conflict? → B3 reconcile
          └─ broken behavior? → B4 bug workflow
```

Host pick (writer for this session):

```text
Primary daily driver?
├─ Cursor → official pstack + sdd-continue
├─ Claude → user-scope pstack-claude + /pstack:*
└─ Codex  → $agentic-sdd + $speckit-* (+ pstack port if installed)
```

---

## 9. Definition of done

| Audience | Done means |
|----------|------------|
| **Human** | Final Goal observable; can delete the chat and resume from `progress.md` + feature artifacts on any host |
| **Agent** | Spec Kit evidence current; REA disposition `pass` or `not-applicable`; `sdd-continue` / progress status `delivered` (or next feature already started); no open blocking acceptance |

---

## 10. Minimal reference cards

### Greenfield (one screen)

1. `specify init` (+ peer integrations)  
2. `/agentic-sdd` + Final Goal + field greenfield  
3. Phases auto-advance; pstack inside phases  
4. REA → next feature or delivered  

### Brownfield (one screen)

1. Classify B1–B5; never silent whole-app rewrite  
2. Orient (`how`/`why`) → specify **bound** change  
3. Reuse architecture + existing checks  
4. Implement small; blast-radius; interrogate; REA  

### pstack invoke

| Need | Cursor | Claude |
|------|--------|--------|
| Design before code | `/architect` | `/pstack:architect` |
| Bakeoff | `/arena` | `/pstack:arena` |
| Parallel slices | `/swarm` | `/pstack:swarm` |
| Adversarial review | `/interrogate` | `/pstack:interrogate` |
| Batch style | poteto non-negotiables | same via `/pstack:poteto-mode` skill text |
