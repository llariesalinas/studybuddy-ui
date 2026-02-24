<template>
  <div style="padding: 40px;">
    <h1>Test API Connection</h1>

    <input v-model="newMessage" placeholder="Enter message" />
    <button @click="sendMessage">Send</button>

    <hr />

    <button @click="loadMessages">Load Messages</button>

    <ul v-if="messages.length">
      <li v-for="msg in messages" :key="msg.id">
        {{ msg.message }}
      </li>
    </ul>

    <p v-else>No messages yet.</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const messages = ref([])
const newMessage = ref('')

const loadMessages = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/test/')
  const data = await response.json()
  messages.value = data
}

const sendMessage = async () => {
  await fetch('http://127.0.0.1:8000/api/test/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: newMessage.value
    })
  })

  newMessage.value = ''
  loadMessages()
}
</script>
