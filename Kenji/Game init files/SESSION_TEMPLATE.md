# Session log (template)

Copy per session. Keep in the same folder or your notes app.

| Field | Value |
|-------|--------|
| **Date** | |
| **In-game** | [Month] [Day], [Year] AR · [Time of day] · [Location] |
| **Scene** | |

**Recap (3–5 sentences)**


**Player decisions / outcomes**


**Time advanced** (hours / long rest?)


**Combat / EXP** (if any)


**Clocks / consequences to track**


**Next session hooks**


**Files to update** (check any that apply)

- [ ] `character_tracker.md` — update NPC locations, dispositions, goal statuses, timestamps. Add new goals. Resolve completed goals (write conclusion, don't delete).
- [ ] `npc_appearance.md` — add physical details for any newly introduced NPCs.
- [ ] `AI_CONTEXT.md` — update `canon_pointer`, `Where we left off`, `Time and place` fields.
- [ ] Chapter prose file — write/append session prose to the active book's chapter file.
- [ ] `tracking_rules.md` — only if a new rule is needed.

**Post-session checklist (from tracking_rules.md)**

1. Every change in `character_tracker.md` gets an in-game date timestamp.
2. Any character whose `last_updated` is >2 in-game days behind current date → flag for drift check.
3. Any goal whose `due_date` has passed → resolve or update before next session.
4. If a chapter aged out of the 2-chapter review window → run consolidation pass (move important facts to tracker, let prose details go).
5. Alive characters must have at least one active goal. If they don't, add one or mark them MIA.
