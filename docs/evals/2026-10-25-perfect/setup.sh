#!/bin/sh
# usage: setup.sh <sl-root>
# Rebuilds the isolated eval workspace used by run3.sh / matrix*.sh: the two base repositories
# (todo CLI, kv CLI), pstack and REA config for Claude, an isolated CODEX_HOME (auth, pstack, the
# pstack AGENTS.md block, REA), a second CODEX_HOME with the hook-free plugin installed, and the
# plugin marketplace snapshot from this checkout's HEAD.
set -e
SL=$1; REPO=$(cd "$(dirname "$0")/../../.." && pwd)
mkdir -p "$SL/skill"

# --- base: todo CLI (Python), Spec Kit claude integration -------------------------------------
B=$SL/base; rm -rf "$B"; mkdir -p "$B/tests"
cat > "$B/todo.py" <<'EOF'
#!/usr/bin/env python3
"""Tiny todo CLI. Store: JSON file at $TODO_FILE (default ./todo.json)."""
import json, os, sys

STORE = os.environ.get("TODO_FILE", "todo.json")


def load():
    if not os.path.exists(STORE):
        return {"next_id": 1, "items": []}
    with open(STORE) as f:
        return json.load(f)


def save(data):
    with open(STORE, "w") as f:
        json.dump(data, f, indent=2)


def main(argv):
    if not argv:
        print("usage: todo add <text> | list | done <id>", file=sys.stderr)
        return 2
    cmd, args = argv[0], argv[1:]
    data = load()
    if cmd == "add" and args:
        item = {"id": data["next_id"], "text": " ".join(args), "done": False}
        data["items"].append(item)
        data["next_id"] += 1
        save(data)
        print(f"added {item['id']}")
        return 0
    if cmd == "list":
        for it in data["items"]:
            if not it["done"]:
                print(f"{it['id']}. {it['text']}")
        return 0
    if cmd == "done" and len(args) == 1:
        for it in data["items"]:
            if str(it["id"]) == args[0]:
                it["done"] = True
                save(data)
                print(f"done {it['id']}")
                return 0
        print(f"no item {args[0]}", file=sys.stderr)
        return 1
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
EOF
cat > "$B/tests/test_todo.py" <<'EOF'
import os, subprocess, sys, tempfile, unittest
from pathlib import Path

TODO = Path(__file__).resolve().parent.parent / "todo.py"


class TodoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, TODO_FILE=os.path.join(self.tmp.name, "t.json"))

    def tearDown(self):
        self.tmp.cleanup()

    def run_todo(self, *args):
        return subprocess.run([sys.executable, str(TODO), *args], capture_output=True, text=True, env=self.env)

    def test_add_list_done(self):
        self.assertEqual(self.run_todo("add", "milk").returncode, 0)
        self.run_todo("add", "eggs")
        self.assertIn("1. milk", self.run_todo("list").stdout)
        self.assertEqual(self.run_todo("done", "1").returncode, 0)
        self.assertNotIn("milk", self.run_todo("list").stdout)

    def test_done_unknown(self):
        r = self.run_todo("done", "99")
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(r.stderr)


if __name__ == "__main__":
    unittest.main()
EOF
printf 'todo.json\n__pycache__/\n' > "$B/.gitignore"

# --- base2: kv CLI (Node, multi-module) --------------------------------------------------------
K=$SL/base2; rm -rf "$K"; mkdir -p "$K/src" "$K/test"
cat > "$K/package.json" <<'EOF'
{ "name": "kv", "version": "0.1.0", "type": "module", "bin": { "kv": "src/cli.js" }, "scripts": { "test": "node --test" } }
EOF
cat > "$K/src/store.js" <<'EOF'
import { existsSync, readFileSync, writeFileSync } from "node:fs";

export const storePath = () => process.env.KV_FILE || "kv.json";

export function load() {
  const p = storePath();
  return existsSync(p) ? JSON.parse(readFileSync(p, "utf8")) : { entries: {} };
}

export function save(data) {
  writeFileSync(storePath(), JSON.stringify(data, null, 2));
}
EOF
cat > "$K/src/commands.js" <<'EOF'
import { load, save } from "./store.js";

export function set(key, value) {
  const data = load();
  data.entries[key] = { value };
  save(data);
}

export function get(key) {
  const entry = load().entries[key];
  return entry ? entry.value : undefined;
}

export function del(key) {
  const data = load();
  if (!(key in data.entries)) return false;
  delete data.entries[key];
  save(data);
  return true;
}

export function list() {
  return Object.keys(load().entries).sort();
}
EOF
cat > "$K/src/cli.js" <<'EOF'
#!/usr/bin/env node
import { set, get, del, list } from "./commands.js";

const [cmd, ...args] = process.argv.slice(2);
const fail = (msg, code = 1) => { process.stderr.write(msg + "\n"); process.exit(code); };

switch (cmd) {
  case "set":
    if (args.length !== 2) fail("usage: kv set <key> <value>", 2);
    set(args[0], args[1]);
    break;
  case "get": {
    const v = get(args[0]);
    if (v === undefined) fail(`no key ${args[0]}`);
    console.log(v);
    break;
  }
  case "del":
    if (!del(args[0])) fail(`no key ${args[0]}`);
    break;
  case "list":
    for (const k of list()) console.log(k);
    break;
  default:
    fail("usage: kv set|get|del|list", 2);
}
EOF
cat > "$K/test/cli.test.js" <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const run = (env, ...args) => spawnSync(process.execPath, ["src/cli.js", ...args], { env: { ...process.env, ...env }, encoding: "utf8" });

test("set, get, list, del", () => {
  const env = { KV_FILE: join(mkdtempSync(join(tmpdir(), "kv-")), "s.json") };
  assert.equal(run(env, "set", "a", "1").status, 0);
  assert.equal(run(env, "get", "a").stdout.trim(), "1");
  assert.equal(run(env, "list").stdout.trim(), "a");
  assert.equal(run(env, "del", "a").status, 0);
  assert.notEqual(run(env, "get", "a").status, 0);
});
EOF
printf 'kv.json\nnode_modules/\n' > "$K/.gitignore"

for d in "$B" "$K"; do
  (cd "$d" && git init -q -b main && specify init --here --force --non-interactive --integration claude < /dev/null > /dev/null 2>&1 \
     && git add -A && git -c user.name=eval -c user.email=eval@example.invalid commit -qm "base")
done

# --- Claude: pstack plugin copy and REA MCP config ---------------------------------------------
P=$(ls -d "$HOME"/.claude/plugins/cache/pstack-claude/pstack/* | sort -V | tail -1)
rm -rf "$SL/pstack"; cp -R "$P" "$SL/pstack"
printf '{"mcpServers":{"rea":{"command":"npx","args":["-y","rea-agents@6.7.0","mcp"]}}}\n' > "$SL/rea-mcp.json"

# --- Codex: isolated home (auth, pstack, the pstack AGENTS.md block, REA) ----------------------
CH=$SL/codex-home; rm -rf "$CH"; mkdir -p "$CH/plugins/cache/pstack-claude/pstack"
cp "$HOME/.codex/auth.json" "$CH/"
CP=$(ls -d "$HOME"/.codex/plugins/cache/pstack-claude/pstack/* | sort -V | tail -1)
cp -R "$CP" "$CH/plugins/cache/pstack-claude/pstack/"
sed -n '/pstack-models:start/,/pstack-mandate:end/p' "$HOME/.codex/AGENTS.md" > "$CH/AGENTS.md"
cat > "$CH/config.toml" <<'EOF'
model = "gpt-6-luna"
model_reasoning_effort = "medium"

[marketplaces.pstack-claude]
source_type = "git"
source = "https://github.com/michael-denyer/pstack-claude.git"

[plugins."pstack@pstack-claude"]
enabled = true

[features.multi_agent_v2]
enabled = true
max_concurrent_threads_per_session = 8
expose_spawn_agent_model_overrides = true
tool_namespace = "agents"

[mcp_servers.rea]
command = "npx"
args = [ "-y", "rea-agents@6.7.0", "mcp" ]
startup_timeout_sec = 30
EOF

# --- plugin marketplace snapshot and a Codex home with the hook-free plugin --------------------
rm -rf "$SL/market"; mkdir -p "$SL/market"
(cd "$REPO" && git archive HEAD .claude-plugin plugins) | tar -x -C "$SL/market"
rm -rf "$SL/codex-home-pfree" "$SL/fh-setup"; cp -R "$CH" "$SL/codex-home-pfree"; mkdir -p "$SL/fh-setup"
HOME="$SL/fh-setup" CODEX_HOME="$SL/codex-home-pfree" codex plugin marketplace add "$SL/market" > /dev/null
HOME="$SL/fh-setup" CODEX_HOME="$SL/codex-home-pfree" codex plugin add agentic-sdd@agentic-sdd > /dev/null
echo "eval workspace ready at $SL"
