import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const apiGet = vi.fn()
const apiPost = vi.fn()
const apiPatch = vi.fn()
let authStore

vi.mock('@/services/api/api', () => ({
  default: {
    get: apiGet,
    post: apiPost,
    patch: apiPatch,
  },
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStore,
}))

const { useChatStore, clearChatCache } = await import('./chat')

class MockWebSocket {
  static OPEN = 1
  static instances = []

  constructor(url) {
    this.url = url
    this.readyState = MockWebSocket.OPEN
    this.send = vi.fn()
    this.close = vi.fn(() => {
      this.readyState = 3
      this.onclose?.()
    })
    MockWebSocket.instances.push(this)
  }
}

const makeDeferred = () => {
  let resolve
  let reject
  const promise = new Promise((promiseResolve, promiseReject) => {
    resolve = promiseResolve
    reject = promiseReject
  })

  return { promise, resolve, reject }
}

const historyCacheKey = (userId, roomId) => `sb-chat-${userId}-room-${roomId}-history`

const writeHistoryCache = (userId, roomId, messages, overrides = {}) => {
  window.sessionStorage.setItem(
    historyCacheKey(userId, roomId),
    JSON.stringify({
      messages,
      latestMessageId: messages.reduce(
        (latest, message) => Math.max(latest, Number(message.id)),
        0,
      ),
      roomUpdatedAt: null,
      userId: String(userId),
      cachedAt: Date.now(),
      expiresAt: Date.now() + 60_000,
      ...overrides,
    }),
  )
}

describe('chat store history cache', () => {
  beforeEach(() => {
    vi.useRealTimers()
    setActivePinia(createPinia())
    apiGet.mockReset()
    apiPost.mockReset()
    apiPatch.mockReset()
    MockWebSocket.instances = []
    vi.stubGlobal('WebSocket', MockWebSocket)
    window.sessionStorage.clear()
    window.localStorage.clear()
    authStore = {
      user: {
        id: 7,
        profile_id: 70,
        role: 'tutee',
      },
      token: 'test-token',
      isAuthenticated: true,
    }
    clearChatCache()
  })

  it('renders cached history before the network sync finishes', async () => {
    const roomId = 12
    const cachedMessage = {
      id: 101,
      room: roomId,
      content: 'Cached hello',
      sender_id: 22,
      is_me: false,
      created_at: '2026-06-06T00:00:00Z',
    }
    const freshMessage = {
      id: 102,
      room: roomId,
      content: 'Network hello',
      sender_id: 22,
      is_me: false,
      created_at: '2026-06-06T00:01:00Z',
    }
    const deferred = makeDeferred()

    writeHistoryCache(7, roomId, [cachedMessage])
    apiGet.mockReturnValueOnce(deferred.promise)

    const request = useChatStore().fetchHistory(roomId, { preferCache: true })

    expect(useChatStore().messages).toEqual([cachedMessage])
    expect(apiGet).toHaveBeenCalledWith(`chat/rooms/${roomId}/history/`, {
      params: { after_id: 101 },
    })

    deferred.resolve({ data: [freshMessage] })
    await request

    expect(useChatStore().messages.map((message) => message.content)).toEqual([
      'Cached hello',
      'Network hello',
    ])
  })

  it('sends after_id when cached history has a high-water mark', async () => {
    const roomId = 14

    writeHistoryCache(
      7,
      roomId,
      [
        {
          id: 35,
          room: roomId,
          content: 'Already cached',
          sender_id: 8,
          is_me: false,
        },
      ],
      {
        latestMessageId: 88,
      },
    )
    apiGet.mockResolvedValueOnce({ data: [] })

    await useChatStore().fetchHistory(roomId, { preferCache: true })

    expect(apiGet).toHaveBeenCalledWith(`chat/rooms/${roomId}/history/`, {
      params: { after_id: 88 },
    })
  })

  it('excludes pending, failed, and temp-only messages from sessionStorage', async () => {
    const roomId = 18
    const store = useChatStore()

    writeHistoryCache(7, roomId, [
      {
        id: 1,
        room: roomId,
        content: 'Cached stable',
        sender_id: 8,
        is_me: false,
      },
    ])
    store.messages = [
      {
        id: 1,
        room: roomId,
        content: 'Cached stable',
        sender_id: 8,
        is_me: false,
      },
      {
        id: 'temp_pending',
        temp_id: 'temp_pending',
        room: roomId,
        content: 'Pending optimistic',
        sender_id: 7,
        is_me: true,
        pending: true,
        failed: false,
      },
      {
        id: 2,
        temp_id: 'temp_failed',
        room: roomId,
        content: 'Failed optimistic',
        sender_id: 7,
        is_me: true,
        pending: false,
        failed: true,
      },
      {
        id: 'temp_only',
        temp_id: 'temp_only',
        room: roomId,
        content: 'Temp only',
        sender_id: 7,
        is_me: true,
        pending: false,
        failed: false,
      },
      {
        id: 3,
        temp_id: 'temp_saved',
        room: roomId,
        content: 'Saved optimistic',
        sender_id: 7,
        is_me: true,
        pending: false,
        failed: false,
      },
    ]
    apiGet.mockResolvedValueOnce({ data: [] })

    await store.fetchHistory(roomId)

    const cachedMessages = JSON.parse(
      window.sessionStorage.getItem(historyCacheKey(7, roomId)),
    ).messages

    expect(cachedMessages.map((message) => message.id)).toEqual([1, 3])
    expect(cachedMessages.every((message) => !message.pending)).toBe(true)
    expect(cachedMessages.every((message) => !message.failed)).toBe(true)
    expect(cachedMessages.every((message) => !message.temp_id)).toBe(true)
  })

  it('updates cached read state when a read receipt arrives for the active room', () => {
    const roomId = 22
    const store = useChatStore()

    store.currentRoom = { id: roomId, updated_at: '2026-06-06T00:00:00Z' }
    store.messages = [
      {
        id: 201,
        room: roomId,
        content: 'Mine',
        sender_id: 7,
        is_me: true,
        is_read: false,
      },
      {
        id: 202,
        room: roomId,
        content: 'Theirs',
        sender_id: 8,
        is_me: false,
        is_read: false,
      },
    ]

    store.connectToRoom(roomId)
    MockWebSocket.instances[0].onmessage({
      data: JSON.stringify({
        type: 'read_receipt',
        room_id: roomId,
        reader_id: 8,
      }),
    })

    expect(store.messages.find((message) => message.id === 201).is_read).toBe(true)
    expect(store.messages.find((message) => message.id === 202).is_read).toBe(false)

    const cachedMessages = JSON.parse(
      window.sessionStorage.getItem(historyCacheKey(7, roomId)),
    ).messages

    expect(cachedMessages.find((message) => message.id === 201).is_read).toBe(true)
    expect(cachedMessages.find((message) => message.id === 202).is_read).toBe(false)
  })
})
