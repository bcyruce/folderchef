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
 * This matches the DiscountItem model on the backend.
 *
 * @property id - Unique identifier (may be null for new items).
 * @property name - Product name (e.g., "Goudse kaas jong belegen").
 * @property supermarket - Which supermarket ("albert_heijn" or "jumbo").
 * @property original_price - Regular price in EUR (before discount).
 * @property discount_price - Sale price in EUR.
 * @property discount_label - Discount description (e.g., "1+1 gratis").
 * @property category - AI-assigned food category (e.g., "dairy").
 * @property image_url - URL to the product image.
 * @property valid_from - Start date of the discount period (ISO string).
 * @property valid_until - End date of the discount period (ISO string).
 */
export interface DiscountItem {
  id: string | null;
  name: string;
  supermarket: "albert_heijn" | "jumbo";
  original_price: number | null;
  discount_price: number | null;
  discount_label: string;
  category: string | null;
  image_url: string | null;
  valid_from: string | null;
  valid_until: string | null;
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
