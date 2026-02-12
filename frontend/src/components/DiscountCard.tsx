/**
 * FolderChef — Discount Card Component
 * =======================================
 *
 * Compact card showing: product image, name, original price, deal price, discount type.
 */

import type { DiscountItem } from "@/types/discount";

interface DiscountCardProps {
  item: DiscountItem;
}

export default function DiscountCard({ item }: DiscountCardProps) {
  const displayName = item.raw_name || item.common_name;

  return (
    <div className="flex flex-col overflow-hidden rounded-xl bg-white shadow-md transition hover:shadow-lg">
      {/* Product image */}
      <div className="aspect-square w-full bg-gray-100">
        {item.image_url ? (
          <img
            src={item.image_url}
            alt={displayName}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-4xl text-gray-300">
            🛒
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex flex-1 flex-col p-3">
        <h3 className="mb-2 line-clamp-2 text-sm font-medium leading-tight text-gray-800">
          {displayName}
        </h3>

        <p className="mb-2 text-xs font-medium text-green-600">
          {item.discount_info}
        </p>

        <div className="mt-auto flex items-center gap-2">
          {item.discount_price_per_unit != null && (
            <span className="text-lg font-bold text-orange-600">
              €{item.discount_price_per_unit.toFixed(2)}
            </span>
          )}
          {item.original_price != null && (
            <span className="text-sm text-gray-400 line-through">
              €{item.original_price.toFixed(2)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
