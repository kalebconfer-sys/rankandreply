# Get this onto your computer (Windows)

Everything lives in your GitHub repository **kalebconfer-sys/rankandreply**, on the branch `claude/ai-automated-business-plan-ptu9y7`. Pick **one** way to get it.

## Step 1: get the files

**Option A, recommended: GitHub Desktop** (keeps your copy up to date with one click)
1. Install GitHub Desktop from desktop.github.com and sign in with your GitHub account.
2. File → Clone repository → `kalebconfer-sys/rankandreply` → choose a folder, for example `C:\Users\<you>\Documents\rankandreply`.
3. At the top, click **Current branch** → choose `claude/ai-automated-business-plan-ptu9y7`.
   **If you only see `index.html` and no `business` folder, you're on the wrong branch.** The new work isn't on `main` yet.
4. Later, when Claude makes changes in the cloud, click **Fetch origin**, then **Pull**, and your computer has them.

**Option B: one-time download (no account needed)**
1. Download the ZIP: https://github.com/kalebconfer-sys/rankandreply/archive/refs/heads/claude/ai-automated-business-plan-ptu9y7.zip
2. Right-click it → Extract All → put it in Documents.

A ZIP is a snapshot: it won't pick up later changes. Use GitHub Desktop if you'll keep working with Claude in the cloud as well.

## Step 2: install Python (once)
1. Go to python.org/downloads and install Python 3.11 or newer.
2. On the **first screen** of the installer, tick **"Add python.exe to PATH"**.

## Step 3: run the setup (once)
1. Open the folder `business\tools`.
2. Double-click **`setup.bat`**. It creates a private Python environment, installs everything, and opens `.env`.
3. Paste your API keys into `.env` (see `business\02-plan\day-by-day.md`, day 2) and save.
4. Double-click `setup.bat` again. Every AI you set up should say `ready`.
5. **Optional:** install Ollama (ollama.com) and run `ollama pull llama3.1:8b` for the free local model. On a laptop with less than 16 GB of memory, skip it and add `LOCAL_DISABLED=1` to `.env`.

If anything errors, copy the whole message into Claude (step 5) and ask it to fix it.

## Step 4: the daily buttons (all in `business\tools`)

| Double-click | When | What it does |
|---|---|---|
| `daily.bat` | Every day | Finds new Reddit, Hacker News and Upwork posts, drafts replies and proposals, and opens today's page with Open and Copy buttons |
| `replies.bat` | Every day you get replies | **Drag your exported replies CSV onto it.** Tags each reply, drafts answers, runs the free report for every "yes", and opens today's page |
| `leads.bat` | When you have a new Apollo export | **Drag your verified Apollo CSV onto it.** Writes the ready-to-upload file with opening lines. Asks before running a batch that costs more than the safety limit |
| `posts.bat` | Mondays | Writes this week's 3 LinkedIn posts for you to schedule |

Nothing here sends an email or posts anything. You do that, from your own accounts.

## Step 5: keep working with Claude on your computer

Any of these will pick up exactly where we left off. The file `CLAUDE.md` at the top of the folder tells Claude what the project is, where everything is, and the rules.

- **Claude desktop app:** open the Code tab and choose the `rankandreply` folder.
- **Claude Code in a terminal:** open the folder in Terminal or PowerShell and type `claude`. Type `claude remote-control` instead to also see and steer that session from the Claude app on your phone.
- **Keep using the cloud (like this conversation):** that works too. It saves to the same GitHub repository. Use GitHub Desktop's **Pull** to bring the changes down.

If you work in both places, **Pull before you start** and let Claude commit and push when you finish, so the two copies don't drift apart.

## Your private files stay on your computer

These are **never uploaded** to GitHub, because the repository is public:
- `business\tools\.env`: your API keys and passwords
- `business\data\`: leads, replies, reports, clients and the outbox

Back these up yourself, for example by copying `business\data` into a OneDrive or Google Drive folder weekly.

## Checking the tools still work

After any change, Claude (or you) can run the offline tests. They use a stand-in AI, cost nothing and never touch your accounts:
```
cd business\tools
.venv\Scripts\python tests\run_all.py
```
The last line should say `0 failed`.
