import type { NextAuthOptions, Profile } from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import FacebookProvider from 'next-auth/providers/facebook';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

/** Login with Amazon (LWA) — native OAuth2, no extra package needed. */
function makeAmazonProvider() {
  return {
    id: 'amazon',
    name: 'Amazon',
    type: 'oauth' as const,
    authorization: {
      url: 'https://www.amazon.com/ap/oa',
      params: { scope: 'profile' },
    },
    token: 'https://api.amazon.com/auth/o2/token',
    userinfo: 'https://api.amazon.com/user/profile',
    clientId: process.env.AMAZON_CLIENT_ID!,
    clientSecret: process.env.AMAZON_CLIENT_SECRET!,
    checks: ['state' as const],
    profile(profile: Record<string, string>) {
      return { id: profile.user_id, name: profile.name, email: profile.email };
    },
  };
}

function buildProviders() {
  const providers = [];

  if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
    providers.push(
      GoogleProvider({
        clientId: process.env.GOOGLE_CLIENT_ID,
        clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      })
    );
  }

  if (process.env.FACEBOOK_APP_ID && process.env.FACEBOOK_APP_SECRET) {
    providers.push(
      FacebookProvider({
        clientId: process.env.FACEBOOK_APP_ID,
        clientSecret: process.env.FACEBOOK_APP_SECRET,
      })
    );
  }

  if (process.env.AMAZON_CLIENT_ID && process.env.AMAZON_CLIENT_SECRET) {
    providers.push(makeAmazonProvider());
  }

  if (
    process.env.APPLE_ID &&
    process.env.APPLE_TEAM_ID &&
    process.env.APPLE_PRIVATE_KEY &&
    process.env.APPLE_KEY_ID
  ) {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const AppleProvider = require('next-auth/providers/apple').default;
    providers.push(
      AppleProvider({
        clientId: process.env.APPLE_ID,
        clientSecret: {
          appleId: process.env.APPLE_ID,
          teamId: process.env.APPLE_TEAM_ID,
          privateKey: process.env.APPLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
          keyId: process.env.APPLE_KEY_ID,
        },
      })
    );
  }

  return providers;
}

export const authOptions: NextAuthOptions = {
  providers: buildProviders(),
  pages: { signIn: '/', error: '/' },
  callbacks: {
    /** After OAuth success: create/look up the backend user, store token on the User object. */
    async signIn({ user }) {
      if (!user.email) return true;
      try {
        const res = await fetch(`${API_BASE}/api/users`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: user.name ?? '', email: user.email }),
        });
        if (res.ok) {
          const data: { user_id: string; token: string } = await res.json();
          user.backendUserId = data.user_id;
          user.backendToken = data.token;
        }
      } catch {
        /* backend unavailable — still allow login, backend token will be absent */
      }
      return true;
    },

    /** Persist backend credentials into the JWT cookie. */
    async jwt({ token, user }) {
      if (user?.backendUserId) token.backendUserId = user.backendUserId;
      if (user?.backendToken) token.backendToken = user.backendToken;
      return token;
    },

    /** Expose backend credentials to client-side useSession(). */
    async session({ session, token }) {
      if (token.backendUserId) session.user.backendUserId = token.backendUserId;
      if (token.backendToken) session.user.backendToken = token.backendToken;
      return session;
    },
  },
};
