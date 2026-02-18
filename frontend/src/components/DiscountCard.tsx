/**
 * FolderChef — Discount Card Component
 * =======================================
 *
 * Compact card showing: product image, name, original price, deal price, discount type.
 * Links to product page when product_url is available.
 *
 * Discount types: BONUS, 10%, X% volume voordeel → "Online discount"
 */

import type { DiscountItem } from "@/types/discount";

/** Map discount_info to display type. BONUS/10%/volume voordeel → "Online discount" */
function getDiscountType(discountInfo: string): string {
  const upper = discountInfo.toUpperCase().trim();
  if (!upper) return discountInfo;
  if (upper === "BONUS" || upper.startsWith("BONUS")) return "Online discount";
  if (/\d+%\s*VOLUME/.test(upper) || upper.includes("VOLUME VOORDEEL")) return "Online discount";
  if (/^\d+%/.test(upper) || upper.includes("% KORTING")) return "Online discount";
  return discountInfo;
}

interface DiscountCardProps {
  item: DiscountItem;
}

export default function DiscountCard({ item }: DiscountCardProps) {
  const displayName = item.raw_name || item.common_name;
  const CardWrapper = item.product_url ? "a" : "div";
  const wrapperProps = item.product_url
    ? { href: item.product_url, target: "_blank", rel: "noopener noreferrer" }
    : {};

  return (
    <CardWrapper
      className="flex flex-col overflow-hidden rounded-xl bg-white shadow-md transition hover:shadow-lg no-underline text-inherit"
      {...wrapperProps}
    >
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
          {getDiscountType(item.discount_info)}
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
    </CardWrapper>
  );
}
