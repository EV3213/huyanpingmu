# -*- coding: utf-8 -*-
"""自动推送：装一个 git post-commit 钩子，每次提交后立刻推到 GitHub。

用法（在仓库根目录运行）：
    python tools/autopush.py install          # 装钩子，代理默认 127.0.0.1:7897
    python tools/autopush.py install --proxy http://127.0.0.1:7890
    python tools/autopush.py install --proxy none   # 直连
    python tools/autopush.py status           # 看装了没、看推送日志
    python tools/autopush.py remove           # 卸载

钩子只做一件事：git push 当前分支到 origin。它不会自动提交，
所以你仍然可以攒着一堆半成品改动不提交；一旦提交，就会立刻上传。
"""
import os
import stat
import subprocess
import sys

DEFAULT_PROXY = "http://127.0.0.1:7897"

HOOK = """#!/bin/sh
# EyeGuard 自动推送（由 tools/autopush.py 安装）
# 每次提交后把当前分支推到 origin，结果写进 .git/autopush.log
ROOT=$(git rev-parse --show-toplevel)
LOG="$ROOT/.git/autopush.log"
PROXY="{proxy}"

log() {{ echo "[$(date '+%F %T')] $*" >> "$LOG"; }}

log "commit -> push start"
if [ -n "$PROXY" ]; then
  unset ALL_PROXY all_proxy
  export http_proxy="$PROXY" https_proxy="$PROXY" HTTP_PROXY="$PROXY" HTTPS_PROXY="$PROXY"
fi

BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" = "HEAD" ]; then
  log "detached HEAD, skip"
  exit 0
fi

if git push origin "$BRANCH" >> "$LOG" 2>&1; then
  log "push ok ($BRANCH)"
else
  log "push failed ($BRANCH) — 会在下次提交时再试"
fi
exit 0
"""


def repo_root():
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("这里不是 git 仓库")
    return out.stdout.strip()


def hook_path(root):
    return os.path.join(root, ".git", "hooks", "post-commit")


def cmd_install(root, proxy):
    path = hook_path(root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(HOOK.format(proxy="" if proxy in ("none", "-", "") else proxy))
    try:
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass
    print("已安装钩子：%s" % path)
    print("代理：%s" % (proxy if proxy not in ("none", "-", "") else "直连"))
    print("之后每次 git commit 都会立刻 push 到 origin。")


def cmd_remove(root):
    path = hook_path(root)
    if os.path.exists(path):
        os.remove(path)
        print("已移除：%s" % path)
    else:
        print("没有装过")


def cmd_status(root):
    path = hook_path(root)
    print("钩子：%s" % ("已安装" if os.path.exists(path) else "未安装"))
    if os.path.exists(path):
        for line in open(path, encoding="utf-8", errors="replace"):
            if line.startswith("PROXY="):
                print("代理：%s" % line.split("=", 1)[1].strip().strip('"'))
    log = os.path.join(root, ".git", "autopush.log")
    if os.path.exists(log):
        lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
        print("--- 最近推送记录（%d 行） ---" % len(lines))
        for line in lines[-8:]:
            print(" ", line)
    else:
        print("还没有推送记录")


def main():
    root = repo_root()
    args = sys.argv[1:]
    action = args[0] if args else "status"
    proxy = DEFAULT_PROXY
    if "--proxy" in args:
        i = args.index("--proxy")
        if i + 1 < len(args):
            proxy = args[i + 1]
    if action == "install":
        cmd_install(root, proxy)
    elif action == "remove":
        cmd_remove(root)
    else:
        cmd_status(root)


if __name__ == "__main__":
    main()
