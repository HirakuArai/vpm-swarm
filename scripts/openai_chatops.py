import json, os, pathlib, datetime, argparse, time
from github import Github
from openai import OpenAI

BOT_NAME = "openai-bot"
DATA_DIR = pathlib.Path("data/raw")         # ここに ndjson を貯める
DATA_DIR.mkdir(parents=True, exist_ok=True) # data/raw 両方まとめて作成

def collect_context(thread, k: int = 20) -> list[dict]:
    ctx = []
    for c in list(thread.get_comments())[-k:]:
        role = "assistant" if c.user.login == BOT_NAME else "user"
        ctx.append({"role": role, "content": c.body})
    return ctx

def main(repo_full: str, event_name: str, payload_json: str) -> None:
    gh_token = os.getenv("GITHUB_TOKEN")
    if not gh_token:
        raise RuntimeError("GITHUB_TOKEN is not set")

    gh     = Github(gh_token)
    repo   = gh.get_repo(repo_full)
    event  = json.loads(payload_json)

    # —— Issue コメントのみ対応 ——
    if event_name != "issue_comment":
        print(f"skip: unsupported event {event_name}")
        return

    cmt    = event["comment"]
    thread = repo.get_issue(event["issue"]["number"])

    messages = collect_context(thread) + [{"role": "user", "content": cmt["body"]}]

    # —— GPT-4.1 呼び出し ——
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    reply  = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.5,
        max_tokens=800
    ).choices[0].message.content

    # —— Bot 返信を投稿 ——
    thread.create_comment(reply)

    # —— ndjson へ保存 ——
    now     = datetime.datetime.now(datetime.timezone.utc)
    now_iso = now.isoformat(timespec="seconds")
    records = [
        {"id": f"gh_cmt_{cmt['id']}",
         "speaker": cmt["user"]["login"],
         "ts": cmt["created_at"],
         "text": cmt["body"]},
        {"id": f"gh_bot_{int(time.time())}",
         "speaker": BOT_NAME,
         "ts": now_iso,
         "text": reply},
    ]
    path = DATA_DIR / f"{now:%Y-%m-%d}-github.ndjson"
    with path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--event")
    ap.add_argument("--payload")
    args = ap.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set")
    main(args.repo, args.event, args.payload)
