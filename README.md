# news-image-20261121 — The World in One Day

Entry for the make.fun competition **news-image-20261121**:
"Sum up 21 November's world news in one image".

A newspaper front page, **"THE WORLD IN ONE DAY — Saturday
21 November 2026"**, drawn by `render.py` (Python 3, Pillow, system
fonts only, no network, fully deterministic). It holds **38 verified
stories from six continents** — 8 illustrated panels, a world map with
12 numbered pins, a day-in-figures strip — every headline happened, or
was first reported, on Saturday 21 November 2026. See `STORIES.md`
for the story list and its live sources.

## Lead stories

- Russia's biggest barrage of the war: 400+ drones and 110+ missiles
  hit Ukraine overnight; three Kyiv bridges damaged, eight killed —
  and two missiles land in Poland as NATO jets scramble.
- The AI rout: Nasdaq dives 5.3%, S&P 500 falls 3.7% into correction;
  Nvidia drops 14% and Anthropic 9% a day after its record debut.
- The World Court finds Myanmar committed genocide against the
  Rohingya; Trump defends Putin and Xi after the Shenzhen summit;
  BepiColombo reaches Mercury orbit; GTA VI takes $3.8bn on day one.

## Run

`main.py` (Python 3.13, standard library only) copies `entry.png` to
`/output/entry.png`, verifying format, size (≤ 1 MiB) and dimensions
(1024×1024) first. It writes the same bytes on every run:

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

To redraw the image from scratch:

```
python3 render.py   # writes entry.png (1024x1024) beside this file
```

## License

MIT — see `LICENSE`.
