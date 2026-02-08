/**
 * FolderChef — Discount Card Component
 * =======================================
 *
 * This component renders a single discount item as a card.
 *
 * WHAT IT SHOWS:
 *   - Product name
 *   - Original price (crossed out)
 *   - Discount price or label
 *   - Supermarket badge (AH / Jumbo)
 *   - Category tag (if available)
 *
 * DESIGN:
 *   The card uses a clean, modern design with:
 *   - Rounded corners and subtle shadow
 *   - Colour-coded supermarket badges
 *   - Clear price comparison
 */

import type { DiscountItem } from "@/types/discount";

/**
 * Props for the DiscountCard component.
 *
 * @property item - The discount item data to display.
 */
interface DiscountCardProps {
  item: DiscountItem;
}

/**
 * DiscountCard component.
 *
 * Renders a single supermarket discount as a visual card.
 *
 * @param props - Component props containing the discount item.
 * @returns The discount card JSX element.
 */
export default function DiscountCard({ item }: DiscountCardProps) {
  /**
   * Get the badge colour based on the supermarket.
   * Albert Heijn = blue, Jumbo = yellow.
   */
  const badgeColor =
    item.supermarket === "albert_heijn"
      ? "bg-blue-100 text-blue-800"
      : "bg-yellow-100 text-yellow-800";

  const supermarketLabel =
    item.supermarket === "albert_heijn" ? "Albert Heijn" : "Jumbo";

  return (
    <div className="flex flex-col rounded-xl bg-white p-4 shadow-md transition hover:shadow-lg">
      {/* Top Row: Supermarket Badge + Category */}
      <div className="mb-3 flex items-center justify-between">
        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${badgeColor}`}
        >
          {supermarketLabel}
        </span>
        {item.category && (
          <span className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-500">
            {item.category}
          </span>
        )}
      </div>

      {/* Product Name */}
      <h3 className="mb-2 text-lg font-semibold leading-tight text-gray-800">
        {item.name}
      </h3>

      {/* Discount Label */}
      <p className="mb-3 text-sm font-medium text-green-600">
        {item.discount_label}
      </p>

      {/* Prices */}
      <div className="mt-auto flex items-end gap-2">
        {item.discount_price != null && (
          <span className="text-2xl font-bold text-orange-600">
            &euro;{item.discount_price.toFixed(2)}
          </span>
        )}
        {item.original_price != null && (
          <span className="text-sm text-gray-400 line-through">
            &euro;{item.original_price.toFixed(2)}
          </span>
        )}
      </div>
    </div>
  );
}
