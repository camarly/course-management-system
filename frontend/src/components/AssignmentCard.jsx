/**
 * Assignment card component.
 *
 * Displays a single assignment summary:
 *   - Title, due date, weight
 *   - Student: submission status + grade if available
 *   - Lecturer: number of submissions received
 *
 * Props:
 *   assignment   { id, title, due_date, weight }
 *   submission   { file_url, submitted_at } | null
 *   grade        { score, feedback } | null
 *   role         'student' | 'lecturer' | 'admin'
 *
 * Style input requested from: Carl Heron
 * Owner: Camarly Thomas
 */
