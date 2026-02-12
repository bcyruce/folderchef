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
import { VALID_LABELS } from "@/types/recipe";
import RecipeCard from "@/components/RecipeCard";
import RecipeDetailModal from "@/components/RecipeDetailModal";

const MAX_LABELS = 5;

/**
 * RecipeSection component.
 *
 * Displays a prompt text box, label selector (max 5), and generate button.
 * Only discount items with selected labels are sent to the AI.
 *
 * @returns The recipe section JSX element.
 */
export default function RecipeSection() {
  // --- State ---
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [generated, setGenerated] = useState<boolean>(false);
  const [userPrompt, setUserPrompt] = useState<string>("");
  const [selectedLabels, setSelectedLabels] = useState<string[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);

  function toggleLabel(label: string) {
    setSelectedLabels((prev) => {
      if (prev.includes(label)) {
        return prev.filter((l) => l !== label);
      }
      if (prev.length >= MAX_LABELS) return prev;
      return [...prev, label];
    });
  }

  const canGenerate = selectedLabels.length >= 1 && !loading;

  /**
   * Handle the "Generate Recipes" button click.
   *
   * Sends user prompt and selected labels; backend filters discount items
   * by label and passes them + prompt to the AI.
   */
  async function handleGenerate() {
    if (!canGenerate) return;
    setLoading(true);
    setError(null);

    const minLoadingMs = 600; // So user always sees "Generating..." feedback
    const start = Date.now();

    try {
      const response = await apiClient.generateRecipes({
        supermarkets: ["albert_heijn", "jumbo"],
        num_recipes: 3,
        dietary_preferences: [],
        max_budget_per_meal: undefined,
        user_prompt: userPrompt.trim() || undefined,
        label_filter: selectedLabels,
      });

      setRecipes(response.recipes ?? []);
      setGenerated(true);
    } catch (err) {
      console.error("Failed to generate recipes:", err);
      setError("Could not generate recipes. Please try again.");
    } finally {
      const elapsed = Date.now() - start;
      const remaining = Math.max(0, minLoadingMs - elapsed);
      setTimeout(() => setLoading(false), remaining);
    }
  }

  return (
    <div>
      {/* User prompt + label selector */}
      <div className="mb-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <label htmlFor="recipe-prompt" className="mb-2 block text-sm font-medium text-gray-700">
          What do you feel like?
        </label>
        <textarea
          id="recipe-prompt"
          value={userPrompt}
          onChange={(e) => setUserPrompt(e.target.value)}
          placeholder="e.g. quick dinner, no oven, under 30 minutes, something healthy..."
          rows={2}
          className="mb-4 w-full resize-y rounded-lg border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:border-orange-500 focus:outline-none focus:ring-1 focus:ring-orange-500"
        />
        <label className="mb-2 block text-sm font-medium text-gray-700">
          Filter by category (choose 1–5; only these items go to the AI)
        </label>
        <div className="mb-4 flex flex-wrap gap-2">
          {VALID_LABELS.map((label) => {
            const selected = selectedLabels.includes(label);
            const disabled = !selected && selectedLabels.length >= MAX_LABELS;
            return (
              <button
                key={label}
                type="button"
                onClick={() => toggleLabel(label)}
                disabled={disabled}
                className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                  selected
                    ? "bg-orange-500 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                } ${disabled ? "cursor-not-allowed opacity-50" : ""}`}
              >
                {label}
              </button>
            );
          })}
        </div>
        <p className="mb-4 text-xs text-gray-500">
          {selectedLabels.length} of {MAX_LABELS} selected. Select at least one to generate recipes.
        </p>
      </div>

      {/* Generate Button */}
      <div className="mb-8 text-center">
        <button
          type="button"
          onClick={handleGenerate}
          disabled={!canGenerate}
          aria-busy={loading}
          className={`rounded-full px-8 py-3 text-lg font-semibold transition disabled:cursor-not-allowed ${
            loading
              ? "bg-gray-400 text-white shadow-none"
              : "bg-orange-500 text-white shadow-lg hover:bg-orange-600 hover:shadow-xl disabled:opacity-50"
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Generating...
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
            <RecipeCard
              key={recipe.id || index}
              recipe={recipe}
              onClick={() => setSelectedRecipe(recipe)}
            />
          ))}
        </div>
      ) : generated ? (
        <div className="py-8 text-center">
          <p className="text-gray-500">
            No recipes were generated. This may mean there are no discounted items matching your selected labels.
            Try selecting different categories.
          </p>
        </div>
      ) : (
        <p className="py-8 text-center text-gray-400">
          Click the button above to generate budget-friendly recipes
          from this week&apos;s supermarket deals!
        </p>
      )}

      {selectedRecipe && (
        <RecipeDetailModal
          recipe={selectedRecipe}
          onClose={() => setSelectedRecipe(null)}
        />
      )}
    </div>
  );
}
