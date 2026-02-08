/**
 * FolderChef — Recipe Section Component
 * ========================================
 *
 * This component displays AI-generated recipes on the home page.
 *
 * WHAT IT DOES:
 *   - Shows a "Generate Recipes" button
 *   - Calls the backend AI service to generate recipes
 *   - Displays recipe cards in a grid layout
 *   - Shows loading state during AI generation
 *
 * USER FLOW:
 *   1. User sees the recipe section (initially empty or with cached recipes)
 *   2. User clicks "Generate Recipes"
 *   3. Loading spinner appears (AI is working)
 *   4. Recipe cards appear with titles, costs, and ingredients
 *   5. User can click a recipe for full details
 */

"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api";
import type { Recipe } from "@/types/recipe";
import RecipeCard from "@/components/RecipeCard";

/**
 * RecipeSection component.
 *
 * Displays AI-generated recipes with a generate button.
 * Manages the loading state during recipe generation.
 *
 * @returns The recipe section JSX element.
 */
export default function RecipeSection() {
  // --- State ---
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [generated, setGenerated] = useState<boolean>(false);

  /**
   * Handle the "Generate Recipes" button click.
   *
   * Calls the backend API to generate recipes from current discounts.
   * Updates the UI with the results or an error message.
   */
  async function handleGenerate() {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.generateRecipes({
        supermarkets: ["albert_heijn", "jumbo"],
        num_recipes: 6,
        dietary_preferences: [],
        max_budget_per_meal: undefined,
      });

      setRecipes(response.recipes);
      setGenerated(true);
    } catch (err) {
      console.error("Failed to generate recipes:", err);
      setError("Could not generate recipes. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {/* Generate Button */}
      <div className="mb-8 text-center">
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="rounded-full bg-orange-500 px-8 py-3 text-lg font-semibold text-white shadow-lg transition hover:bg-orange-600 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
              AI is cooking...
            </span>
          ) : generated ? (
            "Generate More Recipes"
          ) : (
            "Generate My Recipes"
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 rounded-lg bg-red-50 p-4 text-center text-red-600">
          {error}
        </div>
      )}

      {/* Recipe Cards Grid */}
      {recipes.length > 0 ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {recipes.map((recipe, index) => (
            <RecipeCard key={recipe.id || index} recipe={recipe} />
          ))}
        </div>
      ) : generated ? (
        <p className="py-8 text-center text-gray-400">
          No recipes generated yet. Try again with different preferences.
        </p>
      ) : (
        <p className="py-8 text-center text-gray-400">
          Click the button above to generate budget-friendly recipes
          from this week&apos;s supermarket deals!
        </p>
      )}
    </div>
  );
}
