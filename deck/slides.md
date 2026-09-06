---
theme: default
title: Your Sidekiq Jobs Have Become a Workflow Engine
info: BRUG, 6 Sep 2026
class: text-center
transition: none
mdc: true
# No webfont fetch at runtime: venue wifi must not be able to change your
# typography mid-talk. Uses local system fonts only.
fonts:
  provider: none
  sans: Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif
  mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace
---

# Your Sidekiq Jobs Have Become a Workflow Engine

<div class="opacity-50 mt-4">BRUG · Sunday, 6 September 2026</div>

<!--
GATES: 10:00 realization · 15:00 demo starts · 20:00 demo ends
PROTECT: program counter (~7:15), ME→RUNTIME (~15:00), the demo.
OPENER (spoken, before the poll slide). They did NOT know the topic before
arriving, so do not joke about background jobs yet. Build rapport on the one
thing everyone here shares: getting to HSR on a Sunday.

  "Quick one before I start. Hands up if you travelled more than an hour
   to get here tonight."   [look at the hands]
  "More than two?"   [laugh]
  "Right. HSR on a Sunday evening, and you picked this over dinner.
   Thank you, genuinely. I'll try to make it worth the auto fare."   [LAUGH]

THEN the poll slide. LOOK at the hands both times.
-->

---
layout: center
---

# Two questions

<div class="text-2xl mt-8 space-y-6">

<div>1. Who runs Sidekiq in production?</div>

<div v-click>2. Who has a Sidekiq job with a <span class="font-bold">state machine</span> inside it?</div>

</div>

<!--
Wait for hands both times. Actually look.
"Some of you put your hand up VERY fast." [LAUGH]
"Keep that job in your head. We're going to go find it."
This poll is called back in the final slide — it is what makes the ending land.
-->

---
layout: center
---

```ruby
GenerateInvoiceJob.perform_async(invoice.id)
```

<div v-click class="text-center mt-10 text-2xl opacity-80">This is good code.</div>

<!--
No twist coming. Sidekiq is great, Mike Perham is a national treasure of a country
I don't live in. [LAUGH]
PREEMPT "this is a vendor pitch" — kill it in the first 90 seconds.
-->

---

# Order fulfillment

```ruby
class ProcessOrderJob
  include Sidekiq::Job

  def perform(order_id)
    order = Order.find(order_id)
    charge_payment(order)
    reserve_inventory(order)
    ship(order)
  end
end
```

<div v-click class="mt-6 opacity-70">Three steps. One job. Nobody argues with it in review.</div>

<StatusEnum :stage="1" />

<!--
SAY FIRST: "Half this room has built this. Watch which step you stopped at."
Then pause half a beat. This converts experts from bored into self-auditing.
Then: "Reality shows up. Five times. Like it does."
-->

---
layout: center
class: text-center
---

# Failure 1

## Payment succeeds. Worker dies.

<!--
Box recycled, deploy, OOM, someone ran a migration on a Friday.
Sidekiq retries. perform runs from the top. Charges the customer twice.
[LAUGH — SACRIFICIAL] customers never email to say you charged them half.
DROP THIS JOKE FIRST if running long.
-->

---

# Idempotent: safe to run twice

```ruby {3-5}
def perform(order_id)
  order = Order.find(order_id)
  charge_payment(order)    unless order.charged?
  reserve_inventory(order) unless order.reserved?
  ship(order)              unless order.shipped?
end
```

<div v-click class="mt-6">

Nobody asked for `charged_at`.

</div>

<div v-click class="mt-4 text-xl">

That's not information about the order.
That's information about **how far along the job got**.

</div>

<Just :n="1" />
<StatusEnum :stage="2" />

<!--
"No PM has ever written a ticket that says: as a user I want a boolean
indicating how far through a Sidekiq job I got." [LAUGH]
Then: it was the right call, I'd do it again tomorrow. But it's the first brick.
-->

---
layout: center
---

## The real fix is an idempotency key

<div v-click class="mt-8 text-xl opacity-80">

Generate it. Store it. Decide what it's scoped to.

</div>

<div v-click class="mt-6 text-xl">

Another column. Another thing you own.

</div>

<Just :n="1" />
<StatusEnum :stage="2" />

<!--
*** THIS REPLACED A STRAWMAN. Do not go back to "just use a transaction" —
a room of Rails devs will say nobody would do that anyway, and then the whole
first half looks rigged. Steelman it instead. ***

SAY:
  "Now, the actual answer here isn't a transaction. You can't wrap a call to a
   payment gateway in one anyway, because the gateway isn't in your database.
   The real answer is an idempotency key. You generate a key, you send it with
   the charge, the gateway dedupes it for you. That is correct, and you should
   do it."
  [CLICK]
  "And it's a key you generate. Store. And decide the scope of. Is it per order?
   Per attempt? Per retry?"
  [CLICK]
  "Another column. Another thing you own."

This is now STRONGER than the version it replaced, because you conceded the
expert's point and it still ends up on the pile. Concede fast and mean it.
-->

---
layout: center
class: text-center
---

# Failure 2

## The warehouse takes two days.

<!--
A worker can't sit for two days. Thread, timeout, killed by the next deploy —
which at most companies is about eleven minutes away. [LAUGH]
"Somebody always suggests `sleep 2.days` at this point. Usually as a joke. Usually."
-->

---

# A job that schedules itself

```ruby {6}
class CheckWarehouseJob
  def perform(order_id)
    order = Order.find(order_id)
    return ShipOrderJob.perform_async(order_id) if warehouse_ready?(order)

    CheckWarehouseJob.perform_in(1.hour, order_id)   # 🤞
  end
end
```

<div v-click class="mt-6 text-xl">

That's a timer.

We had no way to wait, so we built waiting out of a scheduler and a queue.

</div>

<Just :n="2" />
<StatusEnum :stage="3" />

<!--
"All of you have written this. Some of you wrote it this week. Some of you are
looking at your laptop right now." [LAUGH]

CONCEDE IMMEDIATELY (someone is already thinking it):
  "And yes, you'd schedule one job for when you actually expect it, not poll
   every hour. That's better. I'd do that too."
  "Either way, the job is now two jobs. And where it resumes lives outside
   the code, in a column."

That concession is what makes the program-counter line land as an observation
instead of a setup. Do NOT defend the polling version.
-->

---
layout: center
class: text-center
---

# It's a program counter.

<div v-click class="text-2xl mt-6 opacity-80">In your orders table. With an index on it.</div>

<div v-click class="mt-12 text-xl max-w-2xl mx-auto opacity-90">

I'm not saying the code got ugly. The code is fine.

I'm saying we **introduced a concept**, and nobody decided to.

</div>

<Just :n="2" />
<StatusEnum :stage="3" />

<!--
*** PROTECT — CONCEPTUAL PEAK OF THE FIRST HALF. DO NOT COMPRESS. ***
Say "program counter" → PAUSE → the reframe → PAUSE again.
Not an aesthetic argument (dismissible). A conceptual one (isn't).
This is what makes the realization at 9:30 feel inevitable rather than asserted.
-->

---
layout: center
class: text-center
---

# Failure 3

## The warehouse sends a callback instead.

<div v-click class="mt-8 opacity-70">Token. Dedup table. Race on commit.</div>

<Just :n="3" />

<!--
CONCEDE THE EASY PART FIRST:
  "Dedup is easy. Unique index on the token, five lines, done. That's not the
   interesting bit."
  "The interesting bit is the callback that arrives BEFORE you've committed
   the row."

THEN: "...and you get `undefined method for nil:NilClass`, which as we all know
is the national anthem of this ecosystem." [LAUGH]
Fix it with a lock, or a retry, or a `sleep 0.5` you tell nobody about.

Never imply dedup is hard. The room knows it isn't, and claiming otherwise
costs you the next two minutes.
-->

---
layout: center
class: text-center
---

# Failure 4

## We deploy mid-flight.

<div v-click class="mt-8 font-mono text-sm opacity-70">

\# TODO: remove after migration, Mar 2024

</div>

<Just :n="4" />

<!--
*** WEAKEST OF THE FIVE. CUT THIS FIRST, AND WITHOUT REGRET. ***
The objection is correct and someone will make it: you never change job args
incompatibly, you add a new job class. Standard practice, and it works.

IF YOU KEEP IT, do not argue about payload versioning. Say the one thing that
is unarguably true and move on in ten seconds:
  "In-flight processes outlive the code that started them. However you handle
   that, you are handling it."

Then go straight to failure five. Do not linger here.
-->

---
layout: center
class: text-center
---

# Failure 5

## The customer cancels.

<div v-click class="mt-8 opacity-70">

Compensation: the undo you write yourself.

</div>

<Just :n="5" />

<!--
Stop a process that isn't running — it's a row in Redis with a timestamp.
"...usually the week after someone from finance asks a very calm question." [LAUGH]
-->

---

# And then someone writes this

```ruby
# Runs every 10 min. Do NOT delete.
# Ask Anubhav before changing this.
# (Anubhav doesn't work here any more.)
class ReconcileStuckOrdersJob
```

<div v-click class="mt-8 text-xl">

Every company I've worked at has this job.

</div>

<div v-click class="mt-2 text-xl">

And `git blame` always says it was me.

</div>

<Just :n="6" />
<StatusEnum :stage="4" />

<!--
[LAUGH] on the comment, [LAUGH] on git blame. Naming YOURSELF is what makes
the two land as one joke: the comment names you, then two lines later git blame
names you too. Also removes any chance of a real colleague reading it as them.
git blame line is LOAD-BEARING: it puts you inside the joke, not above it.
Without it the whole bit reads as mocking their codebase. NEVER CUT IT.
This comment returns in the final slide.
-->

---

# <span v-mark.circle.orange="1">What we added</span>

<div class="grid grid-cols-2 gap-12 mt-8 text-lg">

<div>

**Sidekiq**
- retries
- scheduling
- queues

</div>

<div>

**Rails / Postgres**
- state columns
- idempotency guards
- callback dedup
- polling
- payload versioning
- compensation
- reconciliation

</div>

</div>

<Just :n="7" big />

<!--
*** THE PAYOFF. BIGGEST LAUGH IN THE TALK. DO NOT TALK OVER IT. Count three beats. ***
The counter has been in that corner, unremarked, for seven minutes.
NEXT SLIDE flips the title.
-->

---
layout: center
class: text-center
---

# Workflow Engine v1.0

<div v-click class="mt-10 text-xl max-w-2xl mx-auto">

We didn't set out to build a workflow engine.

We just kept solving the next requirement.

</div>

<Just :n="7" big />

<!--
Every one of those was a good decision. I'd defend all of them in review.
"Nobody's name is on it. There was never a ticket that said build workflow engine.
It arrived one PR at a time over eighteen months, and every one was small enough
to approve on your phone." [LAUGH]
-->

---
layout: center
---

```ruby
class DefinitelyNotAWorkflow < ApplicationJob
  # 847 lines
end
```

<!--
[LAUGH]. Short slide. Move on quickly — don't milk it, the big one just landed.
-->

---

# Job vs workflow

<div class="grid grid-cols-2 gap-12 mt-8">

<div>

### A job

> "Please do this."

Send the email. Resize the image. Sync the record.

Short. Discrete. Retry as a unit.

</div>

<div v-click>

### A workflow

> "Make sure this eventually completes."

Onboarding. Fulfillment. Payment lifecycle.

State. Time. Events. Compensation.

</div>

</div>

<div v-click class="mt-10 text-center opacity-80">

It's a spectrum. Nothing happens when you cross it. Rubocop has no rule for this.

</div>

<!--
[LAUGH] on the Rubocop line.
Then: "which is exactly why you end up on the wrong side without noticing."
-->

---
layout: center
class: text-center
---

# A workflow is what a job gradually turns into.

<!--
*** BEGINNERS' TAKEAWAY. The sentence they repeat to a colleague on Monday. ***
Say it slowly. NO JOKE AFTER THIS. Let the silence do the punctuation.
-->

---

# Yes, these exist

<div class="text-xl mt-8 font-mono opacity-90 leading-relaxed">

Sidekiq Pro Batches · acidic_job · Gush<br>
AASM · Statesman · GoodJob

</div>

<div v-click class="mt-10 text-xl">

Each one makes **a step** better.

</div>

<div v-click class="mt-4 text-xl">

None of them fundamentally changes who owns **keeping the process alive**.

</div>

<div class="absolute bottom-6 left-0 right-0 text-center text-xs opacity-40">

Batches (Sidekiq Pro) · acidic_job, @fractaledmind · Gush, Chaps · AASM · Statesman, GoCardless · GoodJob, @bensheldon

</div>

<!--
PREEMPT — THE #1 Q&A AMBUSH. Placement is load-bearing: this comes BEFORE
Temporal appears. Said after, it sounds defensive.
"There is always a gem for it, and usually four, and two are unmaintained." [LAUGH]
"If you're not using them, some of you should leave now. I won't be offended." [LAUGH]
Still your app, your Postgres, your reconciler, your phone at 3am.
-->

---
layout: center
class: text-center
---

# What if keeping the process alive was the runtime's job instead of ours?

<div v-click class="mt-10 text-xl opacity-70">

Not the business logic. The machinery.

</div>

<div v-click class="mt-8 text-2xl font-bold">

Durable execution

</div>

---
layout: center
---

# Several systems do this

<div class="text-2xl mt-8 font-mono opacity-80">

Temporal · DBOS · Restate · Inngest

</div>

<div v-click class="mt-10 text-lg">

I picked one, for a boring reason that matters to this room:

**the Ruby SDK went GA last October.**

</div>

<div class="absolute bottom-6 left-0 right-0 text-center text-xs opacity-40">

GA announced 1 Oct 2025 · temporal.io/changelog/ruby-sdk-generally-available

</div>

<!--
"Which means for once we are not standing outside the window watching the
Java people have a nice time." [LAUGH]
Not comparing them. One case study, chosen for Ruby relevance.
-->

---

# Three words

<div class="mt-10 space-y-8 text-xl">

<div><span class="font-bold">Workflow</span>: decides what happens next. Your orchestration.</div>

<div v-click><span class="font-bold">Activity</span>: touches the outside world. Charge the card.</div>

<div v-click><span class="font-bold">Worker</span>: the process you run that executes both.</div>

</div>

<div v-click class="mt-10 opacity-60">Everything else is day two.</div>

<!--
THREE. NOT SEVEN. Signals / replay / history appear later, in context, where
they're visible on screen. Dumping seven nouns here is where beginners leave.
-->

---

# The same process

```ruby {all|6}
class OrderWorkflow < Temporalio::Workflow::Definition
  def execute(order_id)
    Temporalio::Workflow.execute_activity(ChargePayment, order_id)
    Temporalio::Workflow.execute_activity(ReserveInventory, order_id)

    Temporalio::Workflow.wait_condition { @warehouse_ready }

    Temporalio::Workflow.execute_activity(ShipOrder, order_id)
  end

  workflow_signal
  def warehouse_confirmed = @warehouse_ready = true
end
```

<!--
CAREFUL — this is the slide where a talk becomes an ad.
SAY IT: "Don't look at how short it is. Line count is a cheap argument and
I refuse to make it." (PREEMPT: "that's just my code but shorter")
Second click highlights wait_condition: that's the two-day wait. No scheduler,
no re-enqueue, no status column. Doesn't hold a thread.
SYNTAX VERIFIED against temporalio 1.6.0 on this machine: class compiles,
signal registers as "warehouse_confirmed". Workflow.now / Workflow.random on the
determinism slide also exist.
ONE CAVEAT if challenged: this compiles but wouldn't RUN as-is — Temporal requires
a start_to_close_timeout (or schedule_to_close_timeout) on each activity. Omitted
here for slide legibility. If someone calls it out, that's a gift: "correct, and
the fact that the runtime makes me declare a timeout per activity is exactly the
kind of thing you don't get for free with perform_async."

-->

---

# You already wrote all of this

| What you built in the first half | Here |
|---|---|
| `order.charged?` guards | history records the activity completed |
| `CheckWarehouseJob` re-enqueueing itself | `wait_condition` |
| callback token + dedup table | `signal` |
| status column as program counter | the workflow's own position in the code |

<div v-click class="mt-8 text-xl">

| `ReconcileStuckOrdersJob` | — |
|---|---|

</div>

<!--
*** THIS SLIDE IS THE BRIDGE. It is more persuasive than the code slide. ***
The code alone is illegible to most of this room in 90 seconds. This decodes it
by mapping every line back to something THEY wrote in the first half — so it
lands as recognition, not as a new API.

Walk the rows briskly, ~6 seconds each. Don't teach the API, just point:
  "The guards you added — the runtime already knows, it's in the history."
  "The job that re-enqueued itself — that's the one line, wait_condition."
  "The dedup table — that's a signal. Second one arrives, workflow's moved on."
  "The status column doing double duty as a program counter — it's just where
   the code is."

THEN CLICK. The reconciler row appears with a dash.
Say nothing for a beat. Then: "There isn't a row for that one."

TIMING: this slide costs ~30s net. You get most of it back because you no
longer need to explain the code slide in detail — point at wait_condition, say
the one line, and come here.
-->

---
layout: center
class: text-center
---

# Waiting became a language feature.

---
layout: center
class: text-center
---

# Who owns keeping this process alive?

<div v-click class="mt-12 text-3xl">

The first half of this talk: **me**.

</div>

<div v-click class="mt-4 text-lg opacity-70">

My columns. My scheduler. My dedup table. My reconciler. My phone.

</div>

<div v-click class="mt-8 text-3xl">

Here: **the runtime**.

</div>

<!--
*** PROTECT — EMOTIONAL CENTRE OF THE SECOND HALF. ***
STAGING: point at yourself on "me" — small, not theatrical. Count the list off.
Drop the hand for "the runtime."
The room gets ME → RUNTIME. That's the whole talk in two words, delivered
physically instead of asserted.
Deliver "me" with ownership, not confession: you were competent and it still
accumulated. That is the argument.
PREEMPT "you designed the example to flatter Temporal" — a skeptic can argue
line counts forever; nobody can argue the reconciler wasn't in your repo.
-->

---
layout: center
class: text-center
---

# The same process, twice

<div class="mt-8 opacity-70">Same requirements. Same five failures. Both broken on purpose.</div>

<!--
*** DEMO GATE — YOU SHOULD BE HERE AT 15:00. ***
*** THIS IS THE CENTRE OF GRAVITY. DO NOT COMPRESS IT. ***
If behind, you already cut failure #4. If still behind, drop scenario B — but
never rush what's on screen.
"I'm not running this live at 6pm on a Sunday. You're welcome." [LAUGH]
-->

---

# Kill the worker, right after payment

<div class="grid grid-cols-2 gap-10 mt-8">

<div>

### Sidekiq

Retries. Hits my idempotency guards.

**It works.**

Because I wrote the guards.

</div>

<div v-click>

### Temporal

Another worker continues after the payment activity.

**There is no recovery code to show you.**

</div>

</div>

<div v-click class="mt-10 text-center text-xl">

Same outcome. Different answer to *who is responsible for it.*

</div>

<!--
"...and I stay responsible for it every time someone adds a fourth step.
Which they will. On a Friday." [LAUGH]
-->

---

# The callback fires twice

<div class="grid grid-cols-2 gap-10 mt-8">

<div>

### Sidekiq

Dedup table. Unique index.

A philosophical debate about what "twice" means.

</div>

<div v-click>

### Temporal

Workflow is already past that wait.

Second signal is a no-op.

</div>

</div>

<div v-click class="mt-10 text-center text-xl">

Not magic. Somebody wrote that logic.
The question is whether it was **you**, at 2am.

</div>

<!--
"...a debate that will happen in a PR thread and will involve at least one
person quoting the HTTP spec." [LAUGH]
*** CUT THIS SLIDE if you reach it after 18:30. ***
-->

---
layout: center
class: text-center
---

# The 48-hour wait

<div v-click class="mt-8 text-xl">

Temporal's test environment skips time.

</div>

<div v-click class="mt-4 text-xl">

On the Sidekiq side I faked the clock and fired the cron by hand.

</div>

<div v-click class="mt-10 text-2xl font-bold">

I built a fake clock to test my fake timer.

</div>

<!--
[LAUGH] on the last line — funny AND technically the point.
Waiting is either a thing the runtime understands, or a thing you simulate —
and then have to simulate a second time in order to test.
-->

---

# Who owns what

| Concern | Rails + Sidekiq | Durable runtime |
|---|---|---|
| Retry | Job system | Runtime |
| Timer | Scheduler + job | Runtime |
| Workflow state | Your DB | Runtime |
| External event | Callback + dedup | Signal |
| Recovery | **You** | **Runtime** |
| Orchestration | You | Workflow |
| **Business logic** | **You** | **You** |
| Side effects | You | Activities |

<!--
Two rows matter.
BUSINESS LOGIC DOESN'T MOVE — "and anyone who tells you otherwise is doing
a webinar." [LAUGH]
RECOVERY MOVES. That's the row you're buying.
Then seed the beginner question so nobody has to raise a hand:
"Activity touches the outside world. Workflow decides what happens next."
-->

---
layout: center
class: text-center
---

# Okay. What did we just buy?

<!--
*** OFF THE DEMO BY 20:00. ***
That table made it look free. It is not.
-->

---

# Determinism

```ruby
# Inside workflow code. Replay breaks all of these
Time.now
SecureRandom.uuid
rand(100)
Order.find(id)             # any IO at all

# What you write instead
Temporalio::Workflow.now
Temporalio::Workflow.random.uuid
Temporalio::Workflow.execute_activity(FetchOrder, id)
```

<div v-click class="mt-6 text-lg">

`Time.now`. `Order.find`. The two most ordinary things in Rails. Inside a workflow, they're bugs.

</div>

<!--
SAY THE REPLAY SENTENCE EXACTLY:
"The runtime reconstructs the workflow's state by replaying its recorded history
against your workflow code — so your code has to produce the same decisions
given the same history, every time."
The loose version ("re-runs from the top") is memorable and slightly wrong;
people in this room will go implement this and carry that model.
"Matz optimised Ruby for developer happiness. This is the one corner optimised
for a distributed systems paper." [LAUGH — one joke max here, don't undercut it]
*** NEVER CUT THIS SLIDE. It's what makes the trade-off credible. ***
-->

---

# The rest of the bill

<div class="space-y-6 mt-8 text-lg">

<div v-click>**Another runtime.** Not Rails, Postgres, Redis any more. Someone operates this.</div>

<div v-click>**Debugging changes shape.** Not a stack trace. An execution history.</div>

<div v-click>**Versioning becomes first-class.** Old executions in flight when you deploy.</div>

<div v-click>**Your organisation has one more thing it must understand.** Every hire. Every incident.</div>

</div>

<div v-click class="mt-10 text-xl">

Reduces *application* complexity. Increases *system* complexity. That's a real trade.

</div>

<!--
"...and binding.pry is not going to help you." [LAUGH]
"'More honest' and 'less work' are different things." [LAUGH]
Know which side of the trade you're on when you make it.
-->

---

# Where's your line?

<div class="grid grid-cols-2 gap-10 mt-8 text-lg">

<div>

### That's a job

- short
- independent
- stateless
- retryable as a unit
- fire-and-forget

</div>

<div v-click>

### That might be a workflow

- multi-step
- long-running
- stateful
- waits on events or humans
- needs compensation
- **keeps accumulating orchestration code**

</div>

</div>

<!--
Sidekiq isn't just adequate here, it's CORRECT. Adding a runtime would be making
your life worse on purpose — "and there's a word for adding distributed systems
you don't need, and it's usually on someone's promo packet." [LAUGH]
Postgres is extremely good. Owning it is a real answer.
*** If long, CUT THE POSTGRES PARAGRAPH — never the callback on the next slides. ***
-->

---
layout: center
class: text-center
---

# An abstraction is useful right up until you start implementing the abstraction it was supposed to give you.

<!--
*** EXPERTS' TAKEAWAY. The thesis. ***
Sidekiq gives you a job abstraction. It's a great abstraction.
But if your app implements state, waiting, orchestration, recovery, timers,
events — whatever you're holding stopped being a job a while ago.
-->

---
layout: center
class: text-center
---

<div class="text-xl opacity-80">

That job you thought of when I asked at the start.

</div>

<div v-click class="text-xl opacity-80 mt-4">

If there's a comment on it with someone's name, and that person doesn't work there any more,

</div>

<div v-click class="mt-16 text-5xl font-bold">

Is that still a job?

</div>

<!--
Reconciler callback — UNDERPLAY IT. Dry nod, not a punchline. The argument is already
won. You want "oh god, that's my codebase", NOT "haha legacy code am I right."
The second one makes you the guy laughing at their repo and costs you the ending.
Then the final question. THEN SILENCE. No joke. Let them answer it themselves.
"I don't know for your system. I think you do. Thank you."
-->

---
layout: center
class: text-center
---

<div class="text-2xl opacity-60">So, where would you draw the line?</div>

<div class="mt-12 text-4xl font-bold">Anubhav Jain</div>

<div class="mt-10 font-mono text-lg space-y-1 opacity-90">

<div>x.com/anewbhav</div>
<div>linkedin.com/in/anew-bhav</div>

</div>

<div class="mt-10 text-base opacity-60">

Slides: anewbhav.dev/talks/sidekiq-workflow-engine

</div>

<!--
*** DO NOT ADVANCE TO THIS SLIDE UNTIL THE SILENCE HAS DONE ITS WORK. ***
Sequence:
  1. "Is that still a job?" on screen.
  2. "I don't know for your system. I think you do."
  3. SILENCE. Count three. Let them sit in it.
  4. THEN advance. "I'm Anubhav. That's where to find me — and honestly the
     thing I most want out of tonight is to hear where you'd draw the line.
     So: questions, arguments, war stories."
  5. LEAVE THIS SLIDE UP FOR THE ENTIRE Q&A. It's how people photograph it,
     and a blank/black screen during Q&A wastes five minutes of exposure.

"Where would you draw the line?" at the top is doing real work — it opens Q&A
with an invitation to disagree rather than "any questions?" (which gets silence
in a room of 200). If nobody speaks in 5 seconds, take your own prepared one:
"The question I get most is why not just build this ourselves —" and answer it.

FILL IN BEFORE PRESENTING: role/company, three handles, short link.
Kill any line you don't want on a projector — an empty div is fine.
Deliberately no personal email: don't put your inbox on a screen in front of
200 people. Handles are enough.
-->

---
layout: default
---

# References & credits

<div class="text-sm space-y-4 mt-6">

<div>

**Temporal**: temporal.io · [Ruby SDK GA announcement, 1 Oct 2025](https://temporal.io/changelog/ruby-sdk-generally-available) · [github.com/temporalio/sdk-ruby](https://github.com/temporalio/sdk-ruby) · [docs.temporal.io/develop/ruby](https://docs.temporal.io/develop/ruby)
Code on these slides verified against gem `temporalio` 1.6.0.

</div>

<div>

**Sidekiq**: Mike Perham / Contributed Systems · [sidekiq.org](https://sidekiq.org) · [Batches (Pro)](https://github.com/sidekiq/sidekiq/wiki/Batches)

</div>

<div>

**Ruby workflow / job libraries named in this talk**
[acidic_job](https://github.com/fractaledmind/acidic_job) · [Gush](https://github.com/chaps-io/gush) · [AASM](https://github.com/aasm/aasm) · [Statesman](https://github.com/gocardless/statesman) · [GoodJob](https://github.com/bensheldon/good_job)

</div>

<div>

**Other durable execution runtimes**: [DBOS](https://dbos.dev) · [Restate](https://restate.dev) · [Inngest](https://inngest.com)

</div>

<div class="opacity-60 pt-2">

All example code is my own. The order-fulfillment scenario is illustrative, not
taken from any employer's system. No affiliation with Temporal or any project listed.

</div>

</div>

<!--
APPENDIX — do not present this slide. It exists so the published deck carries
its sources.
If you want to acknowledge it out loud, one line on the contact slide is enough:
"Links and credits are on the last slide of the deck."
All 13 URLs verified 200 on 6 Sep 2026.
-->
