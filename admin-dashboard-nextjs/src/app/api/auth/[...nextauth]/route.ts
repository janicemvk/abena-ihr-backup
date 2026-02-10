import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { authenticateUser } from '@/lib/services/authService'

// Note: Authentication now supports multiple admin users
// Users are stored in the Integration Bridge database (admin_users table)
// Default super admin: admin@abena-ihr.com / admin123

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error('Please enter an email and password')
        }

        try {
          // Authenticate via Integration Bridge
          const authResult = await authenticateUser({
            email: credentials.email,
            password: credentials.password,
          })

          if (!authResult.success || !authResult.user) {
            // Provide more detailed error message
            const errorMsg = authResult.error || 'Invalid email or password'
            console.error('Authentication failed:', errorMsg)
            throw new Error(errorMsg)
          }

          return {
            id: authResult.user.id,
            name: authResult.user.name || authResult.user.email,
            email: authResult.user.email,
            role: authResult.user.role,
            bridgeToken: authResult.token, // Store Integration Bridge token
          }
        } catch (error: any) {
          console.error('NextAuth authorize error:', error)
          // If it's a connection error, provide helpful message
          if (error.message?.includes('connect') || error.message?.includes('ECONNREFUSED')) {
            throw new Error('Cannot connect to authentication service. Please ensure the Integration Bridge is running on port 8081.')
          }
          throw error
        }
      },
    }),
  ],
  session: {
    strategy: 'jwt',
    maxAge: 8 * 60 * 60, // 8 hours
    updateAge: 24 * 60 * 60, // 24 hours
  },
  secret: process.env.NEXTAUTH_SECRET || process.env.NODE_ENV === 'production' ? 'abena-ihr-admin-secret-change-in-production-min-32-chars-long' : 'dev-secret-key-for-local-development-only',
  jwt: {
    maxAge: 8 * 60 * 60, // 8 hours
  },
  pages: {
    signIn: '/login',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role
        // Store the Integration Bridge token from the user object
        if ((user as any).bridgeToken) {
          token.bridgeToken = (user as any).bridgeToken
        }
      }
      return token
    },
    async session({ session, token }) {
      if (session?.user) {
        session.user.role = token.role
        // Store bridge token in session for API access
        ;(session as any).bridgeToken = token.bridgeToken
      }
      return session
    },
  },
})

export { handler as GET, handler as POST } 