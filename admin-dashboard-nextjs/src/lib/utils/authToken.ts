/**
 * Auth Token Utility
 * Helper functions to get the Integration Bridge token from NextAuth session
 */

import { getSession } from 'next-auth/react'

/**
 * Get the Integration Bridge token from NextAuth session
 * This token is stored in the session after login
 */
export async function getBridgeToken(): Promise<string | null> {
  try {
    const session = await getSession()
    if (session && (session as any).bridgeToken) {
      return (session as any).bridgeToken
    }
    return null
  } catch (error) {
    console.error('Error getting bridge token:', error)
    return null
  }
}

/**
 * Get the Integration Bridge token synchronously (for use in hooks)
 * Returns null if called outside of a component context
 */
export function getBridgeTokenSync(): string | null {
  // This is a fallback - should use getBridgeToken() in most cases
  // For client-side synchronous access, we'd need to use useSession hook
  return null
}

