/**
 * Discount type classification for display and filtering.
 * BONUS, 10%, X% volume voordeel → "Online discount"
 * Everything else → "In-store deal"
 */

export const DISCOUNT_TYPE_ONLINE = "Online discount";
export const DISCOUNT_TYPE_INSTORE = "In-store deal";

export type DiscountTypeValue = typeof DISCOUNT_TYPE_ONLINE | typeof DISCOUNT_TYPE_INSTORE;

/**
 * Map discount_info from API to display category.
 * Matches Dutch AH/Jumbo formats: BONUS, X% korting, X% volume voordeel.
 */
export function getDiscountType(discountInfo: string): DiscountTypeValue {
  if (!discountInfo?.trim()) return DISCOUNT_TYPE_INSTORE;
  const upper = discountInfo.toUpperCase().trim();
  if (upper === "BONUS" || upper.includes("BONUS")) return DISCOUNT_TYPE_ONLINE;
  if (/\d+\s*%.*VOLUME/i.test(upper) || upper.includes("VOLUMEVOORDEEL") || (upper.includes("VOLUME") && upper.includes("VOORDEEL"))) return DISCOUNT_TYPE_ONLINE;
  if (/\d+\s*%/.test(upper) || upper.includes("% KORTING")) return DISCOUNT_TYPE_ONLINE;
  return DISCOUNT_TYPE_INSTORE;
}
