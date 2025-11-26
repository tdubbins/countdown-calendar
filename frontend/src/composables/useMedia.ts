/**
 * Media Composable - useMedia
 *
 * Handles fetching images and videos with optional authentication.
 * Returns blob URLs for secure media display.
 */

export const useMedia = () => {
  /**
   * Fetch media (image/video) with optional authentication
   *
   * This function fetches media from the API and converts it to a blob URL
   * that can be used in <img> or <video> tags. Blob URLs allow us to:
   * - Fetch protected resources with authentication headers
   * - Display them without exposing the auth token in the URL
   * - Support streaming for videos (via HTTP Range requests)
   *
   * @param url - API endpoint URL (e.g., '/api/calendars/123/videos/1/stream')
   * @param requireAuth - Whether to include JWT authentication header
   * @returns Blob URL for displaying the media (e.g., 'blob:http://localhost:8100/abc-123')
   * @throws Error with user-friendly message if fetch fails
   *
   * Error Codes:
   *   - 403: Day is locked (for non-owners)
   *   - 404: Media not found
   *   - Other: Generic error message
   */
  const fetchMedia = async (url: string, requireAuth: boolean): Promise<string> => {
    const headers: Record<string, string> = {}

    // Add JWT authentication header if required (owner viewing their calendar)
    if (requireAuth) {
      const token = localStorage.getItem('auth_token')
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
    }

    // Fetch media from API with optional authentication
    const response = await fetch(url, { headers })

    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('This day is locked')
      } else if (response.status === 404) {
        throw new Error("This day's surprise is coming soon. Check back later!")
      } else {
        throw new Error(`Failed to load media (${response.status})`)
      }
    }

    // Convert response to blob (binary data)
    const blob = await response.blob()

    // Create blob URL that points to data in browser memory
    // This URL can be used in <img src="..."> or <video src="...">
    // Format: "blob:http://localhost:8100/abc-123-def-456"
    return URL.createObjectURL(blob)
  }

  return {
    fetchMedia
  }
}
