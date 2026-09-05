<script setup>
defineProps({
  n:   { type: Number, required: true },
  big: { type: Boolean, default: false },
})
</script>

<template>
  <div v-if="!big" class="just-quiet">JUST × {{ n }}</div>
  <div v-else class="just-loud">JUST × {{ n }}</div>
</template>

<style scoped>
/* Quiet mode: identical position on every slide, low enough contrast that
   nobody consciously reads it until the payoff. Do not animate. */
.just-quiet {
  position: absolute;
  right: 2.2rem;
  bottom: 1.5rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  opacity: 0.26;
  user-select: none;
  z-index: 5;
}

/* Payoff mode: same string, suddenly the loudest thing on the slide. */
.just-loud {
  position: absolute;
  right: 2.2rem;
  bottom: 1.5rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 2.6rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  opacity: 1;
  user-select: none;
  z-index: 5;
}
</style>
