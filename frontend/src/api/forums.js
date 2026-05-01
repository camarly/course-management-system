/**
 * Forums, Threads, and Replies API module.
 *
 * Owner: Camarly Thomas
 */

import client from './client'

export async function getForums(courseId) {
  const { data } = await client.get(`/courses/${courseId}/forums`)
  return data.data
}

export async function createForum(courseId, payload) {
  const { data } = await client.post(`/courses/${courseId}/forums`, payload)
  return data.data
}

export async function getThreads(forumId) {
  const { data } = await client.get(`/forums/${forumId}/threads`)
  return data.data
}

export async function createThread(forumId, payload) {
  const { data } = await client.post(`/forums/${forumId}/threads`, payload)
  return data.data
}

export async function getThread(threadId) {
  const { data } = await client.get(`/threads/${threadId}`)
  return data.data
}

export async function replyToThread(threadId, payload) {
  const { data } = await client.post(`/threads/${threadId}/replies`, payload)
  return data.data
}

export async function replyToReply(replyId, payload) {
  const { data } = await client.post(`/replies/${replyId}/replies`, payload)
  return data.data
}
