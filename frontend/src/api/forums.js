/**
 * Forums, Threads, and Replies API module.
 *
 * Functions:
 *   getForums(courseId)                     GET  /api/courses/:id/forums
 *   createForum(courseId, payload)          POST /api/courses/:id/forums
 *   getThreads(forumId)                     GET  /api/forums/:id/threads
 *   createThread(forumId, payload)          POST /api/forums/:id/threads
 *   getThread(threadId)                     GET  /api/threads/:id  (includes nested replies)
 *   replyToThread(threadId, payload)        POST /api/threads/:id/replies
 *   replyToReply(replyId, payload)          POST /api/replies/:id/replies
 *
 * Owner: Camarly Thomas
 */

import client from './client'
