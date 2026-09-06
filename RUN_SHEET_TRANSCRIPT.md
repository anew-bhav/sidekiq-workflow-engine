# Your Sidekiq Jobs Have Become a Workflow Engine
## Run sheet + transcript — BRUG, Sunday 6 Sep 2026, 18:00

**Slot:** 25 min content + 5 min Q&A

## Timing reality — read before rehearsing

**The scripted material is denser than the nominal timings suggest.** The per-beat timestamps below are correct on paper and will not survive contact with a live room: laughs eat 2–3 seconds each, code needs silence while people read it, and pauses you've marked deliberately are real time. Failure #1 in particular carries an explanation, a definition, a code slide, a reframe, two laughs *and* the transaction preempt inside a nominal 2:30. Expect it to run 3:00.

**So rehearse the gates, not the timestamps.** Memorising per-slide times will make you rush a section that was landing well. Only three numbers matter:

- `10:00` → THE REALIZATION
- `15:00` → demo starts
- `20:00` → demo ends

**Drift diagnostic:**
- Realization at 10:45 → **fine.** Do nothing. Keep delivering.
- Entering Temporal at 13:30 → **trouble.** Cut failure #4 out loud and go.
- Not started the demo by 15:30 → cut scenario B on the spot.

One stopwatch runthrough. Note only where you hit those three gates.

## PROTECT — do not compress these, whatever the clock says

1. **Program counter** (~7:15) — conceptual peak of the first half
2. **Ownership / ME → RUNTIME** (~15:00) — emotional centre of the second half
3. **The demo** (15:15–20:00) — centre of gravity of the whole talk

Everything else is negotiable. These three are why the talk works. If something has to give, it comes from the cut list below — never from these.

**Cut list when behind, in order:**
1. Failure #4 (deploy/versioning) → one spoken line
2. Rails-tension aside → delete
3. Second demo scenario → drop to one
4. "Where should state live" spoken bit → leave it on the closing slide

**Never cut:** inline jargon definitions (3 sec each, they're the beginner on-ramp), the JUST counter, the reconciler callback.

**THE DEMO IS NOT FIVE MINUTES. It is the centre of gravity of the talk.**
If you are behind at 14:30, you do not compress the demo — you cut from the list above, out loud, and move on. The room will happily forgive *"I'm going to skip failure four."* It will not forgive a rushed demo where nobody could see what actually happened. Protect it aggressively.

---

## TWO RUNNING GAGS — set up early, pay off late

**1. The JUST counter.** Bottom-right corner of every slide in the complexity section. Every time you say *"just add another job"* / *"just add a column"*, it ticks up. Nobody consciously notices until the payoff at 9:30 when it reads **JUST × 7** and the slide title becomes `Workflow Engine v1.0`. Cheap to build, biggest laugh in the talk, and it's the argument.

**2. The enum that grows.** Same slide corner, opposite side. Order status enum, re-shown each failure:

```ruby
enum status: %i[pending shipped]                                   # minute 2
enum status: %i[pending charged reserved shipped]                  # minute 4
enum status: %i[pending charged reserved awaiting_warehouse
                shipped]                                           # minute 6
enum status: %i[pending charging charged charge_failed
                charge_retrying reserved reservation_failed
                awaiting_warehouse warehouse_timed_out shipping
                shipped cancelling cancelled refund_pending
                refunded stuck]                                    # minute 9
```

Never comment on it. Let people notice. The word `stuck` at the end does the work.

`[PREEMPT]` markers show where a likely question gets defused before it can be asked.
`[LAUGH]` markers = pause. Land it, then move. Don't step on your own laugh.

---

## 0:00 — 0:45 · POLL

> Quick one before I start. Hands up if you travelled more than an hour to get here tonight.
>
> *(look at the hands)*
>
> More than two? **[LAUGH]**
>
> Right. HSR on a Sunday evening, and you picked this over dinner. Thank you, genuinely. I'll try to make it worth the auto fare. **[LAUGH]**
>
> Two questions before I start. Hands up.
>
> One: who runs Sidekiq in production?
>
> *(look at them — actually look)*
>
> Right. Most of the room.
>
> Two, the real one: who has a Sidekiq job with a state machine inside it?
>
> *(fewer hands, more laughing)*
>
> Some of you put your hand up *very* fast. **[LAUGH]**
>
> Keep that job in your head. We're going to go find it.

**Note:** the second question is the whole talk in one hand-raise. Don't rush it. The local-traffic joke is buying you goodwill for the next 90 seconds — spend it.

---

## 0:45 — 2:00 · THE BORING THING THAT WORKS

> Let me start somewhere completely uncontroversial.
>
> ```ruby
> GenerateInvoiceJob.perform_async(invoice.id)
> ```
>
> That's it. Something happened in a request, we don't want to do it in the request, we push it to a queue.
>
> This is good code. I want to be clear about that, because the title has "Sidekiq" in it and you're all waiting for the part where I tell you it's bad.
>
> That part isn't coming. There's no twist. Sidekiq is great, Mike Perham is a national treasure of a country I don't live in, and if your problem fits on that one line, write that line and go home. **[LAUGH]**
>
> I'm not going to manufacture a problem so I can sell you a solution. Instead we're going to follow one process — one — and see where it takes us.

**[PREEMPT: "this is a vendor pitch"]** — killed in the first 90 seconds, explicitly, before the suspicion can form.

---

## 2:00 — 9:30 · INCREMENTAL COMPLEXITY

### 2:00 — expert bone + happy path (0:45)

> The process is order fulfillment. Before I start:
>
> **half this room has built this. Watch which step you stopped at.**
>
> Version one.
>
> ```ruby
> class ProcessOrderJob
>   include Sidekiq::Job
>
>   def perform(order_id)
>     order = Order.find(order_id)
>     charge_payment(order)
>     reserve_inventory(order)
>     ship(order)
>   end
> end
> ```
>
> Three steps, one job, top to bottom. Genuinely fine. Nobody argues with it in review.
>
> Then reality shows up. Five times. Like it does.

**Note:** say the "watch which step you stopped at" line, then pause half a beat. It converts experts from *ahead of you* into *auditing their own code*.

### 2:45 — Failure #1: worker dies (2:30)

> **Failure one. Payment succeeds. Worker dies.**
>
> Box recycled, deploy went out, OOM killer, someone ran a migration on a Friday. Doesn't matter.
>
> Sidekiq does the correct thing: it retries. `perform` runs again from the top. And charges the customer twice.
>
> Now — the customer notices this. Customers are extremely good at noticing this. They have never once emailed to say "you charged me half as much as expected." **[LAUGH — SACRIFICIAL: this is the one joke to drop if failure #1 is running long. The transaction preempt below is not droppable.]**
>
> So we make it idempotent — idempotent meaning safe to run twice. And to be safe to run twice, the job has to know what it already did. Which means it has to write down what it already did.
>
> ```ruby
> def perform(order_id)
>   order = Order.find(order_id)
>   charge_payment(order)    unless order.charged?
>   reserve_inventory(order) unless order.reserved?
>   ship(order)              unless order.shipped?
> end
> ```
>
> We just added three columns. And nobody in the business asked for `charged_at`. No PM has ever written a ticket that says "as a user, I want a boolean indicating how far through a Sidekiq job I got." **[LAUGH]**
>
> That's not information about the order. That's information about **how far along the job got**. We persisted execution state into our domain model.
>
> And it was the right call. I'd do it again tomorrow. But it's the first brick.
>
> `JUST × 1`

**[PREEMPT: "just use a transaction"]** — say it here, out loud:

> And no, you can't wrap this in a transaction, because the payment gateway is not in your database. That's the entire problem. The moment a step touches the outside world, `ActiveRecord::Base.transaction` stops being the thing that saves you — and for most of us that's genuinely upsetting, because it's been the thing that saves us since we started writing Rails. **[LAUGH]**

### 5:15 — Failure #2: warehouse takes two days (2:15)

> **Failure two. The warehouse takes two days to confirm.**
>
> A worker cannot sit there for two days. It's a thread, it has a timeout, and it will be killed by the next deploy — which, at most companies, is roughly eleven minutes away. **[LAUGH]**
>
> Somebody always suggests `sleep 2.days` at this point. Usually as a joke. Usually.
>
> So we split the job.
>
> ```ruby
> class CheckWarehouseJob
>   def perform(order_id)
>     order = Order.find(order_id)
>     return ShipOrderJob.perform_async(order_id) if warehouse_ready?(order)
>
>     CheckWarehouseJob.perform_in(1.hour, order_id)   # 🤞
>   end
> end
> ```
>
> A job that schedules itself. All of you have written this. Some of you wrote it this week. Some of you are looking at your laptop right now. **[LAUGH]**
>
> And look at what it actually is. That's a timer. We had no way to wait, so we built waiting out of the parts we had — a scheduler and a queue. This is hope-driven development, and it has a `perform_in` in it.
>
> Also, quietly: the status column is now doing real work. It's not describing the order any more. It's telling the next job where to resume.
>
> It's a program counter. In your orders table. With an index on it.
>
> *(beat)*
>
> And I want to be precise about what I'm claiming, because I'm not saying our Rails code got ugly. The code is fine. The code is *nice*.
>
> I'm saying we introduced a concept. Nobody decided to. Nobody wrote it down. But there is now a program counter in this system, and it's spread across a column, a scheduler and a Redis key.
>
> `JUST × 2`

**Note:** THIS IS THE CONCEPTUAL PEAK OF THE FIRST HALF. Not a throwaway line — the reframe the whole talk turns on. You are not making an aesthetic argument ("look how ugly this got"), you are making a conceptual one ("look what we accidentally invented"). The aesthetic version is dismissible; the conceptual one isn't. Slow down here. Say "program counter", pause, then the two-sentence reframe, then pause again. This moment is what makes the realization at 9:30 feel inevitable instead of asserted.

### 7:30 — Failures #3, #4, #5: montage (2:00)

> Three more, fast, because you know how these go.
>
> **Three. The warehouse sends a callback instead.** Better! Except: how does the callback find the order? Add a token. What if it arrives twice? Add a dedup table. What if it arrives *before* we committed the row?
>
> Then you get `undefined method for nil:NilClass`, which as we all know is the national anthem of this ecosystem. **[LAUGH]** And you fix it with a lock, or a retry, or a `sleep 0.5` you tell nobody about.
>
> **Four. We deploy mid-flight.** There are orders in the queue *right now*, halfway through, serialized with the old arguments. So you version the payload, or drain the queue, or write the shim with the comment that says `# TODO: remove after migration — Mar 2024`. **[LAUGH]**
>
> **Five. The customer cancels.** After payment, before shipping. Now you have to stop a process that isn't running — it's a row in Redis with a timestamp on it — and undo a charge. That's compensation: the undo you write yourself, usually the week after someone from finance asks a very calm question. **[LAUGH]**
>
> And somewhere in here, someone writes this:
>
> ```ruby
> # Runs every 10 min. Do NOT delete.
> # Ask Anubhav before changing this.
> # (Anubhav doesn't work here any more.)
> class ReconcileStuckOrdersJob
> ```
>
> **[LAUGH]**
>
> Every company I've worked at has this job. It always has that comment. And `git blame` always says it was me. **[LAUGH]**
>
> `JUST × 6`

**[PREEMPT: "you're mocking my codebase"]** — the reconciler bit must land as *recognition*, not contempt. You're in the joke, not above it. That's what `git blame says it was me` is for. Don't cut that line.

---

## 9:30 — 12:00 · THE REALIZATION

**⏱ CLOCK CHECK — be here by 10:00.**

### 9:30 — the pile + JUST payoff (1:00)

> So let's put it on one slide. Not the business logic — just the machinery we added to keep the process alive.
>
> ```text
> Sidekiq          Rails / Postgres
>  ├── retries      ├── state columns
>  ├── scheduling   ├── idempotency guards
>  └── queues       ├── callback dedup
>                   ├── polling
>                   ├── payload versioning
>                   ├── compensation
>                   └── reconciliation
> ```
>
> *(counter in the corner flips: `JUST × 7`. Slide title changes to:)*
>
> ```text
> Workflow Engine v1.0
> ```
>
> **[LAUGH — this is the biggest one in the talk. Wait for it. Do not talk over it.]**
>
> Every one of those was a good decision. I'd defend all of them in code review. None is wrong.
>
> But look at the shape. State. Timers. Retries. External events. Recovery. Compensation.
>
> That is not a job any more.
>
> **We didn't set out to build a workflow engine. We just kept solving the next requirement.**
>
> And nobody's name is on it. There was never a ticket that said "build workflow engine." It arrived one PR at a time over eighteen months, and every one of those PRs was small enough to approve on your phone. **[LAUGH]**
>
> It also has a class name. It's usually something like this.
>
> ```ruby
> class DefinitelyNotAWorkflow < ApplicationJob
>   # 847 lines
> end
> ```
>
> **[LAUGH]**

### 10:45 — job vs process (1:15)

> So let me draw the line that actually matters.
>
> A **job** says: *please do this.* Send the email. Resize the image. Sync the record. Short, discrete, retry as a unit.
>
> A **workflow** says: *make sure this eventually completes.* Onboarding. Fulfillment. Payment lifecycle. Provisioning.
>
> It's a spectrum, not two boxes. And nothing happens when you cross it. No alarm goes off. Nobody gets paged. Rubocop does not have a rule for this. **[LAUGH]**
>
> Which is exactly why you end up on the wrong side without noticing.
>
> **A workflow is what a job gradually turns into.**

**Note:** last line is the beginners' takeaway — the sentence they repeat to a colleague on Monday. Say it slowly. No joke after it. Let it sit.

---

## 12:00 — 12:45 · PREEMPT SLIDE

> Now. Some of you have been quietly furious for five minutes going, *"yes, and that's why Sidekiq Pro has Batches."*
>
> You're right. Let me put them all on screen, because I'm not building a strawman and this is Ruby — there is always a gem for it, and usually four, and two are unmaintained. **[LAUGH]**
>
> ```text
> Sidekiq Pro Batches · acidic_job · Gush
> AASM · Statesman · GoodJob
> ```
>
> These are good. Batches gives you fan-out and callbacks. `acidic_job` gives you real step-level idempotency. Statesman gives you an auditable state machine. If you're not using them, some of you should leave now and go use them. I won't be offended. **[LAUGH]**
>
> But notice what they do. Each one makes **a step** better.
>
> None of them fundamentally changes who **owns keeping the process alive**. It's still your app, your Postgres, your reconciler, your phone at 3am.
>
> That's not a criticism. That's the question of the talk.

**[PREEMPT: the #1 Q&A ambush]** — this slide exists to defuse it *before* Temporal appears. Say Temporal first and this sounds defensive. Order is load-bearing.

---

## 12:45 — 15:15 · DURABLE EXECUTION

> So here's the question.
>
> **What if keeping the process alive was the runtime's job instead of ours?**
>
> Not the business logic. The machinery. State, timers, retries, resumption, history.
>
> That idea has a name: **durable execution**. You write the process as ordinary sequential code, and when the machine running it dies, the process doesn't.
>
> There are several systems doing this — **Temporal, DBOS, Restate, Inngest**. I'm not comparing them. I picked one and looked at it properly, and I picked Temporal for a boring reason that matters to this room: **the Ruby SDK went GA last October.** Fully supported, same features as Go and Java.
>
> Which means for once we are not standing outside the window watching the Java people have a nice time. **[LAUGH]**
>
> Three words, then code. Only three.
>
> - **Workflow** — decides what happens next. Your orchestration.
> - **Activity** — touches the outside world. Charge the card, call the warehouse.
> - **Worker** — the process you run that executes both.
>
> That's the vocabulary. Everything else is day two.
>
> ```ruby
> class OrderWorkflow < Temporalio::Workflow::Definition
>   def execute(order_id)
>     Temporalio::Workflow.execute_activity(ChargePayment, order_id)
>     Temporalio::Workflow.execute_activity(ReserveInventory, order_id)
>
>     Temporalio::Workflow.wait_condition { @warehouse_ready }
>
>     Temporalio::Workflow.execute_activity(ShipOrder, order_id)
>   end
>
>   workflow_signal
>   def warehouse_confirmed = @warehouse_ready = true
> end
> ```
>
> Careful here, because this is the slide where a talk becomes an ad.
>
> Don't look at how short it is. Line count is a cheap argument and I refuse to make it.
>
> Look at `wait_condition`. That's the two-day wait. No scheduler. No re-enqueue. No status column. And it isn't holding a thread — the runtime puts the workflow away and brings it back when something happens.
>
> That's the actual claim. Not "fewer lines."
>
> **Waiting became a language feature.**
>
> And before anyone has to decode that — you already wrote all of this. Every line of it. Just in a different shape.

*(mapping slide — walk the rows briskly, ~6 seconds each. Point, don't teach.)*

| What you built in the first half | Here |
|---|---|
| `order.charged?` guards | history records the activity completed |
| `CheckWarehouseJob` re-enqueueing itself | `wait_condition` |
| callback token + dedup table | `signal` |
| status column as program counter | the workflow's own position in the code |
| `ReconcileStuckOrdersJob` *(on click)* | — |

> "The guards you added — the runtime already knows, it's in the history."
> "The job that re-enqueued itself — that's the one line, `wait_condition`."
> "The dedup table — that's a signal. Second one arrives, workflow's already moved on."
> "The status column doing double duty as a program counter — that's just where the code is."
>
> *(click — reconciler row appears with a dash. Beat.)*
>
> "There isn't a row for that one."

**Note:** THIS SLIDE IS THE BRIDGE, and it is more persuasive than the code slide is. The Ruby alone is illegible to most of the room in 90 seconds — this decodes it by mapping every line back to something *they* wrote in the first half, so it lands as recognition rather than as a new API to learn.

**Timing:** costs ~30s net. You get most of it back by not explaining the code slide in detail — point at `wait_condition`, say the one line, come here.

**On the code slide itself:** don't narrate it top to bottom. Say "line count is a cheap argument", click to highlight `wait_condition`, explain that one line only, then move. Everything else gets decoded here.
>
> But even that isn't the real comparison, so let me say the actual one plainly.
>
> The question is not *which implementation has less code.*
>
> The question is: **who owns keeping this process alive?**
>
> In the first half of this talk, the answer was: **me.** My columns, my scheduler, my dedup table, my reconciler, my phone. And I want to be fair — I did a decent job of it. It worked.
>
> Here the answer is: the runtime.
>
> That's it. That's the entire trade being offered. Everything else is detail.

**STAGING — do this with your body.** On *"the answer was: me"*, point at yourself. Small gesture, not theatrical. Then count the list off: *"My columns. My scheduler. My dedup table. My reconciler. My phone."* Then drop the hand and say *"Here the answer is: the runtime."*

The room now has:

```text
ME  →  RUNTIME
```

That's the whole talk in two words, and it arrives physically rather than as a claim. It's the cheapest, highest-leverage thing in the deck — costs four seconds, no slide.

**Note:** THIS is the emotional centre of the Temporal section, not the code slide. The code exists only to set up this sentence. If the room remembers one thing from minutes 12–15, it should be *"who owns keeping this alive"* — not the Ruby. Deliver the "me" with a bit of ownership; you're not confessing, you're establishing that you were competent and it still accumulated.

**[PREEMPT: "you designed the example to flatter Temporal"]** — the ownership framing is what defuses this. A skeptic can argue about line counts forever. Nobody can argue that the reconciler was in your repo.

**[PREEMPT: "that's just my code but shorter"]** — "line count is a cheap argument" costs 4 seconds and buys the whole section.

---

## 15:15 — 20:00 · THE EXPERIMENT

**⏱ CLOCK CHECK — demo starts at 15:00.**

> So I built the same process twice. Same requirements, same five failures. Then broke both on purpose.
>
> I'm not running this live at 6pm on a Sunday. You're welcome. **[LAUGH]**
>
> *(if Tier A/B: "I recorded it, because live demos at 6pm on a Sunday are how you end up on r/programming.")*

### Scenario A — kill the worker (2:00)

> **Kill the worker right after payment.**
>
> Sidekiq: retries, hits my idempotency guards, and — this is the important bit — **it works**. It genuinely works. Because I wrote the guards. The recovery is correct because I made it correct, and I stay responsible for it every time someone adds a fourth step. Which they will. On a Friday. **[LAUGH]**
>
> Temporal: another worker picks up the execution and continues after the payment activity. I didn't write recovery code. There is no recovery code to show you. That's the whole slide.
>
> Same outcome. Completely different answer to "who's responsible for that."

### Scenario B — duplicate callback (1:30)

> **Warehouse fires the callback twice.**
>
> Sidekiq: dedup table, unique index, and a philosophical debate about whether "twice" means a duplicate event or a retry — a debate that will happen in a PR thread and will involve at least one person quoting the HTTP spec. **[LAUGH]**
>
> Temporal: same signal twice, workflow's already past that wait, second one's a no-op.
>
> Not magic. Somebody still wrote that logic. The question is whether it was **you**, at 2am, under a deadline.

### The 48-hour wait (0:45)

> I'm not demoing the two-day wait — and *how* I would have demoed it is the finding.
>
> Temporal's test environment skips time. You ask it to jump 48 hours and it does.
>
> On the Sidekiq side I had to fake the clock and fire the cron by hand.
>
> That asymmetry is the talk. On one side waiting is a real thing the runtime understands. On the other, waiting is something I simulated out of a scheduler and a status column — so to *test* it, I have to simulate it a second time. I built a fake clock to test my fake timer. **[LAUGH]**

### Who owns what (0:30)

> Only scoreboard I care about.
>
> | Concern | Rails + Sidekiq | Durable runtime |
> |---|---|---|
> | Retry | Job system | Runtime |
> | Timer | Scheduler + job | Runtime |
> | Workflow state | Your DB | Runtime |
> | External event | Callback + dedup | Signal |
> | Recovery | You | Runtime |
> | Orchestration | You | Workflow |
> | **Business logic** | **You** | **You** |
> | Side effects | You | Activities |
>
> Two rows matter. **Business logic doesn't move** — nothing here makes your domain simpler, and anyone who tells you otherwise is doing a webinar. **[LAUGH]**
>
> And **recovery** moves. That's the row you're buying.

### Seeded beginner question (0:15)

> The question I get most, and it's a good one: what's actually the difference between a workflow and an activity?
>
> Activity touches the outside world. Workflow decides what happens next. That's the whole split.

**[PREEMPT: beginners won't ask in a room full of experts]** — ask it for them. No hand required.

---

## 20:00 — 23:00 · WHAT DID WE JUST BUY

**⏱ CLOCK CHECK — off the demo by 20:00.**

> That's the good part. Now the honest part, because that table made it look free and it is not.

### Determinism (1:15)

> The one you hit on day one.
>
> Workflow code is not ordinary Ruby. The runtime **reconstructs the workflow's state by replaying its recorded history against your workflow code** — so your code has to produce the same decisions given the same history, every time.
>
> Which means it can't ask the outside world anything mid-decision.
>
> Which means:
>
> ```ruby
> # Inside workflow code — replay breaks all of these
> Time.now
> SecureRandom.uuid
> rand(100)
> Order.find(id)             # any IO at all
>
> # What you write instead
> Temporalio::Workflow.now
> Temporalio::Workflow.random.uuid
> Temporalio::Workflow.execute_activity(FetchOrder, id)
> ```
>
> Read the top block again. `Time.now`. `Order.find`.
>
> The two most ordinary things in Rails. Inside a workflow, they're bugs.
>
> Matz optimised Ruby for developer happiness. This is the one corner of it that was optimised for a distributed systems paper. **[LAUGH]**
>
> That's not a footnote. It's a new rule your whole team holds in their head forever, in a language where nothing else behaves that way.

**Note:** this slide is what makes the losses section credible. Never cut it. One joke max — don't undercut it.

**Say the replay sentence exactly as written.** The loose version — "it re-runs your workflow from the top" — is more memorable and slightly wrong: it leaves people thinking the whole program re-executes from scratch on every event. Some of this room will go implement this next month, and that's the mental model they'd carry. Precision costs you three words here.

### The rest of the bill (1:45)

> And the rest of what you're signing up for.
>
> **Another runtime.** It's not Rails, Postgres, Redis any more. Someone operates this. Self-hosted it's a real service with a real datastore. Cloud, it's a bill and a vendor and a procurement conversation.
>
> **Debugging changes shape.** You're not reading a stack trace, you're reading an execution history. Often *better* — you can see exactly what happened to one order six weeks ago — but it is not the skill your team has today, and `binding.pry` is not going to help you. **[LAUGH]**
>
> **Versioning becomes first-class.** Old executions are still in flight when you deploy, and Temporal makes you handle that explicitly. Which is more honest than the shim with `# TODO: remove Mar 2024` on it — but "more honest" and "less work" are different things. **[LAUGH]**
>
> **And the one nobody puts on a slide:** your organisation now has one more thing it must understand. Every new hire. Every incident. Every person you wake up.
>
> A technology can reduce your *application* complexity and increase your *system* complexity at the same time. That's a legitimate trade. It's just a trade — know which side of it you're on when you make it.

---

## 23:00 — 25:00 · WHERE'S YOUR LINE

> So where does that leave us.
>
> If your work is short, independent, stateless, retryable as a unit, fire-and-forget — that's a job. Sidekiq isn't just adequate, it's **correct**, and adding a runtime would be making your own life worse on purpose. There is a word for adding distributed systems you don't need, and it's usually on someone's promo packet. **[LAUGH]**
>
> But if it's multi-step, long-running, stateful, waiting on external events, waiting on humans, needs compensation — and this is the tell — **it keeps accumulating orchestration code around it**:
>
> then you may already be running a workflow engine. You're just also the one maintaining it. At 3am. Without documentation.
>
> And owning it is a real answer. Postgres is *extremely* good. A state machine and a well-written reconciler have kept a lot of serious companies alive. If your process fits in your head, keeping it in Rails is the better engineering decision and I'd defend that too.
>
> The idea I want to leave you with isn't about Temporal at all.
>
> **An abstraction is useful right up until you start implementing the abstraction it was supposed to give you.**
>
> Sidekiq gives you a job abstraction. It's a great abstraction. But if your app has ended up implementing state, and waiting, and orchestration, and recovery, and timers, and events — then whatever you're holding, it stopped being a job a while ago.
>
> So — that job you thought of when I asked at the start. The one some of you raised your hand for very fast.
>
> Go and open it tomorrow. And if there's a comment on it with someone's name, and that person doesn't work there any more — **[LAUGH]** — that's your answer.
>
> # Is that still a job?
>
> I don't know for your system. I think you do.
>
> Thank you.

### The landing — exact sequence, don't improvise it

1. `Is that still a job?` on screen.
2. *"I don't know for your system. I think you do."*
3. **SILENCE. Count three.** Do not fill it. This is the only moment in 25 minutes where nothing is happening, and it's what makes the question feel handed over rather than asked rhetorically.
4. *Then* advance to the contact slide.
5. *"I'm Anubhav. That's where to find me — and honestly the thing I most want out of tonight is to hear where you'd draw the line. So: questions, arguments, war stories."*
6. **Leave the contact slide up for the whole Q&A.** A black screen during Q&A wastes five minutes of the only time your name is in front of 200 people.

Opening Q&A with *"where would you draw the line?"* instead of *"any questions?"* matters — the second one gets silence in a big room. You're inviting disagreement, which is the thing this talk has actually earned.

If nobody speaks within five seconds, take your own: *"The question I get most is why not just build this ourselves —"* and answer it. Never stand in silence waiting; it reads as the talk not landing when it just means people are shy.

**Fill in before presenting:** role/company, three handles, short link to slides + both implementations. No personal email on a projector — handles are enough.

**Note:** the reconciler callback + poll callback is what makes the ending feel earned rather than rhetorical. If you're running long, cut the Postgres paragraph — never the callback.

**Tone warning — underplay it.** The argument is already won by the time you get here; the callback is a nod, not a punchline. Land it dry and keep moving to the final question. The feeling you want is *"oh god, that's my codebase"* — not *"haha, legacy code, am I right."* The second one makes you the guy laughing at their repo, and it costs you the ending. Aim for recognition, not ridicule.

---

# Q&A

Five minutes, so ~4 questions. 45 seconds each, not three minutes.

**"Why not just use Sidekiq Batches?"**
> Batches is genuinely good at fan-out and callbacks. What it doesn't do is own state, timers, or resumption across a deploy. If your process is a fan-out, Batches is right and Temporal is overkill.

**"What does it cost / self-host or Cloud?"**
> Cloud is per-action, so it scales with executions rather than with your ops team. Self-hosting is a real service plus a real datastore and you own the upgrades. Honestly: for a small team, self-hosting Temporal is a bigger commitment than running Sidekiq.

**"We do all this in Postgres and it's fine."**
> Then it probably is fine. The test isn't complexity, it's whether that machinery is still *growing*. Stable is fine. Compounding is the signal.

**"What happens when Temporal is down?"**
> Workers stop making progress, history is durable, executions resume. You moved the failure domain, you didn't delete it. Anyone who says otherwise is selling something.

**"How do you test workflows?"**
> Time-skipping test env — a 48-hour workflow runs in milliseconds. Replay makes it deterministic so tests aren't flaky. Strongest part of the story and I under-sold it.

**"How would I migrate an existing Rails app?"**
> One process. The worst one — whichever has the reconciler with someone's name in the comment. Your service objects become activities mostly unchanged; the orchestration is what you rewrite.

**"Isn't putting business process into infrastructure bad coupling?"**
> Sharpest objection here and I don't have a clean answer. It makes the process explicit and observable, and it couples you. If you have a good answer, find me after — I want it.

**"Why not just build this ourselves?"** ← EXPECT THIS ONE. Also your Q&A opener if the room is quiet.

**Framing when you ask it yourself** — say it as reported, never as invented:
> "The question I get most when I talk about this is: why not just build it ourselves?"

Do NOT say "a question I often ask myself" — that's what sounds staged.

**The answer (~50s, near-verbatim):**
> "You absolutely can. That's what the first half of this talk was — and I want to be clear, it worked. It shipped, it was correct, customers got their orders.
>
> So the question was never whether it's possible. It obviously is. All of us have done it.
>
> The question is whether workflow execution semantics — retries, timers, resumption, recovery — is a thing you want your application team to own as infrastructure.
>
> For some teams that's an easy yes. You've got the people, the process is stable, it's 200 lines and nobody's touched it in a year. Keep it.
>
> The signal isn't complexity. It's whether that code is still **growing**. Stable machinery is fine. Compounding machinery is the tell."

**Structure, if you fumble and need to rebuild live:**
concede → point at your own first half → possible-vs-ownership → the discriminator → stop.

**Delivery rules:**
- Concede in the FIRST sentence. Defend first and you're a vendor for the rest of Q&A.
- 50 seconds. Not three minutes. This is the opener, leave room for real questions.
- End on "either answer is fine" and mean it.

**The follow-up you will get — "how do I know if it's growing?"** Have this ready, it's the most useful thing you hand anyone all night:
> "Run `git log` on that file for the last twelve months. Sort the commits into two piles: ones that changed business rules, and ones that changed how the process survives failure. If the second pile is bigger, you already know."


**"Doesn't this just move complexity?"**
> Yes. Explicitly yes. The question is whether it moves somewhere better-tested than your reconciler. Sometimes obviously. Sometimes your reconciler is 80 lines and works fine.

---

## If someone is hostile

BRUG has people who've run Sidekiq at scale for a decade and may hear this as an attack.

Agree, fast and genuinely:
> "Yeah — and the fact that Sidekiq *lets* you build all of that is a point in its favour. It's flexible enough that you can. The talk isn't that it can't. It's that at some point you should notice you did."

**MEMORIZE THIS ONE VERBATIM.** It's the only line in the deck you should be able to say without thinking. Hostile questions arrive with adrenaline and that is exactly when you improvise badly and sound defensive. Having this ready means you agree instantly and confidently instead of negotiating — and agreeing instantly is what ends it. The last clause is the whole move: *it's that at some point you should notice you did.*

Don't defend Temporal. You're not its lawyer. You looked at it and reported back.

---

## Comedy notes

- **~16 laugh beats, roughly one per 90 seconds.** That's the right density for a technical talk. More and it's a set; fewer and it's a lecture.
- **Every joke rides the argument.** None is detachable. If you cut a joke for time you also cut a point — so cut from the *cut list*, not from the jokes.
- **You are inside every joke, not above it.** `git blame says it was me` is the load-bearing line of the whole comedic register. It's what makes the reconciler bit affectionate instead of superior. If the room thinks you're mocking their codebase, you lose them and don't get them back.
- **Two places with no joke after them, deliberately:** *"A workflow is what a job gradually turns into"* and *"Is that still a job?"* Silence is the punctuation there.
- **The JUST × 7 payoff is your biggest laugh.** Do not talk over it. Count three beats. It's also the single strongest moment of the argument, which is not a coincidence.

---

# References & credits

All URLs verified 200 on 6 Sep 2026. Deck carries these on an appendix slide (last slide, not presented).

**Temporal**
- [Ruby SDK GA announcement — 1 Oct 2025](https://temporal.io/changelog/ruby-sdk-generally-available) — source for the "went GA last October" claim
- [github.com/temporalio/sdk-ruby](https://github.com/temporalio/sdk-ruby) — releases, changelog
- [docs.temporal.io/develop/ruby](https://docs.temporal.io/develop/ruby)
- Slide code verified against gem `temporalio` **1.6.0** (latest 1.7.0; no API on these slides changed between them)

**Sidekiq** — Mike Perham / Contributed Systems
- [sidekiq.org](https://sidekiq.org)
- [Batches (Sidekiq Pro)](https://github.com/sidekiq/sidekiq/wiki/Batches) — the steelman on the preempt slide

**Ruby libraries named on the preempt slide**
- [acidic_job](https://github.com/fractaledmind/acidic_job) · [Gush](https://github.com/chaps-io/gush) · [AASM](https://github.com/aasm/aasm) · [Statesman](https://github.com/gocardless/statesman) · [GoodJob](https://github.com/bensheldon/good_job)

**Other durable execution runtimes** (named, not compared)
- [DBOS](https://dbos.dev) · [Restate](https://restate.dev) · [Inngest](https://inngest.com)

**Disclosures to keep true**
- All example code is original. The order-fulfillment scenario is illustrative, not drawn from any employer's system — worth keeping that literally true, since the reconciler joke invites the assumption.
- No affiliation with Temporal or any project listed. If anyone asks whether this is sponsored, say plainly that it isn't.

