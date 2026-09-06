# CUE SHEET — phone, scroll as you go

`▸n` = number of clicks on that slide. **Gates: 10:00 · 15:00 · 20:00**

---

**BEFORE SLIDE 1 — spoken, no slide**
Hands up if you travelled more than an hour? *(look)* More than two? *(laugh)*
"HSR on a Sunday, and you picked this over dinner. Thank you. I'll make it worth the auto fare."

**1 · Title** ▸0
Straight through.

**2 · Two questions** ▸1
Q1 Sidekiq in prod. *(look)* CLICK. Q2 job with a state machine. *(look)*
"Some of you put your hand up very fast." → "Keep that job in your head."

**3 · perform_async** ▸1
"Something happened in a request, we push it to a queue." CLICK → **"This is good code."**
No twist coming. Perham line. "Follow one process and see where it takes us."

**4 · Order fulfillment** ▸1
**SAY FIRST: "Half this room has built this. Watch which step you stopped at."** *(beat)*
CLICK. "Reality shows up. Five times."

**5 · Failure 1** ▸0
Worker dies. Sidekiq retries. Charges twice.
*[SACRIFICIAL JOKE — cut if behind]* customers never email to say you charged half.

**6 · Idempotent** ▸2
Guards. CLICK → nobody asked for charged_at / no PM ticket. CLICK → **"not info about the order, info about how far the job got."**
Right call. I'd do it again. First brick.

**7 · Idempotency key** ▸2 **NOT DROPPABLE**
"The actual answer isn't a transaction, the gateway isn't in your DB. It's an idempotency key. Send it with the charge, gateway dedupes. That's correct, you should do it."
CLICK → "A key you generate. Store. And scope. Per order? Per attempt? Per retry?"
CLICK → **"Another column. Another thing you own."**
*(Concede fast and mean it. This is the expert's answer, and it still lands on the pile.)*

**8 · Failure 2** ▸0
Two days. Thread, timeout, killed by next deploy (~11 min away). "sleep 2.days. Usually a joke. Usually."

**9 · Schedules itself** ▸1
"All of you have written this. Some of you this week."
**CONCEDE:** "And yes, you'd schedule one job for when you expect it, not poll hourly. That's better, I'd do that too. Either way the job is now two jobs, and where it resumes lives in a column."
CLICK → **that's a timer.** Built waiting from a scheduler and a queue.

**10 · PROGRAM COUNTER** ▸2 🔒**PROTECT**
Say it. **PAUSE.** CLICK → in your orders table, with an index on it. **PAUSE.**
CLICK → "Not saying the code got ugly. Saying we introduced a concept. Nobody decided to."

**11 · Failure 3** ▸1
**CONCEDE FIRST:** "Dedup is easy. Unique index, five lines, done. Not the interesting bit."
"The interesting bit is the callback that arrives BEFORE you commit the row." → `nil:NilClass` = national anthem. CLICK.

**12 · Failure 4** ▸1 ✂️**WEAKEST — CUT FIRST, NO REGRET**
Objection is correct: you add a new job class, you don't change args. Don't argue payload versioning.
If kept, 10 seconds only: "In-flight processes outlive the code that started them. However you handle that, you're handling it." CLICK. Move on.

**13 · Failure 5** ▸1
Cancel. Stop a process that isn't running. CLICK → compensation, "week after finance asks a calm question."

**14 · The reconciler** ▸2
Read the comment. CLICK → every company has this job. CLICK → **"git blame always says it was me."**
Deliver both as ONE joke, no pause between.

**15 · What we added** ▸0 🎯**BIGGEST LAUGH**
Read the pile. Counter reads **JUST × 7**. **STOP TALKING. COUNT THREE.**

**16 · Workflow Engine v1.0** ▸1
"Every one was a good decision." CLICK → "We didn't set out to build a workflow engine."
"Nobody's name on it. Approved on your phone."

**17 · 847 lines** ▸0
Let them read it. Move quickly, the big one just landed.

**18 · Job vs workflow** ▸2
Job = please do this. CLICK → workflow = make sure this completes. CLICK → spectrum, no alarm, Rubocop has no rule.

**19 · A workflow is what a job gradually turns into** ▸0 🔒
Say it SLOWLY. **NO JOKE AFTER. Let it sit.**

**20 · Yes, these exist** ▸2
"Some of you have been quietly furious." Gem for it, usually four, two unmaintained.
CLICK → each makes a step better. CLICK → **none changes who owns keeping it alive.**

**21 · What if the runtime owned it** ▸2
CLICK → not business logic, the machinery. CLICK → **durable execution.**

**22 · Several systems** ▸1
Temporal, DBOS, Restate, Inngest. CLICK → Ruby SDK GA last October.
"Not watching the Java people have a nice time through a window."

**23 · Three words** ▸3
Workflow. CLICK Activity. CLICK Worker. CLICK → "everything else is day two."

**24 · The code** ▸1
**"Don't look at how short it is. Line count is a cheap argument."**
CLICK → highlights `wait_condition`. Explain ONLY that line. Then move.

**25 · You already wrote all of this** ▸1
6 sec per row, point don't teach. Guards→history. Self-enqueue→wait_condition. Dedup→signal. Status col→where the code is.
CLICK → reconciler row, dash. *(beat)* **"There isn't a row for that one."**

**26 · Waiting became a language feature** ▸0
One line. Say it, move.

**27 · ME → RUNTIME** ▸3 🔒**PROTECT**
"Who owns keeping this alive?" CLICK → **"was: me"** ← POINT AT YOURSELF
CLICK → count off: my columns, my scheduler, my dedup table, my reconciler, my phone
CLICK → drop hand → **"Here: the runtime."**

**28 · Same process twice** ▸0 ⏱**15:00 GATE**
"Not running this live at 6pm on a Sunday. You're welcome."

**29 · Kill the worker** ▸2
Sidekiq: **it works — because I wrote the guards.** "...someone adds a fourth step. On a Friday."
CLICK → Temporal: no recovery code to show you. CLICK → different answer to who's responsible.

**30 · Callback twice** ▸2 ✂️cut if past 18:30
Dedup + HTTP-spec debate. CLICK → no-op. CLICK → "was it you, at 2am."

**31 · 48-hour wait** ▸3
CLICK test env skips time. CLICK I faked the clock. CLICK → **"fake clock to test my fake timer."**

**32 · Who owns what** ▸0
**Business logic doesn't move** ("otherwise they're doing a webinar"). **Recovery moves — that's what you're buying.**
Then seed: "activity touches the outside world, workflow decides what happens next."

**33 · What did we buy** ▸0 ⏱**20:00 GATE**
"That table made it look free. It is not."

**34 · Determinism** ▸1 🔒**NEVER CUT**
SAY EXACTLY: *"reconstructs state by replaying recorded history against your workflow code."*
CLICK → Time.now, Order.find are bugs. Matz/developer-happiness line. One joke max.

**35 · Rest of the bill** ▸5
CLICK runtime · CLICK debugging (binding.pry won't help) · CLICK versioning ("more honest ≠ less work") · CLICK org · CLICK trade

**36 · Where's your line** ▸1
That's a job → Sidekiq is CORRECT. "promo packet" line.
CLICK → might be a workflow. **✂️cut the Postgres paragraph if long.**

**37 · The abstraction line** ▸0 🔒
The thesis. Slowly.

**38 · THE LANDING** ▸2 🔒
"That job you thought of at the start." CLICK → "...person doesn't work there any more,"
CLICK → **Is this still a job?**
"I don't know, for your system. I think you do."
**SILENCE. COUNT THREE.**

**39 · Contact** ▸0
"I'm Anubhav. That's where to find me. What I most want tonight is to hear where you'd draw the line. Questions, arguments, war stories."
**LEAVE THIS UP FOR ALL OF Q&A.**

**40 · References** — do not present.

---

## IF Q&A IS SILENT (5 sec)
"The question I get most is: why not just build this ourselves?"
→ You absolutely can, that's what the first half was, and it worked. Question is whether workflow execution semantics is something you want your app team to own. **The signal isn't complexity, it's whether that code is still growing.**

## IF HOSTILE — verbatim
"The fact that Sidekiq *lets* you build all of that is a point in its favour. The talk isn't that it can't. It's that at some point you should notice you did."
