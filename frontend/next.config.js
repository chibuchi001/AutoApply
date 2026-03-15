/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // next-auth requires these at runtime
  // Set NEXTAUTH_URL and NEXTAUTH_SECRET in your .env.local
};


module.exports = nextConfig;
