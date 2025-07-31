import json, os, pathlib, datetime
from github import Github
from openai import OpenAI

BOT_NAME = "openai-bot"

def collect_context(thread, k=20):
    ctx = []
    for c in list(thread.get_comments())[-k:]:
        role = "assistant" if c.user.login == BOT_NAME else "user"
        ctx.append({"role": role, "content": c.body})
    return ctx

def main(repo_full, event, payload_json):
    gh     = Github(os.getenv("GITHUB_TOKEN"))
    repo   = gh.get_repo(repo_full)
    event  = json.loads(payload_json)

    if event == "issue_comment":
        c = event["comment"]; thread = repo.get_issue(event["issue"]["number"])
    else:                          # discussion_comment
        c = event["comment"]; thread = repo.get_discussion(event["discussion"]["number"])

    messages = collect_context(thread) + [{"role":"user","content":c["body"]}]

    client   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    reply    = client.chat.completions.create(
                 model="gpt-4.1",
                 messages=messages,
                 temperature=0.5,
                 max_tokens=800).choices[0].message.content

    thread.create_comment(reply)                       # Bot 返信

    # ndjson 保存（RAW → Watcher → EG-Space）
    now   = datetime.datetime.utcnow().isoformat()+"Z"
    out   = [
        {"id":f"gh_cmt_{c['id']}", "speaker":c["user"]["login"],
         "ts":c["created_at"], "text":c["body"]},
        {"id":f"gh_bot_{int(datetime.datetime.utcnow().timestamp())}",
         "speaker":BOT_NAME, "ts":now, "text":reply},
    ]
    path  = pathlib.Path("data/raw") / f"{now[:10]}-github.ndjson"
    path.parent.mkdir(exist_ok=True)
    with path.open("a",encoding="utf-8") as f:
        f.write("\n".join(json.dumps(o, ensure_ascii=False) for o in out)+"\n")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--repo"); p.add_argument("--event"); p.add_argument("--payload")
    a = p.parse_args()
    if os.getenv("OPENAI_API_KEY"):             # guard
        main(a.repo, a.event, a.payload)
