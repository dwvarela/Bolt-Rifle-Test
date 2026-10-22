# Project rules (Bolt-Rifle-Test / boltrifle mod) - READ FIRST

## HARD RULE: never more than 2 arms / 2 hands in any animation (set by the user, permanent)
* In every animation of every gun there are **exactly two hands** (`left_hand`, `right_hand`) and never more. No `bolt_hand`, no extra arm,
  no hand that is hidden/shown or scaled in and out, no hand that appears or disappears while it can be seen. The same two hands move
  continuously from pose to pose (the right hand travels from the grip to the bolt handle and back).
* Never use scale keys to hide/show a hand or a magazine. A magazine never disappears or re-appears in view: it moves out of view
  (carried by the hand) and moves back in. Spent cases / chambered rounds may only be toggled while hidden inside the receiver or after
  they have fallen out of view.
* This rule may not be changed, worked around or re-interpreted for any reason. `tools/animlib.py` enforces it when animations are written
  (the generators fail if it is broken).

## Other standing rules
* Models must match the reference photos; do not change shapes beyond the photos without permission.
* Reference jar (Point Blank) is reference-only: never copy its assets, code or models.
* Work in parts, commit + push after each part, verify CI, give the preview link, keep messages short.
* Sounds: use the user's own recordings in `Gun Sound Effects.zip` (see `tools/gen_sounds.py`), not synthesis.
