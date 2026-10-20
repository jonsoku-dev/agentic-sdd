#!/usr/bin/env node
// npx agentic-sdd [setup] [--dry-run|--yes] [--project DIR]
// npx agentic-sdd check-deps | deps | probe [--host H] [--project DIR] | uninstall [...]
//
// Copies this package's files into ~/.agents/skills/agentic-sdd (the path the
// hosts load) unless that path is already a git checkout, then runs install.sh
// there. Everything else (detection, plan, prompt, apply, verify) is install.sh.
"use strict";
const { spawnSync, execFileSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const PKG = path.resolve(__dirname, "..");
const HOME = process.env.AGENTIC_SDD_HOME || os.homedir();
const TARGET = path.join(HOME, ".agents", "skills", "agentic-sdd");
const VERSION = require(path.join(PKG, "package.json")).version;

const USAGE = `agentic-sdd ${VERSION}

  npx agentic-sdd                 detect this machine, show the plan, ask once, install and configure every host found
  npx agentic-sdd --dry-run       detect and plan only
  npx agentic-sdd --yes           no prompt
  npx agentic-sdd --project DIR   also install the project playbook and Cursor rule into DIR
  npx agentic-sdd check-deps      installed vs latest for Spec Kit, pstack, REA pins, host CLIs
  npx agentic-sdd deps            update what can be updated unattended, then relink
  npx agentic-sdd probe [--host claude|codex|cursor|grok] [--project DIR]
  npx agentic-sdd uninstall [--project DIR] [--purge-deps --yes]
  npx agentic-sdd where           print the skill directory the hosts load

Requires python3 and git on PATH. Docs: https://github.com/jonsoku-dev/agentic-sdd
`;

function have(cmd) {
  const r = spawnSync(process.platform === "win32" ? "where" : "which", [cmd], { stdio: "ignore" });
  return r.status === 0;
}

function isGitCheckout(dir) {
  try {
    execFileSync("git", ["-C", dir, "rev-parse", "--is-inside-work-tree"], { stdio: "ignore" });
    return fs.existsSync(path.join(dir, ".git"));
  } catch {
    return false;
  }
}

function sync() {
  const real = fs.existsSync(TARGET) ? fs.realpathSync(TARGET) : TARGET;
  if (fs.existsSync(real) && isGitCheckout(real)) {
    console.log(`using existing git checkout at ${real} (git pull there to update)`);
    return real;
  }
  if (path.resolve(real) === path.resolve(PKG)) {
    return real;
  }
  fs.mkdirSync(path.dirname(TARGET), { recursive: true });
  const stamp = path.join(real, ".npm-version");
  if (fs.existsSync(stamp) && fs.readFileSync(stamp, "utf8").trim() === VERSION) {
    return real;
  }
  if (fs.existsSync(real)) {
    fs.rmSync(real, { recursive: true, force: true });
  }
  // mirror the npm tarball: never carry a dev checkout's .git, tests, workflows, or eval records
  const skip = /[\\/](node_modules|\.git|\.github|tests|docs[\\/]evals)([\\/]|$)/;
  fs.cpSync(PKG, real, { recursive: true, filter: (src) => !skip.test(src) });
  fs.writeFileSync(stamp, VERSION + "\n");
  console.log(`installed agentic-sdd ${VERSION} into ${real}`);
  return real;
}

function main(argv) {
  if (argv.includes("-h") || argv.includes("--help")) {
    process.stdout.write(USAGE);
    return 0;
  }
  if (argv[0] === "--version" || argv[0] === "-v") {
    console.log(VERSION);
    return 0;
  }
  for (const tool of ["python3", "git", "bash"]) {
    if (!have(tool)) {
      console.error(`agentic-sdd needs ${tool} on PATH`);
      return 2;
    }
  }
  const dir = sync();
  const cmd = argv[0] && !argv[0].startsWith("-") ? argv.shift() : "setup";
  if (cmd === "where") {
    console.log(dir);
    return 0;
  }
  const map = {
    setup: () => ["bash", [path.join(dir, "install.sh"), ...argv]],
    "check-deps": () => ["bash", [path.join(dir, "install.sh"), "--check-deps"]],
    deps: () => ["bash", [path.join(dir, "install.sh"), "--deps", ...argv]],
    uninstall: () => ["bash", [path.join(dir, "install.sh"), "--uninstall", ...argv]],
    probe: () => ["python3", [path.join(dir, "scripts", "harness_probe.py"), ...(argv.length ? argv : ["--host", "auto", "--project", process.cwd()])]],
  };
  if (!map[cmd]) {
    console.error(`unknown command: ${cmd}\n`);
    process.stdout.write(USAGE);
    return 2;
  }
  const [bin, args] = map[cmd]();
  const r = spawnSync(bin, args, { stdio: "inherit", cwd: dir, env: { ...process.env, AGENTIC_SDD_FROM_NPX: "1" } });
  return r.status == null ? 1 : r.status;
}

process.exit(main(process.argv.slice(2)));
