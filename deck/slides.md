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
GATES 10:00 realization · 15:00 demo · 20:00 demo ends

SPOKEN, before you touch the slides:

"Quick one before I start. Hands up if you travelled more than
 an hour to get here tonight."
   [LOOK at the hands]
"More than two?"
   [LAUGH]
"Right. HSR on a Sunday evening, and you picked this over dinner.
 Thank you, genuinely. I'll try to make it worth the auto fare."
   [LAUGH]

Do NOT joke about background jobs yet. They don't know the topic.
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
"Two questions before I start. Hands up."

"One. Who runs Sidekiq in production?"
   [LOOK. Wait for it.]
"Right. Most of the room."

▸ CLICK

"Two, and this is the real one. Who has a Sidekiq job with a
 state machine inside it?"
   [LOOK. Fewer hands, more laughing.]
"Some of you put your hand up very fast."
   [LAUGH]

"Keep that job in your head. We're going to go find it."

^ This poll is called back in the final slide.
-->
---
layout: center
---

```ruby
GenerateInvoiceJob.perform_async(invoice.id)
```

<div v-click class="text-center mt-10 text-2xl opacity-80">This is good code.</div>

<!--
"Let me start somewhere completely uncontroversial."

"That's it. Something happened in a request, we don't want to do
 it in the request, so we push it to a queue."

▸ CLICK

"This is good code."
   [BEAT]

"I want to be clear about that, because the title has Sidekiq in
 it, and you're all waiting for the part where I tell you it's bad."

"That part isn't coming. There's no twist. Sidekiq is great, and
 Mike Perham is a national treasure of a country I don't live in."
   [LAUGH]

"If your problem fits on that one line, write that line and go home."

"I'm not going to manufacture a problem so I can sell you a
 solution. We're going to follow one process. One. And see where
 it takes us."
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
"The process is order fulfillment. And before I start —"

"HALF THIS ROOM HAS BUILT THIS. WATCH WHICH STEP YOU STOPPED AT."
   [BEAT. This turns the experts from bored into self-auditing.]

"Version one. Charge the payment, reserve the inventory, ship it.
 Three steps, one job, top to bottom."

▸ CLICK

"Genuinely fine. Nobody argues with it in review."

"Then reality shows up. Five times. Like it does."
-->
---
layout: center
class: text-center
---

# Failure 1

## Payment succeeds. Worker dies.

<!--
"Failure one. Payment succeeds. The worker dies."

"Box gets recycled. Deploy goes out. The OOM killer. Someone ran
 a migration on a Friday. Doesn't matter which."

"Sidekiq does the correct thing. It retries. So perform runs
 again, from the top. And charges the customer a second time."

"Now, the customer notices this. Customers are extremely good at
 noticing this. They have never once emailed to say, you charged
 me half as much as I expected."
   [LAUGH]
   *** ✂ SACRIFICIAL — the joke to drop first if you're running long. ***
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
"So we make it idempotent. Idempotent meaning safe to run twice."

"And to be safe to run twice, the job has to know what it already
 did. Which means it has to write down what it already did."

"So we add three columns, and guard each step on its column."

▸ CLICK

"Nobody in the business asked for charged_at. No product manager
 has ever written a ticket that says: as a user, I want a boolean
 indicating how far through a Sidekiq job I got."
   [LAUGH]

▸ CLICK

"That is not information about the order."
   [BEAT]
"That is information about how far along the job got."

"We persisted execution state into our domain model. And it was
 the right call. I'd do it again tomorrow. But it's the first brick."
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
*** CONCEDE FAST, AND MEAN IT. THIS IS THE EXPERT'S OWN ANSWER. ***

"Now, the actual answer here isn't a transaction. You can't wrap
 a call to a payment gateway in one anyway, because the gateway
 isn't in your database."

"The real answer is an idempotency key. You generate a key, you
 send it with the charge, and the gateway dedupes it for you.
 That is correct, and you should do it."

▸ CLICK

"And it's a key you generate. Store. And decide the scope of.
 Is it per order? Per attempt? Per retry?"

▸ CLICK

"Another column. Another thing you own."

*** NOT DROPPABLE. Never go back to the "you can't use a
    transaction" strawman — the room would be right to reject it. ***
-->
---
layout: center
class: text-center
---

# Failure 2

## The warehouse takes two days.

<!--
"Failure two. The warehouse takes two days to confirm."

"A worker cannot sit there for two days. It's a thread. It has a
 timeout. And it will be killed by the next deploy, which at most
 companies is about eleven minutes away."
   [LAUGH]

"Somebody always suggests sleep two days at this point. Usually
 as a joke."
   [BEAT]
"Usually."
   [LAUGH]
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
"So we split the job. If the warehouse is ready, ship it.
 Otherwise, schedule myself again in an hour."

"A job that schedules itself. All of you have written this. Some
 of you wrote it this week. Some of you are looking at your
 laptop right now."
   [LAUGH]

*** CONCEDE IMMEDIATELY — someone is already thinking it: ***
"And yes, you'd schedule one job for when you actually expect it,
 not poll every hour. That's better. I'd do that too."
"Either way, the job is now two jobs. And where it resumes lives
 outside the code, in a column."

▸ CLICK

"That's a timer. We had no way to wait, so we built waiting out
 of the parts we had. A scheduler, and a queue."
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
*** 🔒 PROTECT — CONCEPTUAL PEAK OF THE FIRST HALF. SLOW DOWN. ***

"The status column isn't describing the order any more. It's
 telling the next job where to resume."

"It's a program counter."
   [BEAT — let it sit]

▸ CLICK

"In your orders table. With an index on it."
   [BEAT]

▸ CLICK

"And I want to be precise about what I'm claiming. I'm not saying
 our Rails code got ugly. The code is fine. The code is nice."

"I'm saying we introduced a concept."
   [BEAT]
"And nobody decided to."

You index it so a cron can find crashed programs. That's the tell.
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
*** CONCEDE THE EASY PART FIRST: ***

"Failure three. The warehouse sends a callback instead. Better."

"Dedup is easy. Unique index on the token, five lines, done.
 That's not the interesting bit."

"The interesting bit is the callback that arrives BEFORE you've
 committed the row."

"And then you get: undefined method for nil, NilClass. Which, as
 we all know, is the national anthem of this ecosystem."
   [LAUGH]

▸ CLICK

"And you fix it with a lock. Or a retry. Or a sleep zero point
 five that you tell nobody about."

Never imply dedup is hard. The room knows it isn't.
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
*** ✂ WEAKEST OF THE FIVE. CUT THIS FIRST, WITHOUT REGRET. ***
The objection is correct: you add a new job class, you don't
change args incompatibly. Do NOT argue payload versioning.

IF KEEPING IT — ten seconds, one unarguable line:

"Failure four. We deploy mid-flight. There are orders in the
 queue right now, halfway through."

▸ CLICK

"In-flight processes outlive the code that started them. However
 you handle that, you are handling it."

Then go straight to failure five. Do not linger.
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
"Failure five. The customer cancels. After payment, before
 shipping."

"Now you have to stop a process that isn't running. It's a row in
 Redis with a timestamp on it. And you have to undo a charge."

▸ CLICK

"That's compensation. The undo you write yourself. Usually the
 week after someone from finance asks a very calm question."
   [LAUGH]
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
"And somewhere in here, someone writes this."
   [Let them read it. Don't read it aloud.]

▸ CLICK

"Every company I've worked at has this job. It always has that
 comment."

▸ CLICK

"And git blame always says it was me."
   [LAUGH]

DELIVER BOTH AS ONE JOKE. No pause between them — the second
line is the reveal. This is what puts you INSIDE the joke rather
than above it. Never cut the git blame line.

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
*** 🎯 THE BIGGEST LAUGH IN THE TALK. ***

"So let's put it on one slide. Not the business logic. Just the
 machinery we added to keep the process alive."

[Read the pile briskly. The counter in the corner now reads
 JUST × 7 — it's been sitting there unremarked for seven minutes.]

   [STOP TALKING. COUNT THREE. DO NOT TALK OVER IT.]

Do not point at the counter. Do not explain the gag.
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
"Every one of those was a good decision. I'd defend all of them
 in code review. None of them is wrong."

"But look at the shape. State. Timers. Retries. External events.
 Recovery. Compensation."
   [BEAT]
"That is not a job any more."

▸ CLICK

"We didn't set out to build a workflow engine. We just kept
 solving the next requirement."

"And nobody's name is on it. There was never a ticket that said
 build workflow engine. It arrived one pull request at a time
 over eighteen months, and every one of them was small enough to
 approve on your phone."
   [LAUGH]
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
[Let them read it. Say almost nothing.]

"It usually has a class name too."
   [LAUGH]

Move quickly. The big one just landed — don't try to top it.
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
"So let me draw the line that actually matters."

"A job says: please do this. Send the email. Resize the image.
 Sync the record. Short, discrete, retry it as a unit."

▸ CLICK

"A workflow says: make sure this eventually completes.
 Onboarding. Fulfillment. Payment lifecycle. Those have state,
 time, events, compensation."

▸ CLICK

"And it's a spectrum, not two boxes. Nothing happens when you
 cross it. No alarm goes off. Nobody gets paged. Rubocop does not
 have a rule for this."
   [LAUGH]

"Which is exactly why you end up on the wrong side of it without
 noticing."
-->
---
layout: center
class: text-center
---

# A workflow is what a job gradually turns into.

<!--
*** 🔒 THE BEGINNERS' TAKEAWAY — the sentence they repeat on Monday. ***

"A workflow is what a job gradually turns into."

SAY IT SLOWLY.
   [BEAT]
NO JOKE AFTER THIS. Silence is the punctuation.
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
*** PREEMPT — THE #1 Q&A AMBUSH. MUST COME BEFORE TEMPORAL. ***

"Now. Some of you have been quietly furious for about five
 minutes, going: yes, and that's why Sidekiq Pro has Batches."

"You're right. Let me put them all on the screen, because I'm not
 building a strawman. And this is Ruby — there is always a gem
 for it. Usually four. And two are unmaintained."
   [LAUGH]

▸ CLICK

"These are good. Batches gives you fan-out and callbacks. Acidic
 job gives you real step-level idempotency. Statesman gives you
 an auditable state machine."

"If you're not using them, some of you should leave now and go
 use them. I won't be offended."
   [LAUGH]

"But notice what they do. Each one makes a step better."

▸ CLICK

"None of them fundamentally changes who owns keeping the process
 alive. It's still your app. Your Postgres. Your reconciler.
 Your phone at three a.m."

"That's not a criticism. That's the question of this talk."
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

<!--
"So here's the question."

"What if keeping the process alive was the runtime's job instead
 of ours?"

▸ CLICK

"Not the business logic. The machinery. State, timers, retries,
 resumption, history."

▸ CLICK

"That idea has a name. Durable execution."

"You write the process as ordinary sequential code. And when the
 machine running it dies, the process doesn't."
-->
---
layout: center
---

# Several systems do this

<div class="text-2xl mt-8 font-mono opacity-80">

Temporal · DBOS · Restate · Inngest

</div>

<div v-click="1" class="mt-10 text-lg">

I picked one, for a boring reason that matters to this room:

**the Ruby SDK went GA last October.**

</div>

<div v-click="1" class="absolute bottom-6 left-0 right-0 text-center text-xs opacity-40">

GA announced 1 Oct 2025 · temporal.io/changelog/ruby-sdk-generally-available

</div>

<!--
"There are several systems doing this. Temporal. DBOS. Restate.
 Inngest."

"I'm not going to compare them. I picked one and looked at it
 properly."

▸ CLICK

"And I picked Temporal for a boring reason that matters to this
 room specifically. The Ruby SDK went generally available last
 October. Fully supported, same features as Go and Java."

"Which means, for once, we are not standing outside the window
 watching the Java people have a nice time."
   [LAUGH]
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
"Three words. Then code. Only three."

"Workflow. Decides what happens next. Your orchestration."

▸ CLICK

"Activity. Touches the outside world. Charges the card."

▸ CLICK

"Worker. The process you run that executes both."

▸ CLICK

"Everything else is day two."

THREE, NOT SEVEN. Signals, replay and history come later, in
context, where they're on screen. Dumping seven nouns here is
where beginners give up.
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
*** CAREFUL — THIS IS THE SLIDE WHERE A TALK BECOMES AN AD. ***

"Now, the same process, written against that runtime."

"Don't look at how short it is. Line count is a cheap argument,
 and I refuse to make it."

▸ CLICK  (highlights wait_condition)

"Look at one line. wait_condition. That's the two-day wait. No
 scheduler. No re-enqueue. No status column. And it isn't holding
 a thread — the runtime puts the workflow away and brings it back
 when something happens."

"That's the actual claim. Not fewer lines."

EXPLAIN ONLY THAT LINE. Everything else gets decoded next slide.
Syntax verified against gem temporalio 1.6.0.
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
*** THE BRIDGE — more persuasive than the code slide.
    ~6 sec per row. Point, don't teach. ***

"And before anyone has to decode that — you already wrote all of
 this. Every line of it. Just in a different shape."

"The guards you added? The runtime already knows. It's in the
 history."
"The job that re-enqueued itself? That's the one line.
 wait_condition."
"The dedup table? That's a signal. Second one arrives, the
 workflow has already moved on."
"The status column doing double duty as a program counter? That's
 just where the code is."

▸ CLICK  (reconciler row appears, with a dash)
   [BEAT]

"There isn't a row for that one."
-->
---
layout: center
class: text-center
---

# Waiting became a language feature.

<!--
"Waiting became a language feature."

One line. Say it, then move.
-->
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
*** 🔒 PROTECT — EMOTIONAL CENTRE OF THE SECOND HALF. ***

"So here's the actual comparison, and it isn't about syntax."

"Who owns keeping this process alive?"

▸ CLICK

"In the first half of this talk, the answer was: me."
   ← POINT AT YOURSELF. Small gesture, not theatrical.

▸ CLICK

"My columns. My scheduler. My dedup table. My reconciler.
 My phone."
   ← Count them off.

"And I want to be fair to myself. I did a decent job of it.
 It worked."

▸ CLICK

"Here, the answer is: the runtime."
   ← DROP THE HAND.

"That's it. That's the entire trade being offered. Everything
 else is detail."

The room now has ME → RUNTIME. That's the talk in two words.
-->
---
layout: center
class: text-center
---

# The same process, twice

<div class="mt-8 opacity-70">Same requirements. Same five failures. Both broken on purpose.</div>

<!--
*** ⏱ 15:00 GATE — THE DEMO IS THE CENTRE OF GRAVITY. DO NOT RUSH IT. ***
If you're behind, you already cut failure 4. Cut more BEFORE this,
never compress what's on screen.

"So I built the same process twice. Same requirements, same five
 failures. Then I broke both on purpose."

"I'm not running this live at six pm on a Sunday. You're welcome."
   [LAUGH]
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
"First. Kill the worker, right after payment."

"Sidekiq retries, hits my idempotency guards, and — this is the
 important part — it works. It genuinely works. Because I wrote
 the guards."

"The recovery is correct because I made it correct. And I stay
 responsible for that every time someone adds a fourth step.
 Which they will. On a Friday."
   [LAUGH]

▸ CLICK

"Temporal. Another worker picks up the execution and continues
 after the payment activity. I didn't write recovery code."
   [BEAT]
"There is no recovery code to show you. That's the whole slide."

▸ CLICK

"Same outcome. Completely different answer to who is responsible
 for it."
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
*** ✂ CUT THIS SLIDE if you reach it after 18:30. ***

"Second. The warehouse fires the callback twice."

"Sidekiq. Dedup table. Unique index. And a philosophical debate
 about whether twice means a duplicate event or a retry. A debate
 that will happen in a pull request thread, and will involve at
 least one person quoting the HTTP spec."
   [LAUGH]

▸ CLICK

"Temporal. Same signal arrives twice. The workflow is already
 past that wait. Second one is a no-op."

▸ CLICK

"Not magic. Somebody still wrote that logic. The question is only
 whether it was you. At two a.m. Under a deadline."
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
"And the forty-eight hour wait. I'm not demoing that — and how
 I would have demoed it is the finding."

▸ CLICK

"Temporal's test environment skips time. You ask it to jump
 forty-eight hours, and it does."

▸ CLICK

"On the Sidekiq side, I had to fake the clock and fire the cron
 by hand."

▸ CLICK

"I built a fake clock to test my fake timer."
   [LAUGH]

Funny AND technically the point. Let it land.
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
"So here's the only scoreboard I care about."

[Walk the rows briskly. Then land the two that matter:]

"Business logic doesn't move. Nothing here makes your domain
 simpler. And anyone who tells you otherwise is doing a webinar."
   [LAUGH]

"And recovery moves. That's the row you're actually buying."

THEN SEED THE BEGINNER QUESTION so nobody has to raise a hand:
"Oh — and the question I get most, which is a good one. What's
 the difference between a workflow and an activity? An activity
 touches the outside world. A workflow decides what happens next.
 That's the whole split."
-->
---
layout: center
class: text-center
---

# Okay. What did we just buy?

<!--
*** ⏱ 20:00 GATE — you should be off the demo by now. ***

"So that's the good part."
   [BEAT]
"Now the honest part. Because that table made it look free, and
 it is not."
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
*** 🔒 NEVER CUT THIS SLIDE — it's what makes the trade-off credible. ***

"The one you hit on day one. Determinism."

*** SAY THIS SENTENCE EXACTLY. The loose version is wrong, and
    people here will go and implement it: ***
"Workflow code is not ordinary Ruby. The runtime reconstructs the
 workflow's state by replaying its recorded history against your
 workflow code. So your code has to produce the same decisions,
 given the same history, every time."

"Which means it can't ask the outside world anything mid-decision."

▸ CLICK

"Read that top block again. Time.now. Order.find. The two most
 ordinary things in Rails. And inside a workflow, they're bugs."

"Matz optimised Ruby for developer happiness. This is the one
 corner of it that was optimised for a distributed systems paper."
   [LAUGH — one joke max here. Don't undercut it.]

"That's a new rule your whole team holds in their head, forever,
 in a language where nothing else behaves that way."
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
"And then the rest of the bill."

▸ CLICK
"Another runtime. It's not Rails, Postgres, Redis any more.
 Someone operates this. Self-hosted, it's a real service with a
 real datastore. Cloud, it's a bill and a vendor."

▸ CLICK
"Debugging changes shape. You're not reading a stack trace,
 you're reading an execution history. Often better — you can see
 exactly what happened to one order six weeks ago. But it is not
 the skill your team has today. And binding.pry is not going to
 help you."
   [LAUGH]

▸ CLICK
"Versioning becomes first-class. Old executions are still in
 flight when you deploy. Which is more honest than the shim with
 the comment on it — but more honest and less work are different
 things."
   [LAUGH]

▸ CLICK
"And the one nobody puts on a slide. Your organisation now has
 one more thing it has to understand. Every new hire. Every
 incident. Every person you wake up."

▸ CLICK
"A technology can reduce your application complexity and increase
 your system complexity at the same time. That's a legitimate
 trade. It's just a trade — know which side you're on."
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
"So. Where does that leave us."

"If your work is short, independent, stateless, retryable as a
 unit, fire and forget — that's a job. Sidekiq isn't just
 adequate there, it's correct. And adding a runtime would be
 making your own life worse on purpose."

"There's a word for adding distributed systems you don't need.
 It's usually on someone's promotion packet."
   [LAUGH]

▸ CLICK

"But if it's multi-step. Long-running. Stateful. Waiting on
 external events. Waiting on humans. Needing compensation. And —
 this is the tell — if it keeps accumulating orchestration code
 around it."

"Then you may already be running a workflow engine. You're just
 also the one maintaining it. At three a.m. Without documentation."

✂ IF LONG, CUT THIS PARAGRAPH — never the ending:
"And owning it is a real answer. Postgres is extremely good. A
 state machine and a well-written reconciler have kept a lot of
 serious companies alive. If your process fits in your head,
 keeping it in Rails is the better engineering decision, and I'd
 defend that too."
-->
---
layout: center
class: text-center
---

# An abstraction is useful right up until you start implementing the abstraction it was supposed to give you.

<!--
*** 🔒 THE EXPERTS' TAKEAWAY — THE THESIS. SAY IT SLOWLY. ***

"The idea I want to leave you with isn't about Temporal at all."

"An abstraction is useful right up until you start implementing
 the abstraction it was supposed to give you."
   [BEAT]

"Sidekiq gives you a job abstraction. It's a great abstraction.
 But if your application has ended up implementing state, and
 waiting, and orchestration, and recovery, and timers, and events
 — then whatever you're holding stopped being a job a while ago."

NO JOKE AFTER THIS.
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
*** 🔒 THE LANDING — DO NOT IMPROVISE THIS. ***

"So. That job you thought of when I asked at the start. The one
 some of you raised your hand for very fast."

"Go and open it tomorrow."

▸ CLICK

"And if there's a comment on it with someone's name, and that
 person doesn't work there any more —"
   [BEAT — dry, underplayed. A nod, not a punchline.]
"that's your answer."

▸ CLICK

"Is this still a job?"

"I don't know, for your system. I think you do."

   [SILENCE. COUNT THREE. DO NOT FILL IT.]

THEN advance. Not before.
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
"Thank you."

"I'm Anubhav. That's where to find me. And honestly, the thing I
 most want out of tonight is to hear where you'd draw the line.
 So: questions, arguments, war stories."

LEAVE THIS SLIDE UP FOR THE ENTIRE Q&A.

IF SILENT FOR 5 SECONDS, take your own:
"The question I get most is: why not just build this ourselves?"
→ "You absolutely can. That's what the first half of this talk
   was, and it worked. The question was never whether it's
   possible. It's whether workflow execution semantics is
   something you want your application team to own as
   infrastructure. The signal isn't complexity — it's whether
   that code is still growing."

IF HOSTILE — verbatim, agree instantly:
"The fact that Sidekiq lets you build all of that is a point in
 its favour. The talk isn't that it can't. It's that at some
 point you should notice you did."
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
*** APPENDIX — DO NOT PRESENT. ***
Exists so the published deck carries its sources.
All URLs verified 200 on 6 Sep 2026.
-->
