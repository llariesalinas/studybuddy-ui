<template>
  <div class="session-aurora" aria-hidden="true">
    <i class="session-aurora-blob session-aurora-blob-primary"></i>
    <i class="session-aurora-blob session-aurora-blob-yellow"></i>
    <i class="session-aurora-blob session-aurora-blob-pink"></i>
    <i class="session-aurora-blob session-aurora-blob-violet"></i>
  </div>
</template>

<style scoped>
.session-aurora {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

.session-aurora-blob {
  position: absolute;
  display: block;
  border-radius: 50%;
  filter: blur(46px);
  opacity: 0.5;
}

.session-aurora-blob-primary {
  left: -16%;
  top: -8%;
  width: 60%;
  height: 34%;
  background: radial-gradient(circle, var(--sb-primary), transparent 70%);
  animation: session-aurora-drift-one 14s ease-in-out infinite alternate;
}

.session-aurora-blob-yellow {
  right: -18%;
  top: 24%;
  width: 58%;
  height: 34%;
  background: radial-gradient(circle, var(--sb-pop-yellow), transparent 70%);
  animation: session-aurora-drift-two 17s ease-in-out infinite alternate;
}

.session-aurora-blob-pink {
  left: -14%;
  top: 52%;
  width: 62%;
  height: 34%;
  background: radial-gradient(circle, var(--sb-pop-pink), transparent 70%);
  animation: session-aurora-drift-three 19s ease-in-out infinite alternate;
}

.session-aurora-blob-violet {
  right: -14%;
  top: 78%;
  width: 56%;
  height: 36%;
  background: radial-gradient(circle, var(--sb-aurora-violet), transparent 70%);
  animation: session-aurora-drift-one 22s ease-in-out infinite alternate;
}

@keyframes session-aurora-drift-one {
  to {
    transform: translate(8%, 6%) scale(1.15);
  }
}

@keyframes session-aurora-drift-two {
  to {
    transform: translate(-7%, 8%) scale(1.2);
  }
}

@keyframes session-aurora-drift-three {
  to {
    transform: translate(6%, -7%) scale(1.12);
  }
}

@media (prefers-reduced-motion: reduce) {
  .session-aurora-blob {
    animation: none;
  }
}
</style>
