# Setup — starting from nothing

Assumes you have **nothing installed**. Budget about 45 minutes, most of it
waiting for downloads. Do this a day before you plan to record.

Work through it in order. Don't skip the verification commands — they're how
you find out something failed before it matters.

---

## Step 0 — Which computer are you on?

Almost everything below has a Mac path and a Windows path. Find your OS once
and follow that column throughout.

**Mac:** click the Apple menu → About This Mac. Note whether it says
**Apple M1/M2/M3/M4** (Apple Silicon) or **Intel**. You need this for Docker.

**Windows:** you need Windows 10 64-bit (build 19044+) or Windows 11.

---

## Step 1 — Install Docker Desktop

Docker runs software in sealed boxes called containers. PuppyGraph and
PostgreSQL both ship as containers, so this is the one required install.

### Mac

1. Go to **https://www.docker.com/products/docker-desktop/**
2. Click **Download for Mac** — pick **Apple Silicon** or **Intel Chip** to
   match what you found in Step 0. Picking wrong is the most common mistake here.
3. Open the downloaded `.dmg`, drag **Docker** into **Applications**
4. Open Docker from Applications. Accept the service agreement.
5. It may ask for your password to install networking components. That's normal.
6. Wait for the whale icon in your menu bar to stop animating

### Windows

1. Go to **https://www.docker.com/products/docker-desktop/**
2. Click **Download for Windows**
3. Run the installer. **Leave "Use WSL 2" checked** — this matters.
4. Restart when it asks. It really does need the restart.
5. Open Docker Desktop from the Start menu, accept the agreement
6. If it says WSL 2 needs an update, click the link it gives you, install, restart Docker

### Verify (both)

Open a terminal — **Terminal** on Mac, **PowerShell** on Windows — and run:

```bash
docker --version
docker compose version
```

You should see version numbers for both. If you get "command not found",
Docker Desktop isn't running. Open it and wait for the whale to settle.

Now the real test:

```bash
docker run --rm hello-world
```

You should see "Hello from Docker!". If you do, you're done with the hardest part.

### Give Docker enough memory

PuppyGraph wants room. Open Docker Desktop → **Settings** (gear icon) →
**Resources** → set **Memory to at least 4 GB**, 8 GB if you have 16 GB total.
Click **Apply & Restart**.

---

## Step 2 — Install Python 3

### Mac

Mac already has it. Check:

```bash
python3 --version
```

If that prints `Python 3.x.x`, skip ahead. If not, install from
**https://www.python.org/downloads/** — big yellow "Download Python" button.

### Windows

1. Go to **https://www.python.org/downloads/**
2. Click the yellow **Download Python 3.x** button
3. Run the installer. **Check the box that says "Add python.exe to PATH"** at
   the bottom of the first screen. This is easy to miss and annoying to fix later.
4. Click **Install Now**

Verify in a **new** PowerShell window:

```bash
python --version
```

On Windows the command is `python`. On Mac it's `python3`. Wherever this guide
says `python3`, Windows users type `python`.

### Install the two libraries you need

```bash
pip install duckdb neo4j
```

(Windows: if `pip` isn't found, use `python -m pip install duckdb neo4j`.)

---

## Step 3 — Get the project onto your computer

Download the `airline-network-graph-demo` folder from this conversation and put
it somewhere you can find — **Desktop** is fine.

Open a terminal **in that folder**:

- **Mac:** right-click the folder → Services → **New Terminal at Folder**.
  If that option isn't there, type `cd ` (with a space) in Terminal, then drag
  the folder onto the window and press Enter.
- **Windows:** open the folder in File Explorer, click the address bar, type
  `powershell`, press Enter.

Confirm you're in the right place:

```bash
ls          # Mac
dir         # Windows
```

You should see `README.md`, `docker-compose.yaml`, `schema.json`, `csv_data`.

---

## Step 4 — Test-run the whole thing (before recording)

```bash
python3 validate.py
```

Expect `ALL CHECKS PASSED`. If not, stop and read the error — it tells you
exactly which file disagrees with which.

```bash
docker compose up -d
```

First run downloads two container images, roughly 1–2 GB. **This takes 5–15
minutes on a normal connection.** Do it now, not while filming.

```bash
docker compose ps
```

Both `postgres` and `puppygraph` should show as running, with postgres healthy.

Give Postgres **30–40 seconds** to load the CSVs, then check it worked:

```bash
docker exec -it postgres psql -U postgres -d flightdb -c "SELECT count(*) FROM air.flight_routes;"
```

Expect `37041`. If you get "relation does not exist", the load is still
running — wait and retry.

Now open **http://localhost:8081** in your browser.

- Username: `puppygraph`
- Password: `puppygraph123`

Upload `schema.json`, run a couple of queries from the video guide, and confirm
everything works. **Then leave it running.** Warm caches are the difference
between a 2-second query and a 20-second one on camera.

### Stopping and resetting

```bash
docker compose down                              # stop, keep the data
docker compose down --volumes --remove-orphans   # stop and wipe, for a clean take
```

---

## Step 5 — Install a screen recorder

### Mac — already have one

Press **Cmd + Shift + 5**. A toolbar appears. Choose **Record Entire Screen** or
**Record Selected Portion**. Click **Options** → set **Microphone** to your mic
(built-in is fine) so your narration is captured. Then **Record**.

Stop with the button in the menu bar. Saves to Desktop as `.mov`.

### Windows — built-in

Press **Win + G** for Xbox Game Bar → Capture widget → record button. Works, but
it can't record File Explorer or the desktop, which is limiting.

### Better on both: OBS Studio (free)

**https://obsproject.com/** — more setup, much more control. Worth it if you
plan to record more than once.

Minimal OBS setup:
1. Sources panel → **+** → **Display Capture** → OK
2. Settings → Output → Recording Quality **High**, Format **mp4**
3. Settings → Audio → Mic set to your microphone
4. Big **Start Recording** button, bottom right

### Audio matters more than video

Phone earbuds with a mic beat your laptop's built-in mic. Record somewhere
quiet with soft furnishings — bare rooms echo badly. Do a 10-second test and
listen back before committing to a full take.

---

## Step 6 — Put it on GitHub

Two paths. Pick one.

### Path A — web upload (no git needed, recommended for a first repo)

1. Create an account at **https://github.com/signup** if you don't have one
2. Go to **https://github.com/new**
3. **Repository name:** `airline-network-graph-demo`
4. **Description:** `Global airline route network analysis with PuppyGraph — zero-ETL graph queries on PostgreSQL`
5. Select **Public**
6. **Check** "Add a README file" — you'll replace it
7. Click **Create repository**
8. On the repo page, click **Add file** → **Upload files**
9. **Drag the whole project folder's contents** into the browser window
   (open the folder first and select everything inside — not the folder itself)
10. Wait for uploads to finish. Scroll down, write `Initial commit` in the
    message box, click **Commit changes**

**Before you upload — trim the images.** The `img/` folder is 16 MB. GitHub
allows it, but their demo repos keep image folders small. Keep these four and
delete the rest:

```
img/01_world_routes.png
img/03_headline_route.png
img/04_reach_expansion.png
img/07_fragile_airports.png
```

That drops you to about 9 MB. Keep the full set locally for the video.

### Path B — git command line (better practice)

Install git: Mac runs `git --version` and offers to install it. Windows:
**https://git-scm.com/download/win**.

```bash
git init
git add .
git commit -m "Initial commit: airline network graph demo"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/airline-network-graph-demo.git
git push -u origin main
```

GitHub will ask you to authenticate in a browser. Follow the prompts.

### Add the video link afterwards

Once your video is up, edit the README on GitHub and add near the top:

```markdown
📺 **[Watch the demo video](YOUR-YOUTUBE-LINK)**
```

---

## Step 7 — Final pre-flight, the day of

Run through this list before you press record:

- [ ] Docker Desktop is open and the whale has stopped animating
- [ ] `docker compose ps` shows both containers up
- [ ] `http://localhost:8081` loads and you're logged in
- [ ] `schema.json` is uploaded and the Schema panel shows the model
- [ ] Every query has been run once already (warm cache)
- [ ] Browser zoom is at **125–150%**
- [ ] Terminal font is **18pt or bigger**
- [ ] Notifications are off — Mac: Focus mode. Windows: Focus assist.
- [ ] Bookmarks bar hidden (Mac `Cmd+Shift+B`, Windows `Ctrl+Shift+B`)
- [ ] All eight queries in a scratch text file, ready to paste
- [ ] Mic tested, 10-second playback checked
- [ ] Water nearby, phone silenced

---

## When something breaks

| Symptom | Cause | Fix |
|---|---|---|
| `docker: command not found` | Docker Desktop isn't running | Open it, wait for the whale |
| `port is already allocated` | Old container still up | `docker compose down --remove-orphans` |
| `localhost:8081` won't load | PuppyGraph still starting | Wait 30s; check `docker compose logs puppygraph` |
| `relation "air.airports" does not exist` | Postgres still loading | Wait 30s and retry |
| Schema upload fails | Postgres not ready yet | `docker compose logs postgres`, look for "ready to accept connections" |
| Query results show empty properties | Missing the `USING` line | Add `USING enableCypherEngineProperties 'true'` |
| Everything is broken | — | `docker compose down --volumes --remove-orphans` then `up -d` again |

Reading the logs is genuinely the fastest way to diagnose anything:

```bash
docker compose logs postgres
docker compose logs puppygraph
```
