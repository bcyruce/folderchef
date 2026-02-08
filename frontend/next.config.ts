/**
 * FolderChef — Next.js Configuration
 * =====================================
 *
 * This file configures the Next.js framework.
 *
 * WHAT THIS DOES:
 *   - Sets up environment variables accessible in the browser
 *   - Configures image domains (for product images from supermarkets)
 *   - Can set up redirects, rewrites, and other routing rules
 *
 * IMPORTANT:
 *   Only variables prefixed with NEXT_PUBLIC_ are exposed to the browser.
 *   Keep secrets (API keys, etc.) on the server side only.
 */

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* ---------------------------------------------------------------
   * Image Optimisation
   * Next.js can optimise images from external sources.
   * We add the supermarket domains so we can display product images.
   * --------------------------------------------------------------- */
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.ah.nl",
      },
      {
        protocol: "https",
        hostname: "**.jumbo.com",
      },
    ],
  },

  /* ---------------------------------------------------------------
   * Environment Variables
   * These are available in the browser via process.env.NEXT_PUBLIC_*
   * --------------------------------------------------------------- */
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};

export default nextConfig;
