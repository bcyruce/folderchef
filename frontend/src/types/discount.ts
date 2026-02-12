/**
 * FolderChef — Discount TypeScript Types
 * =========================================
 *
 * These types mirror the Pydantic models on the backend.
 * They define the shape of discount data in the frontend.
 *
 * WHY DUPLICATE TYPES?
 *   The backend uses Python (Pydantic models) and the frontend uses
 *   TypeScript. We define the same shapes in both languages so that:
 *   1. TypeScript can check that we use the data correctly
 *   2. Our editor can auto-complete field names
 *   3. Bugs are caught at compile time, not at runtime
 *
 * KEEP IN SYNC:
 *   When you change a model in the backend (backend/app/models/discount.py),
 *   update the corresponding type here too!
 *
 *   Future improvement: auto-generate these types from the backend
 *   using tools like openapi-typescript-codegen.
 */

/**
 * A single discounted product from a supermarket.
 *
 * Matches backend CleanedProduct.
 */
export interface DiscountItem {
  id: number | null;
  raw_name: string;
  common_name: string;
  labels: string[];
  supermarket: "albert_heijn" | "jumbo";
  original_price: number | null;
  discount_price_per_unit: number | null;
  discount_info: string;
  weight: string | null;
  price_per_kg: number | null;
  start_date: string | null;
  end_date: string | null;
  image_url: string | null;
  scraped_at: string | null;
}

/**
 * API response containing discounts for one supermarket.
 *
 * This matches the DiscountResponse model on the backend.
 *
 * @property supermarket - The supermarket name.
 * @property total_items - Number of discount items.
 * @property week - Human-readable week label (e.g., "Week 2, 2025").
 * @property items - Array of discount items.
 */
export interface DiscountResponse {
  supermarket: string;
  total_items: number;
  week: string;
  items: DiscountItem[];
}
