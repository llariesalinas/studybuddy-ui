// Demo-only shared-password gate for the Vercel deployment (see ADR-0005).
// Only active when DEMO_BASIC_AUTH_USER/DEMO_BASIC_AUTH_PASSWORD are set as
// Vercel project env vars for the demo environment — leave them unset in the
// real production project so this middleware is a no-op there.
export const config = {
  matcher: '/:path*',
}

export default function middleware(request) {
  const user = process.env.DEMO_BASIC_AUTH_USER
  const password = process.env.DEMO_BASIC_AUTH_PASSWORD

  if (!user || !password) {
    return
  }

  const authHeader = request.headers.get('authorization')
  if (authHeader && authHeader.startsWith('Basic ')) {
    const decoded = atob(authHeader.slice(6))
    const separatorIndex = decoded.indexOf(':')
    const suppliedUser = decoded.slice(0, separatorIndex)
    const suppliedPassword = decoded.slice(separatorIndex + 1)

    if (suppliedUser === user && suppliedPassword === password) {
      return
    }
  }

  return new Response('Authentication required', {
    status: 401,
    headers: { 'WWW-Authenticate': 'Basic realm="Studybuddy Demo"' },
  })
}
