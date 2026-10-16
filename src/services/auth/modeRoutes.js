export const MODE_HOME = { tutor: '/tch-dashboard', tutee: '/dashboard' }

export function routeAllowsMode(route, mode) {
  const roles = Array.isArray(route.meta.role) ? route.meta.role : [route.meta.role]
  return !route.meta.role || roles.some((role) => role.toLowerCase() === mode)
}

export async function reconcileRemoteMode(router, role) {
  if (MODE_HOME[role] && !routeAllowsMode(router.currentRoute.value, role)) {
    await router.replace(MODE_HOME[role])
  }
}
