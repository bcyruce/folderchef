/**
 * FolderChef — Discount Section Component
 * ==========================================
 *
 * Weekly supermarket discounts with:
 * - Valid date range when Albert Heijn or Jumbo is selected
 * - Paginated product grid (15 per page)
 * - Product cards: image, name, original price, deal price, discount type
 */

"use client";

import { useState, useEffect, useMemo } from "react";
import { apiClient } from "@/lib/api";
import type { DiscountResponse, DiscountItem } from "@/types/discount";
import DiscountCard from "@/components/DiscountCard";

const PRODUCTS_PER_PAGE = 15;

/** Format date as d.m.yyyy (e.g. 12.2.2026) */
function formatDate(iso: string | null): string {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    if (isNaN(d.getTime())) return "—";
    return `${d.getDate()}.${d.getMonth() + 1}.${d.getFullYear()}`;
  } catch {
    return "—";
  }
}

/** Get valid date range from items (first item with dates) */
function getValidDateRange(items: DiscountItem[]): { from: string; to: string } | null {
  for (const item of items) {
    if (item.start_date || item.end_date) {
      return {
        from: formatDate(item.start_date),
        to: formatDate(item.end_date),
      };
    }
  }
  return null;
}

export default function DiscountSection() {
  const [discounts, setDiscounts] = useState<DiscountResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const [page, setPage] = useState<number>(1);

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

  // Reset to page 1 when filter changes
  useEffect(() => {
    setPage(1);
  }, [activeFilter]);

  const filteredDiscounts =
    activeFilter === "all"
      ? discounts
      : discounts.filter((d) => d.supermarket === activeFilter);

  const allItems = useMemo(
    () => filteredDiscounts.flatMap((d) => d.items),
    [filteredDiscounts]
  );

  const dateRange = useMemo(
    () => getValidDateRange(allItems),
    [allItems]
  );

  const totalPages = Math.ceil(allItems.length / PRODUCTS_PER_PAGE) || 1;
  const startIdx = (page - 1) * PRODUCTS_PER_PAGE;
  const paginatedItems = allItems.slice(startIdx, startIdx + PRODUCTS_PER_PAGE);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-orange-500 border-t-transparent" />
        <span className="ml-3 text-gray-500">Loading deals...</span>
      </div>
    );
  }

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

  return (
    <div>
      {/* Supermarket Filter Buttons */}
      <div className="mb-6 flex flex-wrap justify-center gap-3">
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

      {/* Valid date range + discount type info - shown when Albert Heijn or Jumbo is selected */}
      {activeFilter !== "all" && dateRange && (
        <div className="mb-4 text-center text-sm text-gray-600">
          <p>Valid from {dateRange.from} to {dateRange.to}</p>
          <p className="mt-1 text-xs text-gray-500">
            Discount types: Online discount (BONUS, %, volume) · In-store deals
          </p>
        </div>
      )}

      {/* Product grid + pagination */}
      {allItems.length === 0 ? (
        <p className="py-8 text-center text-gray-400">
          No discounts available yet. Check back soon!
        </p>
      ) : (
        <div className="flex flex-col">
          {/* Grid with min-height so pagination stays fixed when changing pages */}
          <div className="grid min-h-[680px] gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
            {paginatedItems.map((item, index) => (
              <DiscountCard
                key={`${item.id ?? index}-${item.raw_name}`}
                item={item}
              />
            ))}
          </div>

          {/* Pagination - fixed position at bottom of container */}
          {totalPages > 1 && (
            <div className="mt-6 flex shrink-0 items-center justify-center gap-2 py-4">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 disabled:opacity-50 hover:bg-gray-200"
              >
                Previous
              </button>
              <span className="min-w-[120px] px-4 text-center text-sm text-gray-600">
                Page {page} of {totalPages}
              </span>
              <button
                type="button"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 disabled:opacity-50 hover:bg-gray-200"
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
