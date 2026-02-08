/**
 * FolderChef — Recipe Card Component
 * =====================================
 *
 * This component renders a single AI-generated recipe as a card.
 *
 * WHAT IT SHOWS:
 *   - Recipe title
 *   - Description
 *   - Estimated cost with savings badge
 *   - Prep + cook time
 *   - Number of servings
 *   - Tags (vegetarian, quick, etc.)
 *   - Discounted ingredient count
 *
 * DESIGN:
 *   Clean card layout with:
 *   - Warm colour palette matching the FolderChef brand
 *   - Clear cost/savings display
 *   - Quick-glance meta information (time, servings)
 */

import type { Recipe } from "@/types/recipe";

/**
 * Props for the RecipeCard component.
 *
 * @property recipe - The recipe data to display.
 */
interface RecipeCardProps {
  recipe: Recipe;
}

/**
 * RecipeCard component.
 *
 * Renders a single recipe as a visual card with key information.
 * Designed to be displayed in a grid layout.
 *
 * @param props - Component props containing the recipe data.
 * @returns The recipe card JSX element.
 */
export default function RecipeCard({ recipe }: RecipeCardProps) {
  /** Count how many ingredients are currently on sale. */
  const discountedCount = recipe.ingredients.filter(
    (i) => i.is_discounted
  ).length;

  /** Total prep + cook time. */
  const totalTime = recipe.prep_time_minutes + recipe.cook_time_minutes;

  return (
    <div className="flex flex-col rounded-xl bg-white p-5 shadow-md transition hover:shadow-lg">
      {/* Title */}
      <h3 className="mb-2 text-xl font-bold text-gray-800">{recipe.title}</h3>

      {/* Description */}
      <p className="mb-4 text-sm text-gray-500 leading-relaxed">
        {recipe.description}
      </p>

      {/* Meta Information */}
      <div className="mb-4 flex flex-wrap gap-3 text-sm text-gray-500">
        {/* Servings */}
        <span className="flex items-center gap-1">
          <span>👥</span>
          {recipe.servings} servings
        </span>
        {/* Time */}
        <span className="flex items-center gap-1">
          <span>⏱️</span>
          {totalTime} min
        </span>
        {/* Discounted Ingredients */}
        {discountedCount > 0 && (
          <span className="flex items-center gap-1 text-green-600">
            <span>🏷️</span>
            {discountedCount} items on sale
          </span>
        )}
      </div>

      {/* Tags */}
      {recipe.tags.length > 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {recipe.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-orange-50 px-3 py-1 text-xs font-medium text-orange-600"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Price + Savings */}
      <div className="mt-auto flex items-end justify-between">
        <div>
          <span className="text-2xl font-bold text-orange-600">
            &euro;{recipe.estimated_cost.toFixed(2)}
          </span>
          <span className="ml-1 text-sm text-gray-400">estimated</span>
        </div>
        {recipe.savings_percentage != null && recipe.savings_percentage > 0 && (
          <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-semibold text-green-700">
            Save {recipe.savings_percentage.toFixed(0)}%
          </span>
        )}
      </div>
    </div>
  );
}
