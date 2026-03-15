import type { DefaultSession } from 'next-auth';
import type { JWT } from 'next-auth/jwt';

declare module 'next-auth' {
  interface User {
    backendUserId?: string;
    backendToken?: string;
  }
  interface Session {
    user: {
      backendUserId?: string;
      backendToken?: string;
    } & DefaultSession['user'];
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    backendUserId?: string;
    backendToken?: string;
  }
}
