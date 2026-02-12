/**
 * FolderChef — Recipe Card Component
 * =====================================
 *
 * Interactive card that shows recipe preview. Click to open full details
 * (instructions, ingredients with sale info, original/discounted prices).
 */

import type { Recipe } from "@/types/recipe";

interface RecipeCardProps {
  recipe: Recipe;
  onClick?: () => void;
}

export default function RecipeCard({ recipe, onClick }: RecipeCardProps) {
  /** Count how many ingredients are currently on sale. */
  const discountedCount = recipe.ingredients.filter(
    (i) => i.is_discounted
  ).length;

  /** Total prep + cook time. */
  const totalTime = recipe.prep_time_minutes + recipe.cook_time_minutes;

  return (
    <button
      type="button"
      onClick={onClick}
      className="flex w-full flex-col rounded-xl bg-white p-5 text-left shadow-md transition hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
    >
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
      <p className="mt-3 text-xs text-gray-400">Click for full recipe & instructions</p>
    </button>
  );
}
