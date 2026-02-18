/**
 * FolderChef — Discount Section Component
 * ==========================================
 *
 * Weekly supermarket discounts with:
 * - Valid date range when Albert Heijn or Jumbo is selected
 * - Discount type filter: All | Online discount | In-store deal
 * - Products grouped by discount type under valid date
 * - Pagination with fixed position
 */

"use client";

import { useState, useEffect, useMemo } from "react";
import { apiClient } from "@/lib/api";
import type { DiscountResponse, DiscountItem } from "@/types/discount";
import { getDiscountType, DISCOUNT_TYPE_ONLINE, DISCOUNT_TYPE_INSTORE } from "@/lib/discountTypes";
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

/** Group items by discount type */
function groupByDiscountType(items: DiscountItem[]) {
  const online: DiscountItem[] = [];
  const instore: DiscountItem[] = [];
  for (const item of items) {
    if (getDiscountType(item.discount_info) === DISCOUNT_TYPE_ONLINE) {
      online.push(item);
    } else {
      instore.push(item);
    }
  }
  return { online, instore };
}

export default function DiscountSection() {
  const [discounts, setDiscounts] = useState<DiscountResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const [discountTypeFilter, setDiscountTypeFilter] = useState<string>("all");
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

  useEffect(() => {
    setPage(1);
  }, [activeFilter, discountTypeFilter]);

  const filteredDiscounts =
    activeFilter === "all"
      ? discounts
      : discounts.filter((d) => d.supermarket === activeFilter);

  const allItems = useMemo(
    () => filteredDiscounts.flatMap((d) => d.items),
    [filteredDiscounts]
  );

  const { online, instore } = useMemo(
    () => groupByDiscountType(allItems),
    [allItems]
  );

  const itemsByTypeFilter = useMemo(() => {
    if (discountTypeFilter === DISCOUNT_TYPE_ONLINE) return online;
    if (discountTypeFilter === DISCOUNT_TYPE_INSTORE) return instore;
    return [...online, ...instore];
  }, [discountTypeFilter, online, instore]);

  const dateRange = useMemo(
    () => getValidDateRange(allItems),
    [allItems]
  );

  const totalPages = Math.ceil(itemsByTypeFilter.length / PRODUCTS_PER_PAGE) || 1;
  const startIdx = (page - 1) * PRODUCTS_PER_PAGE;
  const paginatedItems = itemsByTypeFilter.slice(startIdx, startIdx + PRODUCTS_PER_PAGE);

  const showGrouped = discountTypeFilter === "all" && (online.length > 0 && instore.length > 0);

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
      {/* Supermarket Filter */}
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
            {filter === "all" ? "All Supermarkets" : filter === "albert_heijn" ? "Albert Heijn" : "Jumbo"}
          </button>
        ))}
      </div>

      {/* Valid date + Discount type filter */}
      {allItems.length > 0 && (
        <div className="mb-4 space-y-3 text-center">
          {activeFilter !== "all" && dateRange && (
            <p className="text-sm text-gray-600">
              Valid from {dateRange.from} to {dateRange.to}
            </p>
          )}
          <div className="flex flex-wrap justify-center gap-2">
            {["all", DISCOUNT_TYPE_ONLINE, DISCOUNT_TYPE_INSTORE].map((type) => (
              <button
                key={type}
                onClick={() => setDiscountTypeFilter(type)}
                className={`rounded-full px-4 py-1.5 text-xs font-medium transition ${
                  discountTypeFilter === type
                    ? "bg-orange-500 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {type === "all" ? "All types" : type}
              </button>
            ))}
          </div>
        </div>
      )}

      {allItems.length === 0 ? (
        <p className="py-8 text-center text-gray-400">
          No discounts available yet. Check back soon!
        </p>
      ) : (
        <div className="flex flex-col">
          {/* Products area - min 3 rows height so pagination stays fixed */}
          <div className="min-h-[920px] flex-1">
            {showGrouped ? (
              <div className="space-y-10">
                {(() => {
                  const pageOnline = paginatedItems.filter((i) => getDiscountType(i.discount_info) === DISCOUNT_TYPE_ONLINE);
                  const pageInstore = paginatedItems.filter((i) => getDiscountType(i.discount_info) === DISCOUNT_TYPE_INSTORE);
                  return (
                    <>
                      {pageOnline.length > 0 && (
                        <section>
                          <h3 className="mb-4 text-lg font-semibold text-gray-800">
                            {DISCOUNT_TYPE_ONLINE}
                          </h3>
                          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
                            {pageOnline.map((item, index) => (
                              <DiscountCard key={`${item.id ?? index}-${item.raw_name}`} item={item} />
                            ))}
                          </div>
                        </section>
                      )}
                      {pageInstore.length > 0 && (
                        <section>
                          <h3 className="mb-4 text-lg font-semibold text-gray-800">
                            {DISCOUNT_TYPE_INSTORE}
                          </h3>
                          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
                            {pageInstore.map((item, index) => (
                              <DiscountCard key={`${item.id ?? index}-${item.raw_name}`} item={item} />
                            ))}
                          </div>
                        </section>
                      )}
                    </>
                  );
                })()}
              </div>
            ) : (
              <div className="grid min-h-[900px] gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
                {paginatedItems.map((item, index) => (
                  <DiscountCard
                    key={`${item.id ?? index}-${item.raw_name}`}
                    item={item}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Pagination - fixed height, won't shift */}
          {totalPages > 1 && (
            <div className="mt-6 flex h-16 shrink-0 items-center justify-center gap-2 border-t border-gray-200 pt-6">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 disabled:opacity-50 hover:bg-gray-200"
              >
                Previous
              </button>
              <span className="min-w-[140px] text-center text-sm text-gray-600">
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
