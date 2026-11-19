# The World in One Image — Thursday, 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Tiannuryadins/makefun-news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Tiannuryadins/makefun-news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

An entry for the make.fun bounty **"Sum up 19 November's world news in one image"**
(`news-image-20261119`): $250 in prizes shared by the top 50 entries — $50 for
1st, $30 for 2nd, $15 for 3rd, $5 for 4th–10th, $3 for 11th–50th. Entries close
Saturday 21 November 2026, 00:00 UTC (07:00 WIB). Entry is free.

## The idea

A newspaper front page for one day: the program writes a single poster that
lets anyone who missed Thursday, 19 November 2026 catch up on it at a glance —
one lead story, a by-the-numbers strip, and twelve more stories in a grid, each
with a category tag and a hand-drawn icon. The image carries the news itself
(the judge has no news feed), so every story is named, dated and sourced on
the poster.

Run it and you get `world_news_19_nov_2026.png` written to `/output/entry.png`:

```bash
python3 main.py                                    # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py        # local testing override
```

`main.py` is standard library only and reads the poster PNG that ships in this
repo — no Pillow at run time (the grader runs `python3 -P -s`, where Pillow
does not exist), no network, and the same bytes on every run, so the two
grader runs write identical files. If `/output` is not writable it falls back
to `./output/entry.png`. The program checks the gate itself on every run with
a small stdlib PNG parser: the file must be a whole PNG of at most 1 MiB and
1024×1024 px. This poster is 1024×1024 px and under 1 MiB.

## The day in thirteen stories

All thirteen were reported on 19 November 2026 and cross-checked against at
least two independent sources (full list in BUILD-TRANSCRIPT.md):

| # | Story |
| --- | --- |
| 1 | **Trump, Xi and Putin meet at last in Shenzhen** — first-ever trilateral at APEC; arms control and the Iran war on the table, Ukraine left off, no deal expected; a Trump–Putin one-on-one the same day. *(Reuters, The Hindu BusinessLine, Daily Caller)* |
| 2 | **GTA VI rolls out worldwide** — rolling midnight launch from New Zealand; 99 on Metacritic; $1.5B in preorders. *(Polygon, Reuters, Stocktwits, TBS News)* |
| 3 | **World court rules on Myanmar** — ICJ delivers its Rohingya genocide verdict at The Hague; a first state verdict is possible. *(Pollar, The Globuzz, BDJam, CrisisBrief)* |
| 4 | **Anthropic debuts on Nasdaq** — Claude maker lists as ANT at $83; 825M shares; up to $1.45T valuation. *(Invezz, NerdWallet, Bitrue)* |
| 5 | **Cyclone Akvan turns very severe** — landfall due Friday noon; extremely heavy rain on Andhra and Odisha coasts. *(IMD, The Library Estate, GKToday)* |
| 6 | **EU's €45B Ukraine loan in Berlin** — Coalition of the Willing meets today; €20B budget, €25B arms; Russia to repay. *(Reuters, EuropeSays, Agence Europe)* |
| 7 | **Fed minutes point to more hikes** — almost all officials back further rises; 10–2 hold at 3.75–4%. *(Reuters, Medium, Odaily)* |
| 8 | **Voyager 1 a light-day from Earth** — NASA briefs today; probe 16bn miles out; a signal takes a full day. *(NASA, Aerospace Global News, People, Reuters)* |
| 9 | **Iran hits Kuwait base; Gulf on edge** — Bahrain's fourth attack in six days; Riyadh lifts alerts in three cities. *(Reuters, AP, Jawawa)* |
| 10 | **Nvidia's new chief promises raises** — Kress pledges earlier pay rises at first all-hands; H-chip sales to China stop. *(SimpleLife, VT Markets)* |
| 11 | **India, Japan review defence ties** — 2+2 dialogue in Tokyo; Rajnath, Jaishankar meet Koizumi, Motegi. *(Indian Economic Observer, The Daily Jagran)* |
| 12 | **Tanker hit by drones off Bulgaria** — Gas Husky struck four times; 19 crew rescued; 17th ship hit since July. *(Reuters, The Library Estate)* |
| 13 | **Somalia–UAE row deepens** — defence chief calls UAE an "enemy"; Mogadishu shut airspace to Emirati jets. *(Dhacdo, Horn Economic Review, Dawan)* |

Nothing here is invented. Stories 9–13 are flagged as borderline in
BUILD-TRANSCRIPT.md: their events fall on 17–18 November but they dominated
the 19 November reporting (19 Nov wires and briefs), the same rule the 17 and
18 November entries used. Deliberately excluded on the date rule: the Deutsche
Bank Epstein files (17 Nov), Hegseth's Venezuela visit (18 Nov), the Gaza
ground operation (18 Nov), the Peltola Senate call (17 Nov) and the UN
chemicals report (17 Nov).

## Files in this repo

- `main.py` — the entry point: reads the poster and writes `/output/entry.png`
- `render_poster.py` — draws the poster with Pillow (build time only)
- `world_news_19_nov_2026.png` — the poster (1024×1024)
- `LICENSE` — MIT (OSI-approved)
- `BUILD-TRANSCRIPT.md` — research notes, test results, bundling notes

To change the poster, edit `render_poster.py` and re-run it:

```bash
pip install pillow        # only needed for rendering, not for the entry
python3 render_poster.py  # regenerates world_news_19_nov_2026.png
```

The renderer asserts that every headline and body fits its card, so a layout
overflow fails loudly at build time instead of shipping a broken poster.

## License

MIT — see `LICENSE`. Copyright (c) 2026 Januar.
