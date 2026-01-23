curl.exe 'https://jules.googleapis.com/v1alpha/sessions' `
  -X POST `
  -H "Content-Type: application/json" `
  -H "X-Goog-Api-Key: $env:JULES_API_KEY" `
  -d '{
    "prompt": "このリポジトリの gemini_command.md の内容を実行してください",
    "sourceContext": {
      "source": "sources/github/komiyamma/make_md_summary",
      "githubRepoContext": {
        "startingBranch": "main"
      }
    },
    "requirePlanApproval": false,
    "automationMode": "AUTO_CREATE_PR",
    "title": "gemini_command.md Markdown 完全自動実行"
  }'