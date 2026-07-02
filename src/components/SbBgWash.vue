<template>
  <div class="sb-bg-wash" aria-hidden="true">
    <i class="sb-bg-wash__blob sb-bg-wash__blob--1"></i>
    <i class="sb-bg-wash__blob sb-bg-wash__blob--2"></i>
    <i class="sb-bg-wash__blob sb-bg-wash__blob--3"></i>
  </div>
</template>

<style scoped>
.sb-bg-wash {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
  background: linear-gradient(
    180deg,
    var(--sb-aurora-wash-start) 0%,
    var(--sb-bg) 42%,
    var(--sb-aurora-wash-end) 100%
  );
}

.sb-bg-wash__blob {
  position: absolute;
  display: block;
}

.sb-bg-wash__blob--1 {
  left: -25vw;
  top: -14vh;
  width: 150vw;
  height: 58vh;
  background: var(--sb-wash-blob-1);
}

.sb-bg-wash__blob--2 {
  right: -30vw;
  top: 20vh;
  width: 135vw;
  height: 50vh;
  background: var(--sb-wash-blob-2);
}

.sb-bg-wash__blob--3 {
  left: -22vw;
  bottom: -18vh;
  width: 145vw;
  height: 52vh;
  background: var(--sb-wash-blob-3);
}
</style>
