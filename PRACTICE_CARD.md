# PRACTICE CARD — hold this, not the transcript

## GATES (only three numbers)
**10:00** realization · **15:00** demo starts · **20:00** demo ends
Realization at 10:45 = fine. Temporal section at 13:30 = cut failure #4 out loud.

---

## THE ONE RULE FOR JOKES
**Throw them away.** Same volume as the sentence before. Do not lift your pitch
into a punchline. Say it, stop, move on.

If you announce a joke it dies. If you undersell it, it lands.
You are *in* every joke, never above it.

---

## THE 8 LANDINGS — slow down, then stop. No joke after these.

1. "This is good code."
2. "That's not information about the order. That's information about **how far along the job got**."
3. **"It's a program counter. In your orders table. With an index on it."**
4. "We didn't set out to build a workflow engine. We just kept solving the next requirement."
5. **"A workflow is what a job gradually turns into."**  ← beginners leave with this
6. "Waiting became a language feature."
7. **"In the first half of this talk, the answer was: me."**  ← point at yourself
8. **"An abstraction is useful right up until you start implementing the abstraction it was supposed to give you."**  ← experts leave with this

---

## THE 5 MOMENTS THAT CARRY THE TALK

**JUST × 7** (9:30) — counter's been in the corner unremarked for 7 min.
Slide flips to `Workflow Engine v1.0`. **Biggest laugh. Count three beats.
Do not talk over it.**

**Program counter** (7:15) — say it → PAUSE → "I'm not saying the code got ugly.
The code is fine. I'm saying we introduced a concept. And nobody decided to."

**ME → RUNTIME** (15:00) — point at yourself on "me". Count off:
*my columns, my scheduler, my dedup table, my reconciler, my phone.*
Drop the hand: **"Here, the answer is the runtime."**

**Mapping slide** (after the Temporal code) — 6 sec per row, point don't teach.
Click → reconciler row appears with a dash → beat → **"There isn't a row for that one."**

**The landing** (25:00) — see below.

---

## OPENING 40 SECONDS (the hardest part — know it cold)

> It's Sunday. It's six pm. And you are in a room, voluntarily, to hear about
> background jobs.
> I see that. I've also structured this to be shorter than getting from
> Koramangala to Whitefield. *[laugh]*
>
> Two questions. Hands up.
> One: who runs Sidekiq in production? *[look]*
> Two, the real one: who has a Sidekiq job with a **state machine** inside it?
> *[look]* Some of you put your hand up very fast. *[laugh]*
>
> Keep that job in your head. We're going to go find it.

---

## THE CLOSING SEQUENCE — do not improvise this

1. `Is this still a job?` on screen
2. "I don't know, for your system. I think you do."
3. **SILENCE. COUNT THREE.** Do not fill it.
4. *Then* advance to contact slide
5. "I'm Anubhav. That's where to find me — and the thing I most want tonight is
   to hear where you'd draw the line. So: questions, arguments, war stories."
6. **Leave contact slide up for the whole Q&A**

---

## IF THE ROOM IS SILENT (5 sec, then go)

> "The question I get most is: why not just build this ourselves?"

Then: **You absolutely can — that's what the first half was, and it worked.**
The question was never whether it's possible. It's whether workflow execution
semantics is something you want your app team to own as infrastructure.
The signal isn't complexity. It's whether that code is still **growing**.

Follow-up if asked how to tell:
> "Run git log on that file for twelve months. Two piles: commits that changed
> business rules, commits that changed how it survives failure. If the second
> pile is bigger, you already know."

---

## IF SOMEONE IS HOSTILE — memorized, verbatim

> "Yeah — and the fact that Sidekiq *lets* you build all of that is a point in
> its favour. It's flexible enough that you can. The talk isn't that it can't.
> It's that at some point you should notice you did."

Agree instantly. Don't defend Temporal — you're not its lawyer.

---

## CUT LIST (say it out loud, don't silently rush)
1. Failure #4 (deploy/versioning) → one line
2. The "customers never email to say you charged half" joke
3. Demo scenario B (duplicate callback)
4. The Postgres paragraph near the end

**NEVER CUT:** program counter · ME→RUNTIME · the demo · determinism slide ·
the closing silence

---

## FACTS TO KEEP STRAIGHT
- Ruby SDK went GA **October 2025**
- Code verified against gem **1.6.0**
- Business logic **doesn't** move. **Recovery** moves. ← the scoreboard
- Replay: *"reconstructs state by replaying recorded history against your
  workflow code"* — NOT "re-runs from the top"
