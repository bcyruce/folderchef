/**
 * FolderChef — Discount Section Component
 * ==========================================
 *
 * This component displays the current weekly supermarket discounts.
 *
 * WHAT IT DOES:
 *   - Fetches discount data from the backend API
 *   - Displays discount items in a responsive grid
 *   - Shows loading and error states
 *   - Lets users filter by supermarket (Albert Heijn / Jumbo)
 *
 * THIS IS A CLIENT COMPONENT:
 *   The "use client" directive below tells Next.js this component
 *   runs in the browser (not on the server). We need this because:
 *   - It uses React hooks (useState, useEffect)
 *   - It handles user interactions (clicks, filters)
 *   - It fetches data dynamically after the page loads
 */

"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";
import type { DiscountResponse } from "@/types/discount";
import DiscountCard from "@/components/DiscountCard";

/**
 * DiscountSection component.
 *
 * Fetches and displays current supermarket discounts.
 * Shows a loading spinner while data is being fetched,
 * and an error message if something goes wrong.
 *
 * @returns The discount section JSX element.
 */
export default function DiscountSection() {
  // --- State ---
  // "state" is data that can change over time and causes the UI to update.
  const [discounts, setDiscounts] = useState<DiscountResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>("all");

  // --- Fetch discounts on component mount ---
  // useEffect runs code after the component is displayed on screen.
  // The empty [] means it runs once when the component first appears.
  useEffect(() => {
    async function fetchDiscounts() {
      try {
        setLoading(true);
        setError(null);
        const data = await apiClient.getDiscounts();
        setDiscounts(data);
      } catch (err) {
        console.error("Failed to fetch discounts:", err);
        setError("Could not load discounts. Please try again later.");
      } finally {
        setLoading(false);
      }
    }

    fetchDiscounts();
  }, []);

  // --- Filter discounts by supermarket ---
  const filteredDiscounts =
    activeFilter === "all"
      ? discounts
      : discounts.filter((d) => d.supermarket === activeFilter);

  // --- Loading State ---
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-orange-500 border-t-transparent"></div>
        <span className="ml-3 text-gray-500">Loading deals...</span>
      </div>
    );
  }

  // --- Error State ---
  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center text-red-600">
        <p>{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 rounded-lg bg-red-100 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-200"
        >
          Retry
        </button>
      </div>
    );
  }

  // --- Main Content ---
  return (
    <div>
      {/* Supermarket Filter Buttons */}
      <div className="mb-6 flex justify-center gap-3">
        {["all", "albert_heijn", "jumbo"].map((filter) => (
          <button
            key={filter}
            onClick={() => setActiveFilter(filter)}
            className={`rounded-full px-5 py-2 text-sm font-medium transition ${
              activeFilter === filter
                ? "bg-orange-500 text-white shadow-md"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {filter === "all"
              ? "All Supermarkets"
              : filter === "albert_heijn"
              ? "Albert Heijn"
              : "Jumbo"}
          </button>
        ))}
      </div>

      {/* Discount Cards Grid */}
      {filteredDiscounts.length === 0 ? (
        <p className="py-8 text-center text-gray-400">
          No discounts available yet. Check back soon!
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredDiscounts.map((discountGroup) =>
            discountGroup.items.map((item, index) => (
              <DiscountCard key={`${discountGroup.supermarket}-${index}`} item={item} />
            ))
          )}
        </div>
      )}
    </div>
  );
}
