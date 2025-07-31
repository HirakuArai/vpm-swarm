import json, os, pathlib, datetime, argparse
from github import Github
from openai import OpenAI

BOT_NAME = "openai-bot"

def collect_context(thread, k: int = 20) -> list[dict]:
    """直近 k 件のコメントを GPT 用 messages に整形"""
    ctx = []
    for c in list(thread.get_comments())[-k:]:
        role = "assistant" if c.user.login == BOT_NAME else "user"
        ctx.append({"role": role, "content": c.body})
    return ctx

def main(repo_full: str, event_name: str, payload_json: str) -> None:
    # ── GitHub API 初期化 ──────────────────────────
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set")
    gh   = Github(token)
    repo = gh.get_repo(repo_full)

    event = json.loads(payload_json)

    # ── Issue コメント以外はスキップ ───────────────
    if event_name != "issue_comment":
        print(f"skip: {event_name} is not supported yet")
        return

    # ── コメント取得 ──────────────────────────────
    cmt    = event["comment"]
    thread = repo.get_issue(event["issue"]["number"])

    # ── GPT-4.1 へ問い合わせ ──────────────────────
    messages = collect_context(thread) + [{"role": "user", "content": cmt["body"]}]

    client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    reply   = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.5,
        max_tokens=800
    ).choices[0].message.content

    # ── Bot 返信を投稿 ────────────────────────────
    thread.create_comment(reply)

    # ── ndjson 保存（Watcher → EG-Space で使用）──
    now_iso = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    records = [
        {"id": f"gh_cmt_{cmt['id']}",
         "speaker": cmt["user"]["login"],
         "ts": cmt["created_at"],
         "text": cmt["body"]},
        {"id": f"gh_bot_{int(datetime.datetime.utcnow().timestamp())}",
         "speaker": BOT_NAME,
         "ts": now_iso,
         "text": reply},
    ]
    path = pathlib.Path("data/raw") / f"{now_iso[:10]}-github.ndjson"
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--event")
    ap.add_argument("--payload")
    args = ap.parse_args()

    if os.getenv("OPENAI_API_KEY"):
        main(args.repo, args.event, args.payload)
    else:
        raise RuntimeError("OPENAI_API_KEY is not set")
