# Screenshots to capture

The README has five commented-out image slots for PuppyGraph UI screenshots.
This matches how PuppyGraph's own demo READMEs work — see their
[network-topology-demo](https://github.com/puppygraph/puppygraph-getting-started/tree/main/use-case-demos/network-topology-demo),
which embeds `img_login.png`, `img_schema.png`, and query result shots inline.

Take these while you're recording the video anyway. It costs five extra minutes.

## What to capture

| Save as | What's on screen | Where it goes in the README |
|---|---|---|
| `img_login.png` | The PuppyGraph login page at `localhost:8081` | Modeling the Graph, step 1 |
| `img_upload.png` | The Upload Graph Schema JSON block with `schema.json` chosen | Modeling the Graph, step 2 |
| `img_schema.png` | The rendered schema page showing Airport / Country / Airline and the four edges | Modeling the Graph, step 3 |
| `img_query_01.png` | Gremlin query 1 result — Seattle's 90 destinations, **Radial layout** | Querying the Graph, query 1 |
| `img_query_02.png` | Kathmandu after right-click → Expand with all Edge Labels | Querying the Graph, query 2 |

## How to take them

**Mac:** `Cmd + Shift + 4`, then **Space** to switch to window mode, then click
the browser window. Captures just the window with a clean shadow. Saves to
Desktop.

**Windows:** `Win + Shift + S` → drag a rectangle → paste into Paint and save,
or use the Snipping Tool directly.

Crop to the browser content. Don't include your bookmarks bar, other tabs, or
the OS menu bar.

## Then

1. Put the five files in `img/`
2. Open `README.md` and delete the `<!--` and `-->` around each of the five
   image lines — they're marked with a `SCREENSHOT:` comment directly above
3. Commit

Before:
```markdown
<!-- SCREENSHOT: the PuppyGraph login page -->
<!-- ![img_login.png](img/img_login.png) -->
```

After:
```markdown
![img_login.png](img/img_login.png)
```

## Keep them small

Screenshots of a browser window at 1800px wide are plenty. If any file lands
above ~1 MB, resize it:

```bash
pip install pillow
python3 -c "
from PIL import Image
import glob, os
for f in glob.glob('img/img_*.png'):
    im = Image.open(f)
    if im.width > 1800:
        im = im.resize((1800, round(im.height*1800/im.width)), Image.LANCZOS)
    im.save(f, optimize=True)
    print(f, os.path.getsize(f)//1000, 'KB')
"
```

The four data figures already in `img/` are 1800px and under 1.4 MB each.
