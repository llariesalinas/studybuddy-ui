<template>
  <div class="landing-page bg-white min-vh-100 font-inter">
    
    <nav class="navbar navbar-expand-lg bg-white py-3">
      <div class="container">
        <a class="navbar-brand d-flex align-items-center fw-bold fs-4" href="#">
          <i class="bi bi-book text-sb-primary me-2"></i>
          <span class="text-dark">StudyBuddy</span>
        </a>
        <div class="d-flex gap-3 align-items-center">
          <router-link to="/login" class="text-dark fw-semibold text-decoration-none">Log In</router-link>
          <router-link to="/register" class="btn bg-sb-primary text-white px-4 py-2 rounded-pill fw-semibold shadow-sm">
            Get Started
          </router-link>
        </div>
      </div>
    </nav>

    <section class="hero-section py-5 my-5">
      <div class="container">
        <div class="row align-items-center g-5">
          <div class="col-lg-6">
            <span class="badge bg-success bg-opacity-10 text-sb-primary rounded-pill px-3 py-2 mb-4 fw-semibold border border-success border-opacity-25">
              University Peer Tutoring Network
            </span>
            <h1 class="display-3 fw-bold text-dark mb-4" style="line-height: 1.2;">
              Learn Better, <br>
              <span class="text-sb-primary">Together</span>
            </h1>
            <p class="lead text-muted mb-5 pe-lg-5" style="font-size: 1.15rem;">
              Connect with peer tutors matched to your learning needs. Smart recommendations, flexible scheduling, and fair compensation — all in one platform.
            </p>
            <div class="d-flex gap-3">
              <router-link to="/register" class="btn bg-sb-primary text-white px-4 py-3 rounded-3 fw-semibold shadow-sm d-flex align-items-center">
                Find a Tutor <i class="bi bi-arrow-right ms-2"></i>
              </router-link>
              <router-link to="/register" class="btn btn-outline-dark px-4 py-3 rounded-3 fw-semibold">
                Become a Tutor
              </router-link>
            </div>
          </div>
          
          <div class="col-lg-6">
            <div class="rounded-4 overflow-hidden shadow-lg border border-sb d-flex align-items-center justify-content-center bg-white" style="height: 400px;">
              <img 
                src="@/assets/hero.png"
                alt="StudyBuddy Peer Tutoring Illustration" 
                class="img-fluid w-100 h-100"
                style="object-fit: contain; padding: 20px;"
              >
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="stats-section border-top border-bottom border-sb py-5 bg-sb-bg">
      <div class="container">
        <div class="row text-center g-4">
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">500+</h2>
            <p class="text-muted fw-medium mb-0">Active Tutors</p>
          </div>
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">2,000+</h2>
            <p class="text-muted fw-medium mb-0">Sessions Completed</p>
          </div>
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">4.8</h2>
            <p class="text-muted fw-medium mb-0">Average Rating</p>
          </div>
          <div class="col-6 col-md-3">
            <h2 class="display-5 fw-bold text-sb-primary mb-1">50+</h2>
            <p class="text-muted fw-medium mb-0">Subjects Covered</p>
          </div>
        </div>
      </div>
    </section>

    <section class="features-section py-5 my-5">
      <div class="container">
        <div class="text-center mb-5 pb-3">
          <h2 class="fw-bold text-dark mb-3">Everything You Need to Succeed</h2>
          <p class="text-muted lead mx-auto" style="max-width: 600px;">
            StudyBuddy combines intelligent matching with practical tools to create the best peer tutoring experience.
          </p>
        </div>

        <div class="row g-4">
          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-people text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Smart Tutor Matching</h5>
                <p class="text-muted small mb-0">
                  Our recommender system pairs you with the best peer tutor based on subject needs, ratings, and compatibility.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-calendar3 text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Flexible Scheduling</h5>
                <p class="text-muted small mb-0">
                  View tutor availability in real-time and book sessions that fit your schedule with workload balancing.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-bar-chart text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Earnings & Reports</h5>
                <p class="text-muted small mb-0">
                  Track session history, calculate compensation, and monitor tutoring performance metrics.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card h-100 border-sb shadow-sm rounded-4 p-3 hover-lift">
              <div class="card-body">
                <div class="rounded p-3 bg-success bg-opacity-10 d-inline-block mb-4">
                  <i class="bi bi-clock-history text-sb-primary fs-4"></i>
                </div>
                <h5 class="fw-bold mb-3">Workload Balance</h5>
                <p class="text-muted small mb-0">
                  Automatic workload assessment ensures tutors aren't overloaded, maintaining quality support.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-section bg-sb-primary text-white py-5 text-center">
      <div class="container py-5">
        <h2 class="display-6 fw-bold mb-3">Ready to Start Learning?</h2>
        <p class="lead mb-5 opacity-75">
          Join hundreds of students already benefiting from peer tutoring on StudyBuddy.
        </p>
        <router-link to="/register" class="btn btn-light text-sb-primary px-5 py-3 rounded-3 fw-bold shadow-lg fs-5">
          Sign Up Free
        </router-link>
      </div>
    </section>

  </div>
</template>

<style scoped>
/* Ensure the font matches your design exactly */
.font-inter {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Subtle interactive animation for the feature cards */
.hover-lift {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.hover-lift:hover {
  transform: translateY(-5px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.1) !important;
}

.bg-sb-bg {
  background-color: var(--sb-bg, #F8F9FA);
}
</style>