"""Hand-tuned cover content for Unit 1: Exploring One-Variable Data.

Every number here is lifted from the unit's own lessons:

  pet tally          1.3 notes, the pet-ownership worked example (n = 40)
  quiz scores        1.5 notes, the stemplot example
  period 1 scores    1.9 notes, the back-to-back stemplot
  commute times      1.6/1.7, the outlier example (the 45 is the point)
  heights N(70, 3)   1.10 notes, the running Empirical Rule example
  mean of 106/10     1.7, summary statistics
  discrete vs cont.  1.2, the language of variation

Layout is hand-placed: art frames the title band, the meme anchors the
bottom-right, and the tally table balances it top-left.
"""

ELEMENTS = [
    # ── Top band ─────────────────────────────────────────────────────────────
    # Topic 1.3 — the pet-ownership tally, mid-count.
    {"type": "tally", "at": (64, 56), "tilt": -2,
     "rows": [("Dog", 12), ("Cat", 8), ("Fish", 6), ("Bird", 4), ("None", 10)],
     "caption": "pet ownership (n = 40)"},

    # Topic 1.5 — the quiz scores the stemplot lesson works with.
    {"type": "scene", "scene": "quiz", "at": (318, 74), "skew": (0.98, -0.10, 0.20, 0.96),
     "inner": {"type": "dotplot", "w": 200,
               "data": [54, 58, 61, 65, 67, 72, 78, 79, 85]},
     "caption": "quiz scores"},

    # Topic 1.9 — Period 1's scores from the back-to-back comparison.
    {"type": "histogram", "at": (584, 52), "skew": (0.97, 0.12, -0.24, 0.95),
     "data": [68, 71, 72, 76, 79, 83, 85, 88, 91, 94],
     "w": 216, "h": 138, "caption": "Period 1 scores"},

    # Topic 1.10 — heights N(70, 3) with the middle 68% hatched.
    {"type": "normal", "at": (60, 288), "skew": (0.99, 0.08, 0.16, 0.97),
     "w": 240, "mu": 70, "sd": 3, "shade": (-1, 1),
     "caption": "adult heights (inches)"},

    # Topic 1.7 — the mean, worked.
    {"type": "slab", "at": (610, 286), "tilt": 2, "size": 16,
     "lines": ["\\text{mean} = \\frac{106}{10}", "= 10.6 \\text{ hours}"]},

    # The sleep context those hours came from.
    {"type": "scene", "scene": "bed", "at": (398, 300), "tilt": 3,
     "w": 128, "h": 100, "caption": "sleep"},

    # ── Bottom band ──────────────────────────────────────────────────────────
    # Topic 1.2 — one variable, two kinds.
    {"type": "split", "at": (64, 762), "tilt": -2, "w": 296, "h": 112},

    # Topics 1.6–1.8 — the commute-time boxplot, outlier and all.
    {"type": "scene", "scene": "car", "at": (300, 906), "skew": (0.98, -0.09, 0.18, 0.96),
     "inner": {"type": "boxplot", "w": 230,
               "data": [8, 12, 15, 15, 18, 20, 22, 25, 28, 45]},
     "caption": "one-way commute (min)"},

    # The joke. Unit 1 ends on the Normal distribution; so does the cover.
    {"type": "meme", "at": (556, 760), "tilt": 2, "w": 246},

    # Topic 1.10 — the z-score, the unit's parting formula.
    {"type": "slab", "at": (92, 936), "tilt": -3, "size": 17,
     "lines": ["z = \\frac{x - \\mu}{\\sigma}"]},

    # 1.1's very first idea: a sample stands in for n = 12,000.
    {"type": "equation", "at": (652, 986), "tilt": -2,
     "expr": "n = 12{,}000", "size": 19},
]
