#!/usr/bin/env python3
"""Summarize Tier-1 routing runs from the hosts' headless JSON output.

Judged from events and final text, never from a self-report line we asked for.
For each run: tools actually called (name + skill/agent arg when present), the
final assistant text, and which routing tokens that text names.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "tier1"
TOKENS = {
    "agentic-sdd": r"agentic[- ]sdd",
    "poteto-mode": r"poteto[- ]mode",
    "feature-pb": r"feature playbook|playbook.*feature",
    "bug-fix-pb": r"bug[- ]fix",
    "investigation": r"investigation",
    "how": r"\bhow\b.*skill|`how`|/how|pstack:how",
    "why": r"`why`|/why|pstack:why|\bwhy skill",
    "architect": r"architect",
    "interrogate": r"interrogate",
    "sharpen": r"sharpen",
    "specify": r"\bspecify\b|speckit",
    "converge": r"converge",
    "rea": r"\brea\b|capture_process",
    "poteto-agent": r"poteto[- ]agent",
    "none": r"\bnone\b",
}


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def load(path: Path):
    text = path.read_text(errors="replace")
    objs = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            objs.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    if not objs:
        try:
            objs = [json.loads(text)]
        except json.JSONDecodeError:
            pass
    return objs


def tool_calls(objs):
    calls = []
    for d in walk(objs):
        # Claude: content blocks {type: tool_use, name, input}; Cursor/Grok/Codex: various
        if d.get("type") == "tool_use" and "name" in d:
            arg = d.get("input") or {}
            calls.append((d["name"], arg.get("skill") or arg.get("subagent_type") or arg.get("command") or ""))
        elif d.get("type") in ("tool_call", "function_call") and ("name" in d or "tool" in d):
            name = d.get("name") or d.get("tool")
            arg = d.get("arguments") or d.get("input") or d.get("args") or {}
            if isinstance(arg, str):
                try:
                    arg = json.loads(arg)
                except json.JSONDecodeError:
                    arg = {"raw": arg[:60]}
            calls.append((name, (arg.get("skill") or arg.get("subagent_type") or arg.get("command") or arg.get("raw") or "") if isinstance(arg, dict) else ""))
        elif d.get("item", {}) and isinstance(d.get("item"), dict) and d["item"].get("type") in ("command_execution", "mcp_tool_call", "collab_tool_call"):
            it = d["item"]
            calls.append((it.get("type"), (it.get("command") or it.get("tool") or "")[:60]))
        elif d.get("type") == "tool_call" and d.get("subtype") == "started" and isinstance(d.get("tool_call"), dict):
            # Cursor Agent CLI: {"tool_call": {"<kind>ToolCall": {"args": {...}}}}
            for kind, body in d["tool_call"].items():
                if not kind.endswith("ToolCall"):
                    continue
                args = (body or {}).get("args") or {}
                calls.append((kind.removesuffix("ToolCall"), str(args.get("path") or args.get("command") or args.get("toolName") or args.get("pattern") or "")[:60]))
    return calls


SKILL_FILE = re.compile(r"(?:skills|playbooks|references)/([\w.-]+(?:/[\w.-]+)*\.md)")


def skill_reads(calls):
    seen = []
    for _, arg in calls:
        for m in SKILL_FILE.finditer(arg):
            name = m.group(1)
            if name not in seen:
                seen.append(name)
    return seen


def final_text(objs, host):
    texts = []
    for d in objs:
        if host == "claude" and d.get("type") == "result":
            texts.append(d.get("result") or "")
        elif host == "cursor" and d.get("type") == "result":
            texts.append(d.get("result") or d.get("text") or "")
        elif host == "codex" and d.get("type") == "item.completed" and d.get("item", {}).get("type") == "agent_message":
            texts.append(d["item"].get("text") or "")
        elif host == "grok":
            for k in ("result", "text", "content", "output"):
                if isinstance(d.get(k), str):
                    texts.append(d[k])
    if not texts:  # fall back to every assistant text block
        for d in walk(objs):
            if d.get("type") == "text" and isinstance(d.get("text"), str):
                texts.append(d["text"])
    return "\n".join(texts).strip()


def main():
    rows = []
    for path in sorted(ROOT.glob("*.jsonl")):
        host, case = path.stem.split("-", 1)
        objs = load(path)
        calls = tool_calls(objs)
        text = final_text(objs, host)
        named = [k for k, rx in TOKENS.items() if re.search(rx, text, re.I)]
        rows.append({"host": host, "case": case, "events": len(objs), "tool_calls": calls, "named": named, "text": text})
    out = ["| host | case | tool calls | skill/playbook files it opened | routing tokens named in final text |", "|---|---|---|---|---|"]
    for r in rows:
        kinds = {}
        for n, _ in r["tool_calls"]:
            kinds[n] = kinds.get(n, 0) + 1
        calls = ", ".join(f"{n}×{c}" for n, c in kinds.items()) or "none"
        reads = ", ".join(skill_reads(r["tool_calls"])[:6]) or "-"
        out.append(f"| {r['host']} | {r['case']} | {calls} | {reads} | {', '.join(r['named']) or '-'} |")
    print("\n".join(out))
    if "--text" in sys.argv:
        for r in rows:
            print(f"\n## {r['host']} {r['case']}\n{r['text'][:1500]}")


if __name__ == "__main__":
    main()
