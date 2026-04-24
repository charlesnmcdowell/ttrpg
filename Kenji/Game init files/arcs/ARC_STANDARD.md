# Arc documentation — gold standard

**Purpose:** Every arc file in `arcs/` should make the **core problem**, **regional stakes**, and **NPC agendas** obvious enough that a DM or player-facing NPC can **state them in plain language** without tracker jargon.

**Reference implementation:** `north_relay_two_chapter_plan.md` § **Kharn forge crisis — authoritative table spine** (Book 4 north / Kharn). New or refactored arcs should match that level of clarity.

---

## Principles

1. **Core problem first** — One paragraph (or “one-sentence pitch” + short expansion) answering: *What is broken or unstable, right now, in this arc?*
2. **Regional stakes** — Explicit answer: *If this is not resolved, what gets worse for which people, trade routes, polities, or resources?* Stakes can be economic, military, spiritual, or personal—**they do not have to be world-ending**.
3. **Meta-threat optional** — Arcs **may** connect to Threat 1 (Hollowing), the March, the Court, etc.—but **many arcs stand on their own** (e.g. council politics, bandit economy, local succession). If there **is** a bible threat link, **name it once**; do not make every arc a Hollowing subplot.
4. **NPC communicability** — For **every NPC who materially drives the plot**, the arc doc should support this test: *If this NPC spoke for thirty seconds in-scene, could they say (a) what they think the problem is, (b) what they are doing about it, (c) what outcome they want?*  
   - **Protagonists and allies** usually want a **better** resolution.  
   - **Antagonists and opportunists** may want a **worse** resolution or profit from **failure**—that is **valid**; document **their** hoped-for outcome honestly.
5. **No vibe-only villains** — If someone profits from catastrophe, say **how** (black market, contract boom, political climb, sealed records, etc.).

---

## Mandatory template (copy into each `arcs/*.md`)

```markdown
## Arc clarity (gold standard)

### Core problem
[What is wrong / unstable in one tight summary.]

### If unresolved — regional effect
[Who suffers, what spreads, what breaks—trade, war, law, faith, lineage, etc.]

### Optional: link to campaign threat layer
[None / Threat N — one line. Omit if this arc is local or orthogonal.]

### NPC stances (plot-driving characters)

| NPC | How they state the problem | Their action (what they do) | Outcome they want |
|-----|----------------------------|-----------------------------|-------------------|
| … | Plain-language line you could put in dialogue | Concrete behavior | Best case *for them* (can be selfish or cruel) |

*Add rows only for NPCs who move the arc; background color can stay in `character_tracker.md`.*

### PC / party hook (how we entered this)
[1–3 sentences: coincidence, bond, contract, disaster, etc.]

### Dramatic irony or secrets (optional)
[What the table knows vs what a PC knows; items that connect arcs without requiring a speech.]
```

---

## Self-check before saving an arc file

- [ ] **Core problem** is paraphraseable by a **non-DM** in one breath.
- [ ] **Regional stakes** are **not** just “bad vibes”—they name **consequences**.
- [ ] **Hollowing** (or any meta-threat) is **not** pasted in unless this arc **earns** that connection.
- [ ] Every **plot-driving NPC** has a row (or an explicit “crowd / faction” row with a named spokesperson).
- [ ] At least one NPC row reflects **opposition or profit from failure** if the arc has **real** conflict of interest.

---

## File hygiene

- **One arc file** = one primary **camera** or **spine** (north relay, south March, council pressure, etc.).
- Long **session truth** and **beat ladders** stay below the **Arc clarity** section so the top of the file answers *why this exists*.
- Cross-link `fraying_empire_campaign.md` threat entries only where useful; avoid duplicate paragraphs—**link + one summary line** is enough.

---

*DM plan, not automatic in-play canon until scenes establish it at the table.*
