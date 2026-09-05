# Your Sidekiq Jobs Have Become a Workflow Engine

## Talk Intent & Narrative Brief

### BRUG — September 6, 2026

---

## 1. What this talk is about

This talk is **not a Temporal introduction**.

It is not:

> “Here is Temporal, here are its features, and here is why you should use it.”

It is also not:

> “Sidekiq is old and Temporal is the future.”

It is not a benchmark or a feature-by-feature comparison of background job systems.

The intention is to start with something Ruby and Rails developers already know extremely well:

> **Background jobs.**

We know how to enqueue them, retry them, schedule them, make them idempotent, and persist state around them. Over time, we have developed patterns for making increasingly complicated business processes work using these primitives.

The question this talk explores is:

> **What happens when a background job stops being a job and starts becoming a process?**

And, more importantly:

> **At what point does the application begin building a workflow engine around its job system?**

Temporal enters the story only after we have experienced that pain.

It becomes a concrete example of another approach:

> **What if durable execution were provided by the runtime rather than assembled inside the application?**

The audience should leave understanding the idea, the trade-offs, and the alternatives — **not with the feeling that they were sold Temporal.**

---

## 2. The central thesis

The thesis is deliberately nuanced:

> **Sidekiq is very good at executing background jobs. The interesting problem begins when we ask a job system to keep an entire business process alive across failures, time, external events and deployments.**

At that point, we often start adding machinery around the jobs:

```text
Sidekiq
   +
Postgres state
   +
retries
   +
scheduled jobs
   +
callbacks
   +
polling
   +
idempotency
   +
reconciliation
   +
manual recovery
```

None of these individual decisions is necessarily wrong. In fact, they're often the right engineering decisions.

The question is what happens when enough of them accumulate.

We may have effectively created a workflow engine — one that happens to live partly in Rails, partly in Postgres, partly in Sidekiq, and partly in the heads of the engineers maintaining it.

That observation leads naturally to durable execution.

---

## 3. The narrative we want to create

The audience should experience the following progression:

```text
This is easy.
      ↓
Okay, this is getting complicated.
      ↓
But this is still manageable.
      ↓
Wait, why do we have all this state?
      ↓
Why are we scheduling jobs to wait?
      ↓
Why do we need reconciliation?
      ↓
Oh.
      ↓
This is a workflow.
      ↓
Could the runtime own this machinery?
      ↓
Let's investigate.
      ↓
Temporal looks interesting.
      ↓
But what are we giving up?
      ↓
Where would I draw the line?
```

The important thing is that **we don't tell the audience the conclusion at the beginning.**

We let the conclusion emerge from the problem.

---

## 4. Start with the boring thing that works

The opening should establish trust with the audience.

Something as simple as:

```ruby
GenerateInvoiceJob.perform_async(invoice.id)
```

There is nothing wrong with this.

In fact, this is the kind of abstraction we *want*.

We don't want to introduce distributed systems unnecessarily. We don't want to operate another service for something that can be solved with a queue.

The opening position should therefore be:

> **Sidekiq is good. Rails is good. Background jobs are good.**

The talk isn't trying to manufacture a problem in order to justify a solution.

The problem has to **emerge naturally**.

---

## 5. Introduce complexity one requirement at a time

The most important storytelling device is **incremental complexity**.

Start with:

```text
Order placed
    ↓
Process order
```

Then add:

```text
Charge payment
    ↓
Reserve inventory
    ↓
Ship order
```

Still easy.

Then reality starts arriving.

### Failure #1

Payment succeeds. Worker dies.

Now we need to think about:

- idempotency
- retries
- recovery
- transaction boundaries

### Failure #2

The warehouse takes two days.

Now:

- we can't just keep a worker alive
- we need a timer
- or polling
- or a scheduled job
- or persisted state

### Failure #3

Warehouse sends a callback.

Now:

- how does the callback identify the process?
- where does state live?
- what if the callback comes twice?

### Failure #4

We deploy a new version.

Now:

- what happens to processes already in flight?
- can they resume?
- is the new code compatible with the old state?

### Failure #5

Customer cancels.

Now:

- cancellation
- compensation
- potentially reversing previous actions

The point is not to claim that Sidekiq cannot solve these things.

**It absolutely can.**

The point is:

> **We are now building a system around the job system to make the process reliable.**

---

## 6. The realization: we've built a workflow engine

This is the emotional and intellectual pivot.

The audience should look at something like:

```text
Sidekiq
   │
   ├── Retry
   ├── Schedule
   ├── Queue
   │
Rails
   │
   ├── State machine
   ├── Idempotency
   ├── Callbacks
   ├── Polling
   ├── Reconciliation
   └── Recovery
```

and recognize the pattern.

The punchline:

> **“We didn't set out to build a workflow engine.”**

> **“We just kept solving the next requirement.”**

And eventually:

> **“Your Sidekiq jobs have become a workflow engine.”**

This is where the title earns itself.

---

## 7. The crucial distinction: job vs process

### A job

> **“Please do this.”**

Examples:

```text
Send email
Generate PDF
Resize image
Sync record
Refresh cache
```

These are discrete pieces of asynchronous work.

### A workflow

> **“Make sure this process eventually completes.”**

Examples:

```text
Customer onboarding
Order fulfillment
Payment lifecycle
Account provisioning
Data migration
Approval process
```

These have:

- state
- time
- dependencies
- external events
- failures
- retries
- compensation
- human interaction

The distinction is not absolute. It is a spectrum.

The talk should explicitly avoid saying:

> “Jobs bad, workflows good.”

Instead:

> **“A workflow is what a job can gradually turn into.”**

---

## 8. Introduce durable execution as an idea

Only after the audience understands the problem should we introduce:

# Durable execution

The question becomes:

> **What if keeping the process alive was the responsibility of the runtime?**

Today, with conventional background jobs, our application often has to coordinate:

```text
state
timers
retries
callbacks
recovery
next steps
```

A durable execution runtime tries to make those properties part of the execution model.

Conceptually:

```text
              Workflow
                 │
                 ↓
       Durable execution runtime
          │       │       │
       retries  timers  history
          │       │       │
          └───────┼───────┘
                  ↓
             Activities
                  ↓
             Side effects
```

This is the key idea.

**Temporal is not yet the point.**

Durable execution is the point.

---

## 9. Why Temporal becomes the case study

At this point, explicitly say:

> “There are several systems in this space.”

The talk isn't intended to comprehensively compare every workflow engine.

Temporal becomes the concrete implementation we can investigate from the perspective of a Ruby developer.

One practical reason is particularly relevant:

> **Temporal has a GA Ruby SDK.**

That's important because this isn't an abstract architecture discussion for a Go or Java audience.

We're asking:

> **What does durable execution look like if I'm building Rails applications?**

Temporal gives us a concrete way to answer that.

But the framing should remain:

> **Temporal is a case study for the idea, not the answer to the talk.**

---

## 10. The demo should be an experiment

The demo should not be:

> “Let me show you Temporal's API.”

That would turn the talk into a product presentation.

Instead:

> **“Let's build the same problem twice.”**

First:

```text
Rails + Sidekiq
```

Then:

```text
Rails + Temporal
```

The same business process.

The same requirements.

The same failures.

Then deliberately break both.

### Demo failure scenarios

- Kill the worker
- Introduce a timeout
- Send the callback twice
- Make the workflow wait for 48 hours
- Change the code while execution is in progress

The audience should see where the complexity lives in each implementation.

That's the experiment.

---

## 11. The key thing we are measuring

We are **not measuring lines of code**.

We are not measuring:

> “Temporal implementation = 40 lines, Sidekiq implementation = 120 lines.”

That would be too shallow.

We are measuring:

> **Which system owns which responsibility?**

| Concern | Rails + Sidekiq | Durable runtime |
|---|---|---|
| Retry | Job system | Runtime |
| Timer | Scheduler / job | Runtime |
| Workflow state | Application DB | Runtime |
| External event | Callback + state | Workflow interaction |
| Recovery | Application logic | Runtime |
| Orchestration | Application | Workflow |
| Business logic | Application | Application |
| Side effects | Application | Activities |

The interesting question becomes:

> **What responsibilities are we willing to delegate to infrastructure?**

---

## 12. The talk must then turn against the solution

This is essential.

Once the audience sees how much machinery can disappear, immediately ask:

> **“Okay. What did we just buy?”**

Because durable execution is not free.

We have traded one form of complexity for another.

---

## 13. What we gain

The talk should acknowledge the genuine appeal.

### Durable state

The process itself has a durable representation.

### Resumption

A worker can disappear without necessarily meaning that the business process disappeared.

### Timers

Waiting becomes part of the workflow rather than something we have to simulate with scheduled jobs.

### Retries

Retry behavior can become part of execution semantics rather than scattered application logic.

### External events

A long-running process can wait for an external event without us manually building all the state-management machinery around it.

### History

The runtime can retain an execution history that helps answer:

> “What happened to this process?”

These are substantial benefits.

But they are benefits **for a particular class of problem**.

---

## 14. What we lose

This should get equal airtime.

### Another runtime

We're no longer operating only Rails + Postgres + Sidekiq.

We've added infrastructure.

### A new programming model

Developers now need to understand concepts such as:

```text
Workflow
Activity
Worker
Task Queue
Replay
Signals
Workflow History
```

### Determinism

Workflow code isn't simply ordinary Ruby code.

The runtime may replay workflow execution, which imposes constraints on what workflow code can do.

Side effects and external IO need to be separated appropriately.

### Deployment complexity

Long-running processes make code compatibility and versioning a first-class concern.

### Debugging changes

We're no longer just debugging:

```text
exception → stack trace
```

We're debugging an execution history.

### Organizational complexity

The most overlooked cost:

> **Your organization now has another thing it needs to understand.**

A technology can reduce application complexity while increasing **system complexity**.

That's a legitimate trade.

---

## 15. One of the deeper questions: where should state live?

Rails developers are extremely comfortable with:

```text
Postgres
+
ActiveRecord
```

So if a workflow has state, why not simply model it?

For many systems, that may be exactly right.

You can have:

```text
orders
order_states
workflow_events
scheduled_jobs
```

and build a perfectly reliable process.

The alternative is:

> Let the workflow runtime own execution state and history.

Neither is automatically correct.

The talk should ask:

> **When does application-owned state become workflow-runtime-owned state?**

---

## 16. Another deeper question: are we outsourcing business logic?

If the workflow runtime knows:

```text
Payment
Inventory
Shipping
Cancellation
Compensation
```

then infrastructure isn't merely executing code.

It is now participating in the representation of a business process.

Is that desirable?

Maybe.

It can make processes explicit and observable.

But it can also create coupling between:

```text
business process
        ↕
workflow runtime
```

This is worth discussing.

---

## 17. The Rails-specific tension

Rails gives developers an incredibly productive runtime.

The Rails mental model is simple:

```text
Controller
Model
Service
Job
Mailer
Database
```

Introducing durable execution adds another conceptual layer:

```text
Controller
Model
Service
Workflow
Activity
Worker
Runtime
```

That is not necessarily bad.

But it is a cost.

The talk should ask:

> **Is the problem complicated enough to justify another programming model?**

If not, Sidekiq remains the simpler answer.

---

## 18. The talk's decision framework

The audience should leave with a way to reason about their own systems.

Not:

> “Use Temporal if you have more than X jobs.”

Not:

> “Temporal is better at reliability.”

Instead, ask:

### Is this work:

- short-lived?
- independent?
- mostly stateless?
- retryable as a unit?
- fire-and-forget?

Then a job system is probably enough.

But if the work is:

- multi-step
- long-running
- stateful
- dependent on external events
- waiting for humans or systems
- failure-sensitive
- difficult to resume
- requiring compensation
- increasingly surrounded by orchestration code

then:

> **It may be worth evaluating durable execution.**

---

## 19. The audience should make the final decision

The talk should deliberately **not resolve the question universally**.

Instead, leave them with questions.

### When does a job become a workflow?

### How much workflow machinery are we comfortable owning?

### Is Postgres enough?

### When does application-level state become infrastructure-level state?

### Is another runtime worth the operational cost?

### Do we want our infrastructure to understand business processes?

### Is durable execution an abstraction we actually need?

And finally:

> **What would you rather operate?**

```text
500 lines of workflow machinery

              OR

another distributed runtime
```

There is no universally correct answer.

The correct answer depends on the process.

---

## 20. The emotional arc

The audience's emotional progression should roughly be:

### Beginning

> “Yeah, Sidekiq. Obviously.”

### Early middle

> “Yep, we've done that.”

### Middle

> “Wait, that's a lot of machinery.”

### Turning point

> “Oh. That's basically a workflow.”

### Temporal introduction

> “Interesting. The runtime can own that?”

### Demo

> “Oh, that's actually useful.”

### Trade-off section

> “Ah. But there's a cost.”

### Ending

> “Where would *I* draw the line?”

That last question is the goal.

---

## 21. Tone

The tone should be:

**technical + curious + slightly irreverent**

Not:

**vendor presentation + architecture astronaut**

A few jokes and memes should reinforce the narrative rather than distract from it.

For example:

```ruby
class DefinitelyNotAWorkflow < ApplicationJob
  # 847 lines of orchestration
end
```

or:

> **“It's just another Sidekiq job.”**  
> — famous last words

And the recurring joke:

> **“Just add another job.”**

Until the audience realizes that every “just” adds another piece of workflow machinery.

---

## 22. The underlying message

The deepest idea of the talk is not Temporal.

It is this:

> **Abstractions are useful until we start implementing the abstraction they were supposed to give us.**

Sidekiq gives us a job abstraction.

If our application begins implementing:

```text
state
waiting
orchestration
recovery
retries
timers
events
```

then perhaps our actual abstraction isn't a job anymore.

It's a workflow.

And that is the moment where another runtime becomes worth considering.

---

## 23. Final statement

The talk should ultimately arrive here:

> **Your Sidekiq jobs have become a workflow engine.**

Not as an accusation.

Not as a criticism of Sidekiq.

And not as an argument for Temporal.

But as an observation.

Maybe that's perfectly fine.

Maybe your workflow is simple enough that owning it in Rails is the better engineering decision.

Maybe you've accumulated enough machinery that durable execution is exactly the abstraction you're missing.

**The point of the talk is to recognize that boundary.**

So the final question is:

# **Is this still a job?**

And then leave the room to decide.
