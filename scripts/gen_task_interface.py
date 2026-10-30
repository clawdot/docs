#!/usr/bin/env python3
"""从 Hub 的《接口参考》网页产物生成「任务接口」tab（只出中文）。

真源：ClawDot-Hub 仓库 docs/public/dist/web/api/*.json（《接口参考》正本，与 Word / PDF 同一份生成）。
用法：
    python3 scripts/gen_task_interface.py --hub ~/Desktop/Hub/ClawDot-Hub --ref origin/main

会重写：task/*.mdx、task/tools/*.mdx、images/task/*.png，以及 docs.json 里中文的「任务接口」tab。
生成物别手改；《接口参考》换版后重跑本脚本。
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "docs/public/dist/web/api"
DIAG = "docs/public/diag"
TAB = "任务接口"

# 文中指向《接口参考》章节的说法 → 本站页面。没列到的章节引用会让生成失败，避免留下读者打不开的「第 N 章」。
REFS = [
    ("工具、返回的形状、状态与拒绝码见接口参考第 4 章。", "工具、返回的形状、状态与拒绝码见 [返回结构与枚举](/task/response) 和各工具页。"),
    ("（第 4 章）", "（见 [接入与授权](/task/connect#分能力地址)）"),
    ("，见第 4 章「怎么连」", "，见 [怎么连](/task/connect#怎么连)"),
    ("，见第 4 章）", "，见 [分能力地址](/task/connect#分能力地址)）"),
    ("（访问票由授权链签发，见 2.2）", "（访问票由授权链签发，见 [授权链](#授权链)）"),
    ("（见第 4 章开头）", "（见 [接入与授权](/task/connect#每一步都带用户原话)）"),
    ("见第 18 章。", "见 [用户授权](#用户授权)。"),
    ("零售见 17.10。", "零售是授权 → 选商品 → 地址 → 结算 → 确认下单 → 查单与售后。"),
]
REF_LEFT = re.compile(r"第 ?\d+ ?章|(?<![\d.])\d{1,2}\.\d{1,2}(?![\d.])(?! ?[秒元分])")


def git_show(hub, ref, path, binary=False):
    out = subprocess.run(["git", "-C", str(hub), "show", f"{ref}:{path}"], capture_output=True, check=True)
    return out.stdout if binary else out.stdout.decode()


def chapter(hub, ref, n):
    return json.loads(git_show(hub, ref, f"{API}/{n}.json"))


def refs(text):
    for old, new in REFS:
        text = text.replace(old, new)
    return text


def inline(text, cell=False):
    """MDX 行内转义：代码段原样，其余转义 { } < >；表格里再转义 |。"""
    parts = re.split(r"(`[^`]*`)", refs(text))
    out = []
    for p in parts:
        if not (p.startswith("`") and p.endswith("`") and len(p) > 1):
            # 链接 [x](y) 里的括号不动，只转义 MDX 会当成 JSX / 表达式的字符
            p = p.replace("{", "\\{").replace("}", "\\}").replace("<", "&lt;").replace(">", "&gt;")
        if cell:
            p = p.replace("|", "\\|").replace("\n", "<br />")
        out.append(p)
    return "".join(out)


def table(b):
    code = set(b.get("code_cols") or [])
    head = b["head"]
    lines = ["| " + " | ".join(inline(h, True) or " " for h in head) + " |", "|" + "---|" * len(head)]
    for row in b["rows"]:
        cells = []
        for i, c in enumerate(row):
            c = str(c)
            if i in code and c and not c.startswith("`"):
                c = f"`{c}`"
            cells.append(inline(c, True))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def block(b, heading="##"):
    t = b["t"]
    if t in ("h3", "h4"):
        return f"{heading if t == 'h3' else heading + '#'} {strip_no(b['text'])}"
    if t == "label":
        return f"{heading} {inline(b['text'])}"
    if t == "p":
        return inline(b["text"])
    if t == "bullets":
        mark = (lambda i: f"{i + 1}.") if b.get("numbered") else (lambda i: "-")
        return "\n".join(f"{mark(i)} {inline(x)}" for i, x in enumerate(b["items"]))
    if t == "table":
        return table(b)
    if t == "code":
        lang = "bash" if b["text"].lstrip().startswith("curl") else "text"
        return f"```{lang}\n{b['text']}\n```"
    if t == "note":
        return f"<Note>\n{inline(b['text'])}\n</Note>"
    if t == "callout":
        tag = "Warning" if "indeterminate" in b["text"] else "Info"
        return f"<{tag}>\n{inline(b['text'])}\n</{tag}>"
    if t == "image":
        name = b["src"].split("/")[-1]
        return f"![]({'/images/task/' + name})"
    raise SystemExit(f"不认识的块类型：{t}")


def strip_no(title):
    """「17.11 任务接口（…）」→「任务接口（…）」。"""
    return re.sub(r"^\d+(\.\d+)*\s+", "", title)


def sections(blocks):
    """按 h3 切：{h3 标题（去章号）: [块]}，第一个 h3 之前的块记在 '' 下。"""
    out, cur = {"": []}, ""
    for b in blocks:
        if b["t"] == "h3":
            cur = strip_no(b["text"])
            out[cur] = []
        else:
            out[cur].append(b)
    return out


def labels(blocks):
    """按 label 切，返回 [(label 文字或 '', [块])]。"""
    out = [("", [])]
    for b in blocks:
        if b["t"] == "label":
            out.append((b["text"], []))
        else:
            out[-1][1].append(b)
    return out


def page(title, description, body, source, sidebar=None):
    fm = [f'title: "{title}"', f'description: "{description}"']
    if sidebar:
        fm.append(f'sidebarTitle: "{sidebar}"')
    text = "\n\n".join(body)
    left, fence = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
            continue
        if not fence:
            left += [m.group(0) for m in REF_LEFT.finditer(re.sub(r"`[^`]*`|\(/[^)]*\)", "", line))]
    if left:
        raise SystemExit(f"{title}：还有指向《接口参考》章号的说法没映射：{left}（补 REFS）")
    return "---\n" + "\n".join(fm) + "\n---\n\n" + f"{{/* {source}。由 scripts/gen_task_interface.py 生成，勿手改 */}}\n\n" + text + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hub", required=True, type=Path, help="ClawDot-Hub 仓库路径")
    ap.add_argument("--ref", default="origin/main")
    a = ap.parse_args()

    commit = subprocess.run(["git", "-C", str(a.hub), "rev-parse", "--short=8", a.ref],
                            capture_output=True, text=True, check=True).stdout.strip()
    idx = json.loads(git_show(a.hub, a.ref, f"{API}/index.json"))
    source = f"来源：Hub《接口参考》{idx['version']}（{idx['date']}，{commit}）"

    ch2, ch4, ch17, ch18, ch20 = (chapter(a.hub, a.ref, n) for n in (2, 4, 17, 18, 20))
    s2, s17, s18, s20 = sections(ch2["blocks"]), sections(ch17["blocks"]), sections(ch18["blocks"]), sections(ch20["blocks"])

    # 第 4 章：工具之前的通用段 + 按分组 label 切出的各工具
    pre, tools = [], []
    group = None
    for b in ch4["blocks"]:
        if b["t"] == "label" and re.search(r"（\d+ 个）$", b["text"]):
            group = b["text"]
            continue
        if group is None:
            pre.append(b)
        elif b["t"] == "h3":
            tools.append({"group": group, "name": strip_no(b["text"]), "blocks": []})
        else:
            tools[-1]["blocks"].append(b)
    parts = dict(labels(pre))
    intro = parts[""]

    task = ROOT / "task"
    (task / "tools").mkdir(parents=True, exist_ok=True)
    for old in (task / "tools").glob("*.mdx"):
        old.unlink()

    # 概览
    flow = s17["任务接口（照服务端的下一步走）"]
    body = [block(b) for b in intro]
    # 《接口参考》20.1 的对照表讲的是 Hub 站内的工具接口与说明书页，本站只讲任务接口，这里只留一段手写的取舍
    body += ["## 和工具接口的区别",
             "Hub 有两种接口：任务接口（本页，`/mcp/task`）是默认接法，顺序由服务端把着，每一步交回候选，下单前必停一次确认；"
             "零售只在任务接口。工具接口（`/mcp`）把业务接口直接交给你，适合要自己编排每一步的开发者，说明在 "
             "[Hub 文档中心](https://hub.clawdot.net/#/docs)。本站「外卖MCP」「跑腿MCP」两个 tab 是更早的直连接法，不再更新。"]
    body += ["## 一单怎么走"] + [block(b, "###") for b in flow]
    body += ["## 下一步", "<CardGroup cols={2}>\n"
             '<Card title="接入与授权" icon="plug" href="/task/connect">连接地址、OAuth 授权链、API Key、用户授权</Card>\n'
             '<Card title="返回结构与枚举" icon="brackets-curly" href="/task/response">所有工具同一个返回形状、状态与错误码</Card>\n'
             "</CardGroup>"]
    (task / "overview.mdx").write_text(page("任务接口概览", "一单一个 task，照服务端给的下一步走：外卖、跑腿、零售 27 个工具，一个地址办全", body, source, "概览"))

    # 接入与授权
    body = ["## 怎么连"] + [block(b) for b in parts["怎么连"]]
    body = [x.replace("<Info>\n**每一步都带用户原话", "## 每一步都带用户原话\n\n<Info>\n**每一步都带用户原话") for x in body]
    body += ["## 分能力地址"] + [block(b) for b in parts["分能力地址"]]
    body += ["## 协议与端点"] + [block(b) for b in s2[""]]
    body += ["### 授权发现"] + [block(b) for b in s2["授权发现"]]
    # 《接口参考》2.1 的例子打的是工具接口；任务接口的发现地址按线上实测补一句（2026-10-30 curl 核过）
    body.insert(len(body) - 1, "<Note>\n上例打的是工具接口 `/mcp`。连任务接口时，401 的 `resource_metadata` 指向 "
                "`/.well-known/oauth-protected-resource/mcp/task`，其中 `resource` 是 `https://hub.clawdot.net/mcp/task`；"
                "MCP Client 照标准发现走即可。\n</Note>")
    chain = labels(s2["授权链与用户授权"])
    body += ["## 授权链"]
    for lab, bs in chain:
        if lab.startswith(("浏览器授权链", "设备码授权链")):
            body += [f"### {inline(lab)}"] + [block(b) for b in bs]
    body += ["## 用户授权"] + [block(b) for b in s18["用户授权：任务接口"]]
    body += ["## API Key（服务端对服务端）"] + [block(b) for b in s20["可信平台：API Key + 任务接口"]]
    (task / "connect.mdx").write_text(page("接入与授权", "任务接口的连接地址、OAuth 授权链、API Key 与用户第一次使用时的授权", body, source))

    # 返回结构与枚举
    body = []
    for lab in ("返回（所有工具同一个形状，在 structuredContent 里）", "枚举取值"):
        body += [f"## {lab}"] + [block(b, "###") for b in parts[lab]]
    (task / "response.mdx").write_text(page("返回结构与枚举", "任务接口所有工具共用的返回形状、被拒时的形状、状态与错误码", body, source))

    # 各工具
    nav = {}
    for t in tools:
        bs = t["blocks"]
        short = bs[0]["text"].split("。")[0] if bs and bs[0]["t"] == "p" else t["name"]
        body = []
        for b in bs:
            if b["t"] == "label" and b["text"] == "Arguments":
                body.append("## 参数")
            else:
                body.append(block(b))
        slug = t["name"].replace("_", "-")
        (task / "tools" / f"{slug}.mdx").write_text(page(t["name"], inline(short).replace('"', "'"), body, source))
        nav.setdefault(re.sub(r"（\d+ 个）$", "", t["group"]).replace(" · 按顺序", ""), []).append(f"task/tools/{slug}")

    # 图
    img = ROOT / "images" / "task"
    img.mkdir(parents=True, exist_ok=True)
    for b in flow:
        if b["t"] == "image":
            name = b["src"].split("/")[-1]
            (img / name).write_bytes(git_show(a.hub, a.ref, f"{DIAG}/{name}", binary=True))

    # docs.json：中文「任务接口」tab 放在「主页」之后
    dj = ROOT / "docs.json"
    d = json.loads(dj.read_text())
    cn = next(x for x in d["navigation"]["languages"] if x["language"] == "cn")
    tab = {"tab": TAB, "groups": [{"group": "概览", "pages": ["task/overview", "task/connect", "task/response"]}]
           + [{"group": g, "pages": p} for g, p in nav.items()]}
    tabs = [x for x in cn["tabs"] if x["tab"] != TAB]
    tabs.insert(1, tab)
    cn["tabs"] = tabs
    dj.write_text(json.dumps(d, indent=4, ensure_ascii=False) + "\n")

    print(f"{source}：{len(tools)} 个工具，分组 {[(g, len(p)) for g, p in nav.items()]}")
    if len(tools) != sum(len(p) for p in nav.values()):
        sys.exit("工具数对不上")


if __name__ == "__main__":
    main()
