/**
 * FolderChef — Home Page
 * ========================
 *
 * This is the main landing page of FolderChef.
 *
 * WHAT THIS PAGE SHOWS:
 *   1. Hero section — explains what FolderChef does
 *   2. Discount cards — shows current supermarket deals
 *   3. Recipe section — displays AI-generated recipes
 *   4. Call to action — encourages users to generate recipes
 *
 * NEXT.JS ROUTING:
 *   In Next.js App Router, the file path = the URL path.
 *   src/app/page.tsx → renders at "/"  (the homepage)
 *   src/app/recipes/page.tsx → would render at "/recipes"
 *
 * DATA FETCHING:
 *   This is a Server Component by default (no "use client" directive).
 *   We can fetch data directly in the component. For dynamic/interactive
 *   parts, we use Client Components (with "use client").
 */

import DiscountSection from "@/components/DiscountSection";
import RecipeSection from "@/components/RecipeSection";

/**
 * Home page component.
 *
 * Renders the main landing page with hero, discounts, and recipes.
 * This is a Server Component — it renders on the server for fast loading.
 */
export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* ===== HERO SECTION ===== */}
      <section className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center">
          <h1 className="mb-4 text-5xl font-bold tracking-tight">
            FolderChef
          </h1>
          <p className="mb-2 text-xl font-light opacity-90">
            AI-Powered Reverse Meal Planner
          </p>
          <p className="mx-auto mb-8 max-w-2xl text-lg opacity-80">
            Stop planning meals, then shopping. Start with what&apos;s on sale at
            Albert Heijn &amp; Jumbo, and let AI create delicious, budget-friendly
            recipes for you.
          </p>
          <button className="rounded-full bg-white px-8 py-3 text-lg font-semibold text-orange-600 shadow-lg transition hover:bg-orange-50 hover:shadow-xl">
            Generate My Recipes
          </button>
        </div>
      </section>

      {/* ===== HOW IT WORKS ===== */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="mb-12 text-center text-3xl font-bold">
          How It Works
        </h2>
        <div className="grid gap-8 md:grid-cols-3">
          {/* Step 1 */}
          <div className="rounded-xl bg-white p-6 text-center shadow-md">
            <div className="mb-4 text-4xl">🛒</div>
            <h3 className="mb-2 text-xl font-semibold">1. We Scan Deals</h3>
            <p className="text-gray-600">
              We automatically fetch this week&apos;s discounts from Albert Heijn
              and Jumbo.
            </p>
          </div>
          {/* Step 2 */}
          <div className="rounded-xl bg-white p-6 text-center shadow-md">
            <div className="mb-4 text-4xl">🤖</div>
            <h3 className="mb-2 text-xl font-semibold">2. AI Creates Recipes</h3>
            <p className="text-gray-600">
              Our AI chef creates delicious meals using ingredients that are
              on sale this week.
            </p>
          </div>
          {/* Step 3 */}
          <div className="rounded-xl bg-white p-6 text-center shadow-md">
            <div className="mb-4 text-4xl">💰</div>
            <h3 className="mb-2 text-xl font-semibold">3. You Save Money</h3>
            <p className="text-gray-600">
              Cook amazing meals while spending less. Reduce food waste by
              buying only what you need.
            </p>
          </div>
        </div>
      </section>

      {/* ===== DISCOUNTS SECTION ===== */}
      <section className="bg-white py-16">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="mb-8 text-center text-3xl font-bold">
            This Week&apos;s Deals
          </h2>
          <DiscountSection />
        </div>
      </section>

      {/* ===== RECIPES SECTION ===== */}
      <section className="py-16">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="mb-8 text-center text-3xl font-bold">
            Recipes For You
          </h2>
          <RecipeSection />
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="border-t border-gray-200 bg-white py-8 text-center text-gray-500">
        <p>&copy; 2026 FolderChef — Smart Meal Planning from Weekly Deals</p>
        <p className="mt-2 text-sm">
          Made with ❤️ in the Netherlands
        </p>
      </footer>
    </main>
  );
}
