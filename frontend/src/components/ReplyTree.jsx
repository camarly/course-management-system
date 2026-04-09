/**
 * Recursive reply tree component.
 *
 * Renders a thread's reply tree with visual indentation per nesting level.
 * Calls itself recursively for each reply's children array.
 *
 * Props:
 *   replies        Array<Reply>
 *   threadId       number  (needed to post a direct thread reply)
 *   depth          number  (current nesting depth, starts at 0)
 *   onReplyPosted  () => void  (callback to refresh the tree)
 *
 * Reply shape: { id, body, created_by_username, created_at, children: Array<Reply> }
 *
 * Style input requested from: Tramonique Wellington
 * Owner: Camarly Thomas
 */
