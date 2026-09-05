# TTS practice track — "Your Sidekiq Jobs Have Become a Workflow Engine"

Purpose: generate a reference delivery you can shadow while walking, and a
realistic runtime check. Nine chunks, each under most engines' per-request limit.

## IMPORTANT — why this is timed the way it is

A TTS read with no gaps will finish in ~19 minutes and tell you nothing useful,
because the real talk contains ~16 laughs and several deliberate silences.
The `<break>` tags below ARE the timing. Don't strip them.

Target with breaks included: **24–25 minutes across all nine chunks.**
If your generated total is under 22 min, your engine is ignoring the break tags —
see "If your engine ignores SSML" below.

---

# 1 · VOICE DIRECTION (paste as system prompt / style instruction)

```
You are delivering a 25-minute conference talk to about 200 Ruby developers at a
meetup in Bengaluru, on a Sunday evening. Read the script below aloud.

VOICE
- Male, mid-30s, Indian English. Conversational, not broadcast.
- Technical peer talking to peers. You are one of them, not lecturing them.
- Register: curious and slightly irreverent. Dry, never zany.

PACE
- Roughly 140 words per minute. Unhurried.
- Slow down noticeably for any line on its own paragraph — those are the
  landing lines.
- Speed up slightly through lists and code descriptions; they are connective
  tissue, not the point.

DELIVERY RULES
- Jokes are thrown away, never announced. Do not lift your pitch into a
  punchline. Say the funny line at exactly the same volume as the sentence
  before it, then stop.
- Observe every <break> tag literally. The silences are the timing.
- Questions to the audience are genuine, not rhetorical. Let them hang.
- Never sound like you are selling anything. When the script praises a tool,
  sound like someone reporting a finding, not endorsing a product.
- On self-deprecating lines, sound amused at yourself, not embarrassed.

DO NOT
- Do not add enthusiasm, exclamation, or "presenter energy."
- Do not add filler the script does not contain.
- Do not read stage directions, headers, or anything in square brackets.
```

## Pronunciation

| Written | Say |
|---|---|
| Sidekiq | SIDE-kick |
| idempotent | eye-DEM-po-tent |
| Perham | PURR-ham |
| Matz | Mats |
| Postgres | POST-gress |
| Temporal | TEM-por-al (normal English word) |
| Rubocop | ROO-bo-cop |
| Koramangala | Ko-ra-MUN-ga-la |
| Whitefield | WHITE-field |
| nil:NilClass | "nil, NilClass" |
| perform_async | "perform under-score a-sync" |
| wait_condition | "wait under-score condition" |
| acidic_job | "acidic job" |
| AASM | "A-A-S-M" |
| DBOS | "D-B-oh-S" |

## If your engine ignores SSML

ElevenLabs v3 honours `<break time="2.0s"/>`. OpenAI TTS and some others do not.
Fallback: replace each break tag with that many ellipses on their own line —
`. . . . .` — which most engines render as pauses. Or generate each chunk, then
insert real silence in any audio editor. The gaps matter more than the method.

---

# 2 · SCRIPT

Cue legend — for you, not to be spoken:
`<break time="2.0s"/>` laugh gap · `<break time="1.0s"/>` beat · `<break time="3.0s"/>` the big silence

---

## CHUNK 1 — Open (target 2:00)

It's Sunday. It's six pm. And you are in a room, voluntarily, to hear about background jobs.

I want you to know that I see that. And that I've structured this talk to be shorter than getting from Koramangala to Whitefield.
<break time="2.0s"/>

Two questions before I start. Hands up.

One. Who runs Sidekiq in production?
<break time="2.5s"/>

Right. Most of the room.

Two. And this is the real one. Who has a Sidekiq job with a state machine inside it?
<break time="2.5s"/>

Some of you put your hand up very fast.
<break time="2.0s"/>

Keep that job in your head. We're going to go find it.
<break time="1.0s"/>

Let me start somewhere completely uncontroversial. One line. Generate invoice job, perform under-score a-sync, invoice dot i-d.

That's it. Something happened in a request, we don't want to do it in the request, so we push it to a queue.

This is good code.
<break time="1.0s"/>

I want to be clear about that, because the title has Sidekiq in it, and you're all waiting for the part where I tell you it's bad.

That part isn't coming. There's no twist. Sidekiq is great. Mike Perham is a national treasure of a country I don't live in.
<break time="2.0s"/>

If your problem fits on that one line, write that line and go home.

I'm not going to manufacture a problem so I can sell you a solution. Instead we're going to follow one process. One. And see where it takes us.

---

## CHUNK 2 — Happy path and failure one (target 3:15)

The process is order fulfillment. And before I start — half this room has built this. Watch which step you stopped at.
<break time="1.5s"/>

Version one. One job. Charge the payment, reserve the inventory, ship the order. Three steps, top to bottom.

Genuinely fine. Ships on Monday. Nobody objects in review.

Then reality shows up. Five times. Like it does.
<break time="1.0s"/>

Failure one. Payment succeeds. The worker dies.

Box gets recycled. Deploy goes out. The O-O-M killer. Someone ran a migration on a Friday. Doesn't matter which.

Sidekiq does the correct thing. It retries. So perform runs again, from the top. And charges the customer a second time.

Now, the customer notices this. Customers are extremely good at noticing this. They have never once emailed to say, you charged me half as much as I expected.
<break time="2.0s"/>

So we make it idempotent. Idempotent meaning safe to run twice.

And to be safe to run twice, the job has to know what it already did. Which means it has to write down what it already did.

So we add three columns. Charged. Reserved. Shipped. And we guard each step on its column.
<break time="1.0s"/>

Nobody in the business asked for charged underscore at. No product manager has ever written a ticket that says, as a user, I want a boolean indicating how far through a Sidekiq job I got.
<break time="2.0s"/>

But look at what those columns are.

That is not information about the order.
<break time="1.0s"/>

That is information about how far along the job got.

We just persisted execution state into our domain model. And it was the right call. I'd do it again tomorrow.

But it's the first brick.
<break time="1.0s"/>

And no, you can't wrap this in a transaction. Because the payment gateway is not in your database.

That's the entire problem. The moment a step touches the outside world, ActiveRecord dot transaction stops being the thing that saves you. And for most of us that's genuinely upsetting, because it's been the thing that saves us since we started writing Rails.
<break time="2.0s"/>

---

## CHUNK 3 — Failure two and the program counter (target 2:15)

Failure two. The warehouse takes two days to confirm.

A worker cannot sit there for two days. It's a thread. It has a timeout. And it will be killed by the next deploy, which at most companies is about eleven minutes away.
<break time="2.0s"/>

Somebody always suggests sleep two days at this point. Usually as a joke.
<break time="1.0s"/>

Usually.
<break time="2.0s"/>

So we split the job. Check warehouse job. If the warehouse is ready, ship it. Otherwise, schedule myself again in an hour.

A job that schedules itself.

All of you have written this. Some of you wrote it this week. Some of you are looking at your laptop right now.
<break time="2.0s"/>

And look at what it actually is. That's a timer.

We had no way to wait. So we built waiting out of the parts we had. A scheduler, and a queue.

Also, quietly, the status column is now doing real work. It isn't describing the order any more. It's telling the next job where to resume.
<break time="1.5s"/>

It's a program counter.
<break time="1.5s"/>

In your orders table. With an index on it.
<break time="2.0s"/>

And I want to be precise about what I'm claiming here. I'm not saying our Rails code got ugly. The code is fine. The code is nice.

I'm saying we introduced a concept.
<break time="1.0s"/>

And nobody decided to.
<break time="1.5s"/>

---

## CHUNK 4 — Montage and the reconciler (target 2:00)

Three more. Faster. Because you already know how these go.

Three. The warehouse sends a callback instead. Better. Except, now, how does the callback find the order? Add a token. What if it arrives twice? Add a dedup table. What if it arrives before we committed the row?

Then you get, undefined method for nil, NilClass. Which, as we all know, is the national anthem of this ecosystem.
<break time="2.0s"/>

And you fix it with a lock. Or a retry. Or a sleep zero point five that you tell nobody about.
<break time="1.5s"/>

Four. We deploy mid-flight. There are orders in the queue right now, halfway through, serialized with the old arguments.

So you version the payload. Or drain the queue. Or write the compatibility shim, with the comment on it that says, to-do, remove after migration, March twenty twenty-four.
<break time="2.0s"/>

Five. The customer cancels. After payment. Before shipping.

Now you have to stop a process that isn't running. It's a row in Redis with a timestamp on it. And you have to undo a charge.

That's compensation. The undo you write yourself. Usually the week after someone from finance asks a very calm question.
<break time="2.0s"/>

And somewhere in here, someone writes the reconciler. Runs every ten minutes. Do not delete. Ask Anubhav before changing this.
<break time="1.0s"/>

Anubhav doesn't work here any more.
<break time="2.5s"/>

Every company I've worked at has this job. It always has that comment.

And git blame always says it was me.
<break time="2.5s"/>

---

## CHUNK 5 — The realization (target 2:30)

So let's put it on one slide. Not the business logic. Just the machinery we added to keep the process alive.

Retries. Scheduling. Queues. State columns. Idempotency guards. Callback dedup. Polling. Payload versioning. Compensation. Reconciliation.
<break time="2.0s"/>

Every one of those was a good decision. I'd defend all of them in code review. None of them is wrong.

But look at the shape.

State. Timers. Retries. External events. Recovery. Compensation.
<break time="1.5s"/>

That is not a job any more.
<break time="2.0s"/>

We didn't set out to build a workflow engine. We just kept solving the next requirement.
<break time="2.0s"/>

And nobody's name is on it. There was never a ticket that said, build workflow engine. It arrived one pull request at a time, over about eighteen months. And every one of those was small enough to approve on your phone.
<break time="2.5s"/>

It also has a class name. It's usually something like, class definitely not a workflow, inherits from application job. Eight hundred and forty-seven lines.
<break time="2.5s"/>

So let me draw the line that actually matters.

A job says, please do this. Send the email. Resize the image. Sync the record. Short. Discrete. Retry it as a unit.

A workflow says, make sure this eventually completes. Onboarding. Fulfillment. Payment lifecycle.

Those have state. Time. Events. Compensation.

And it's a spectrum, not two boxes. Nothing happens when you cross it. No alarm goes off. Nobody gets paged. Rubocop does not have a rule for this.
<break time="2.0s"/>

Which is exactly why you end up on the wrong side of it without noticing.
<break time="1.5s"/>

A workflow is what a job gradually turns into.
<break time="2.5s"/>

---

## CHUNK 6 — Preempt, durable execution, mapping (target 3:15)

Now. Some of you have been quietly furious for about five minutes, going, yes, and that's why Sidekiq Pro has Batches.

You're right. Let me put them all on the screen, because I'm not building a strawman, and this is Ruby. There is always a gem for it. Usually four. And two are unmaintained.
<break time="2.0s"/>

Batches. Acidic job. Gush. A-A-S-M. Statesman. GoodJob.

These are good. Batches gives you fan-out and callbacks. Acidic job gives you real step-level idempotency. Statesman gives you an auditable state machine.

If you're not using them, some of you should leave now and go use them. I won't be offended.
<break time="2.0s"/>

But notice what they do. Each one makes a step better.

None of them fundamentally changes who owns keeping the process alive. It's still your app. Your Postgres. Your reconciler. Your phone at three a.m.

That's not a criticism. That's the question of this talk.
<break time="1.5s"/>

So here's the question. What if keeping the process alive was the runtime's job instead of ours?

Not the business logic. The machinery. State. Timers. Retries. Resumption. History.

That idea has a name. Durable execution.

You write the process as ordinary sequential code. And when the machine running it dies, the process doesn't.
<break time="1.0s"/>

There are several systems doing this. Temporal. D-B-oh-S. Restate. Inngest.

I'm not going to compare them. I picked one and looked at it properly. And I picked Temporal for a boring reason that matters to this room. The Ruby S-D-K went generally available last October. Fully supported. Same features as Go and Java.

Which means, for once, we are not standing outside the window watching the Java people have a nice time.
<break time="2.0s"/>

Three words. Then code. Only three.

Workflow. Decides what happens next. Your orchestration.
Activity. Touches the outside world. Charges the card.
Worker. The process you run that executes both.

Everything else is day two.
<break time="1.0s"/>

Now, the same process, written against that runtime.

Don't look at how short it is. Line count is a cheap argument, and I refuse to make it.

Look at one line. Wait under-score condition. That's the two-day wait. No scheduler. No re-enqueue. No status column. And it isn't holding a thread. The runtime puts the workflow away, and brings it back when something happens.

That's the actual claim. Not fewer lines.
<break time="1.0s"/>

Waiting became a language feature.
<break time="2.0s"/>

And before anyone has to decode that — you already wrote all of this. Every line of it. Just in a different shape.

The guards you added? The runtime already knows. It's in the history.

The job that re-enqueued itself every hour? That's the one line. Wait condition.

The callback token and the dedup table? That's a signal. Second one arrives, the workflow has already moved on.

The status column doing double duty as a program counter? That's just where the code is.
<break time="1.5s"/>

And the reconciler.
<break time="2.0s"/>

There isn't a row for that one.
<break time="2.0s"/>

---

## CHUNK 7 — The experiment (target 4:45)

So here's the actual comparison, and it isn't about syntax.

Who owns keeping this process alive?
<break time="1.5s"/>

In the first half of this talk, the answer was, me.
<break time="1.0s"/>

My columns. My scheduler. My dedup table. My reconciler. My phone.

And I want to be fair to myself. I did a decent job of it. It worked.
<break time="1.0s"/>

Here, the answer is, the runtime.
<break time="1.5s"/>

That's it. That's the entire trade being offered. Everything else is detail.
<break time="1.5s"/>

So I built the same process twice. Same requirements. Same five failures. Then I broke both on purpose.

I'm not running this live at six pm on a Sunday. You're welcome.
<break time="2.0s"/>

First. Kill the worker, right after payment.

Sidekiq retries, hits my idempotency guards, and — this is the important part — it works. It genuinely works. Because I wrote the guards.

The recovery is correct because I made it correct. And I stay responsible for that every time someone adds a fourth step. Which they will. On a Friday.
<break time="2.0s"/>

Temporal. Another worker picks up the execution and continues after the payment activity. I didn't write recovery code.
<break time="1.0s"/>

There is no recovery code to show you. That's the whole slide.

Same outcome. Completely different answer to who is responsible for it.
<break time="1.5s"/>

Second. The warehouse fires the callback twice.

Sidekiq. Dedup table. Unique index. And a philosophical debate about whether twice means a duplicate event or a retry. A debate that will happen in a pull request thread, and will involve at least one person quoting the H-T-T-P spec.
<break time="2.0s"/>

Temporal. Same signal arrives twice. The workflow is already past that wait. Second one is a no-op.

Not magic. Somebody still wrote that logic. The question is only whether it was you. At two a.m. Under a deadline.
<break time="1.5s"/>

And the forty-eight hour wait. I'm not demoing that. And how I would have demoed it is the finding.

Temporal's test environment skips time. You ask it to jump forty-eight hours, and it does.

On the Sidekiq side, I had to fake the clock and fire the cron by hand.
<break time="1.0s"/>

I built a fake clock to test my fake timer.
<break time="2.5s"/>

So here's the only scoreboard I care about. Retry. Timer. Workflow state. External events. Recovery. Orchestration. Business logic. Side effects.

Two rows matter.

Business logic doesn't move. Nothing here makes your domain simpler. And anyone who tells you otherwise is doing a webinar.
<break time="2.0s"/>

And recovery moves. That's the row you're actually buying.
<break time="1.0s"/>

Oh — and the question I get most, which is a good one. What's the difference between a workflow and an activity?

An activity touches the outside world. A workflow decides what happens next. That's the whole split.

---

## CHUNK 8 — What did we buy (target 3:00)

So that's the good part.

Now the honest part. Because that table made it look free, and it is not.
<break time="1.0s"/>

The one you hit on day one. Determinism.

Workflow code is not ordinary Ruby. The runtime reconstructs the workflow's state by replaying its recorded history against your workflow code. So your code has to produce the same decisions, given the same history, every time.

Which means it can't ask the outside world anything mid-decision.

So, inside workflow code — Time dot now is a bug. Secure random is a bug. Rand is a bug. And Order dot find is a bug.
<break time="1.5s"/>

Read that again. Time dot now. Order dot find.

The two most ordinary things in Rails. And inside a workflow, they're bugs.

Matz optimised Ruby for developer happiness. This is the one corner of it that was optimised for a distributed systems paper.
<break time="2.0s"/>

That's not a footnote. That's a genuinely new rule your whole team holds in their head, forever, in a language where nothing else behaves that way.
<break time="1.0s"/>

And then the rest of the bill.

Another runtime. It's not Rails, Postgres, Redis any more. Someone operates this. Self-hosted, it's a real service with a real datastore. Cloud, it's a bill, and a vendor, and a procurement conversation.

Debugging changes shape. You're not reading a stack trace. You're reading an execution history. Often better — you can see exactly what happened to one order six weeks ago. But it is not the skill your team has today. And binding dot pry is not going to help you.
<break time="2.0s"/>

Versioning becomes first-class. Old executions are still in flight when you deploy, and the runtime makes you handle that explicitly. Which is more honest than the shim with the comment on it. But more honest, and less work, are different things.
<break time="2.0s"/>

And the one nobody puts on a slide. Your organisation now has one more thing it has to understand. Every new hire. Every incident. Every person you wake up.
<break time="1.0s"/>

A technology can reduce your application complexity and increase your system complexity at the same time.

That's a legitimate trade. It's just a trade. Know which side of it you're on when you make it.

---

## CHUNK 9 — Close (target 2:00)

So. Where does that leave us.

If your work is short, independent, stateless, retryable as a unit, fire and forget — that's a job. Sidekiq isn't just adequate there, it's correct. And adding a runtime would be making your own life worse on purpose.

There's a word for adding distributed systems you don't need. It's usually on someone's promotion packet.
<break time="2.0s"/>

But if it's multi-step. Long-running. Stateful. Waiting on external events. Waiting on humans. Needing compensation. And — this is the tell — if it keeps accumulating orchestration code around it.

Then you may already be running a workflow engine. You're just also the one maintaining it. At three a.m. Without documentation.
<break time="1.5s"/>

And owning it is a real answer. Postgres is extremely good. A state machine and a well-written reconciler have kept a lot of serious companies alive. If your process fits in your head, keeping it in Rails is the better engineering decision, and I'd defend that too.
<break time="1.0s"/>

The idea I want to leave you with isn't about Temporal at all.

An abstraction is useful, right up until you start implementing the abstraction it was supposed to give you.
<break time="2.0s"/>

Sidekiq gives you a job abstraction. It's a great abstraction. But if your application has ended up implementing state, and waiting, and orchestration, and recovery, and timers, and events — then whatever you're holding stopped being a job a while ago.
<break time="1.5s"/>

So. That job you thought of when I asked at the start. The one some of you raised your hand for very fast.

Go and open it tomorrow.

And if there's a comment on it with someone's name — and that person doesn't work there any more —
<break time="2.0s"/>

that's your answer.
<break time="1.5s"/>

Is this still a job?
<break time="3.0s"/>

I don't know, for your system.

I think you do.
<break time="2.0s"/>

Thank you.

---

# 3 · HOW TO PRACTICE WITH IT

1. Generate all nine chunks. Note each duration. Total should land 24–25 min.
   If a chunk runs long, that's the section to trim — the audio tells you
   something a silent read never will.
2. **First pass — listen only.** Walking, not at a desk. You're checking whether
   the argument holds without slides. If a section bores you listening, it will
   bore them watching.
3. **Second pass — shadow it.** Speak along half a beat behind. This trains
   pacing far faster than solo rehearsal, especially the throwaway jokes,
   which are the thing people get wrong by pushing.
4. **Third pass — mute the audio at each section start** and deliver it
   yourself, then unmute to compare.

What the TTS will NOT teach you: eye contact, the hands-up poll, pointing at
yourself on "me", and where the real laughs land. Those only come from
the stopwatch runthrough standing up.

