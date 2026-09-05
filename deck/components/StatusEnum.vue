<script setup>
defineProps({
  stage: { type: Number, required: true },
})

const stages = {
  1: `enum status: %i[pending shipped]`,
  2: `enum status: %i[pending charged reserved shipped]`,
  3: `enum status: %i[pending charged reserved
                awaiting_warehouse shipped]`,
  4: `enum status: %i[pending charging charged charge_failed
                charge_retrying reserved reservation_failed
                awaiting_warehouse warehouse_timed_out
                shipping shipped cancelling cancelled
                refund_pending refunded stuck]`,
}
</script>

<template>
  <pre class="status-enum">{{ stages[stage] }}</pre>
</template>

<style scoped>
/* Opposite corner from the JUST counter. Never referenced out loud.
   The audience notices it grow on their own, or they don't — both fine. */
.status-enum {
  position: absolute;
  left: 2.2rem;
  bottom: 1.5rem;
  margin: 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.62rem;
  line-height: 1.35;
  letter-spacing: 0.01em;
  opacity: 0.24;
  user-select: none;
  white-space: pre;
  z-index: 5;
}
</style>
