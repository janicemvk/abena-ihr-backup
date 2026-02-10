/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Enable standalone output for Docker
  output: 'standalone',
  // Path-based routing for MVP deployment
  // When deployed to mvp.abenaihr.com/admin, this ensures all routes and assets work correctly
  // Only use basePath in production or when explicitly set
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || '',
  assetPrefix: process.env.NEXT_PUBLIC_ASSET_PREFIX || '',
  // Ensure trailing slash for consistency
  trailingSlash: false,
}

export default nextConfig 