/**
 * FolderChef — Recipe Detail Modal
 * =================================
 *
 * Shows full recipe details when a recipe card is clicked.
 * Displays: instructions, ingredients with sale info (original/discounted prices).
 */

"use client";

import type { Recipe, RecipeIngredient } from "@/types/recipe";

interface RecipeDetailModalProps {
  recipe: Recipe;
  onClose: () => void;
}

function IngredientRow({ ing }: { ing: RecipeIngredient }) {
  return (
    <li className="flex items-center justify-between gap-2 py-2 border-b border-gray-100 last:border-0">
      <div className="flex flex-col">
        <span className="font-medium text-gray-800">{ing.name}</span>
        <span className="text-sm text-gray-500">{ing.quantity}</span>
      </div>
      <div className="ml-auto flex items-center gap-2">
        {ing.is_discounted && (ing.original_price != null || ing.discount_price != null) ? (
          <>
            {ing.original_price != null && (
              <span className="text-sm text-gray-400 line-through">
                €{ing.original_price.toFixed(2)}
              </span>
            )}
            {ing.discount_price != null && (
              <span className="rounded bg-green-100 px-2 py-0.5 text-sm font-semibold text-green-700">
                €{ing.discount_price.toFixed(2)}
              </span>
            )}
            <span className="rounded bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700">
              ON SALE
            </span>
          </>
        ) : (
          ing.estimated_price != null && (
            <span className="text-sm text-gray-600">
              ~€{ing.estimated_price.toFixed(2)}
            </span>
          )
        )}
      </div>
    </li>
  );
}

export default function RecipeDetailModal({ recipe, onClose }: RecipeDetailModalProps) {
  const totalTime = recipe.prep_time_minutes + recipe.cook_time_minutes;
  const discountedCount = recipe.ingredients.filter((i) => i.is_discounted).length;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="recipe-modal-title"
    >
      <div
        className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 z-10 border-b border-gray-200 bg-white px-6 py-4">
          <div className="flex items-start justify-between gap-4">
            <h2 id="recipe-modal-title" className="text-2xl font-bold text-gray-800">
              {recipe.title}
            </h2>
            <button
              type="button"
              onClick={onClose}
              className="rounded-full p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
              aria-label="Close"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="mt-2 text-gray-600">{recipe.description}</p>
          <div className="mt-3 flex flex-wrap gap-3 text-sm text-gray-500">
            <span>👥 {recipe.servings} servings</span>
            <span>⏱️ {totalTime} min</span>
            {discountedCount > 0 && (
              <span className="text-green-600 font-medium">
                🏷️ {discountedCount} items on sale
              </span>
            )}
          </div>
          {recipe.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
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
          <div className="mt-3 flex items-center gap-4">
            <span className="text-2xl font-bold text-orange-600">
              €{recipe.estimated_cost.toFixed(2)}
            </span>
            {recipe.savings_percentage != null && recipe.savings_percentage > 0 && (
              <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-semibold text-green-700">
                Save {recipe.savings_percentage.toFixed(0)}%
              </span>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          {/* Ingredients */}
          <section className="mb-6">
            <h3 className="mb-3 text-lg font-semibold text-gray-800">Ingredients</h3>
            <ul className="divide-y divide-gray-100">
              {recipe.ingredients.map((ing, i) => (
                <IngredientRow key={i} ing={ing} />
              ))}
            </ul>
          </section>

          {/* Instructions */}
          <section>
            <h3 className="mb-3 text-lg font-semibold text-gray-800">How to make</h3>
            <ol className="list-decimal space-y-2 pl-5">
              {recipe.instructions.map((step, i) => (
                <li key={i} className="text-gray-700 leading-relaxed">
                  {step}
                </li>
              ))}
            </ol>
          </section>

          {recipe.supermarkets.length > 0 && (
            <p className="mt-4 text-sm text-gray-500">
              Available at: {recipe.supermarkets.length > 0 ? recipe.supermarkets.join(", ") : "—"}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
