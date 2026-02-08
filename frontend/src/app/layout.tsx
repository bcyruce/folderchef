/**
 * FolderChef — Root Layout
 * ==========================
 *
 * This is the root layout that wraps EVERY page in the app.
 *
 * WHAT IT DOES:
 *   - Sets up the HTML document structure (<html>, <body>)
 *   - Loads global CSS (Tailwind + custom styles)
 *   - Sets metadata (page title, description) for SEO
 *   - Provides a consistent layout shell across all pages
 *
 * NEXT.JS APP ROUTER:
 *   In Next.js 13+ (App Router), layout.tsx files define shared UI.
 *   The {children} prop is where the actual page content goes.
 *
 * NOTE:
 *   This file CANNOT be a client component. It must be a server component
 *   because it renders the <html> and <body> tags.
 */

import type { Metadata } from "next";
import "./globals.css";

/**
 * Metadata for the entire application.
 *
 * This sets the default <title> and <meta description> tags
 * for SEO (Search Engine Optimisation). Individual pages can
 * override these values.
 */
export const metadata: Metadata = {
  title: "FolderChef — Smart Meal Planning from Weekly Deals",
  description:
    "AI-powered reverse meal planner for the Dutch market. " +
    "Generate budget-friendly recipes from Albert Heijn and Jumbo weekly discounts.",
};

/**
 * Root layout component.
 *
 * This wraps every page in the application with:
 * - The HTML document structure
 * - Global styles
 * - Shared navigation (to be added)
 *
 * @param children - The page content to render inside the layout.
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="nl">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {/* 
          Future additions:
          - <Navbar /> component at the top
          - <Footer /> component at the bottom  
          - Toast notification provider
          - Auth context provider
        */}
        {children}
      </body>
    </html>
  );
}
