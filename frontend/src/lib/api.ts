/**
 * FolderChef — API Client
 * =========================
 *
 * This module provides a typed API client for communicating with the
 * FolderChef backend.
 *
 * WHY A DEDICATED API CLIENT?
 *   Instead of writing `fetch()` calls everywhere in our components,
 *   we centralise all API communication here. This gives us:
 *   1. One place to update if the API changes
 *   2. Consistent error handling across the app
 *   3. TypeScript types for all requests and responses
 *   4. Easy to swap the base URL for production vs development
 *
 * USAGE IN COMPONENTS:
 *   import { apiClient } from "@/lib/api";
 *
 *   const discounts = await apiClient.getDiscounts();
 *   const recipes = await apiClient.generateRecipes({ num_recipes: 5 });
 *
 * API BASE URL:
 *   - Development: http://localhost:8000 (local backend)
 *   - Production: Set via NEXT_PUBLIC_API_URL environment variable
 */

import type { DiscountResponse } from "@/types/discount";
import type {
  RecipeGenerateRequest,
  RecipeGenerateResponse,
  Recipe,
} from "@/types/recipe";

/**
 * The base URL for all API requests.
 *
 * In development, this defaults to http://localhost:8000 (the local backend).
 * In production (Railway), set NEXT_PUBLIC_API_URL to the deployed backend URL.
 *
 * NEXT_PUBLIC_ prefix means this variable is accessible in the browser.
 */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Make a typed API request to the backend.
 *
 * This is a helper function that wraps the native `fetch()` API with:
 * - Automatic JSON parsing
 * - Error handling
 * - Correct headers
 * - TypeScript generics for the response type
 *
 * @template T - The expected response type.
 * @param endpoint - The API endpoint path (e.g., "/api/discounts").
 * @param options - Optional fetch options (method, body, etc.).
 * @returns The parsed JSON response, typed as T.
 * @throws Error if the request fails or the server returns an error.
 *
 * @example
 *   const data = await fetchAPI<DiscountResponse[]>("/api/discounts");
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  // If the server returned an error, throw a descriptive error
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(
      `API Error ${response.status}: ${response.statusText} — ${errorBody}`
    );
  }

  // Parse and return the JSON response
  return response.json() as Promise<T>;
}

/**
 * FolderChef API client.
 *
 * Provides typed methods for all backend API endpoints.
 * Each method handles the request construction and response typing.
 *
 * @example
 *   import { apiClient } from "@/lib/api";
 *
 *   // Get all discounts
 *   const discounts = await apiClient.getDiscounts();
 *
 *   // Generate recipes
 *   const response = await apiClient.generateRecipes({
 *     num_recipes: 5,
 *     dietary_preferences: ["vegetarian"],
 *   });
 */
export const apiClient = {
  // =============================================
  // DISCOUNT ENDPOINTS
  // =============================================

  /**
   * Fetch all current supermarket discounts.
   *
   * @returns Array of discount responses, one per supermarket.
   */
  async getDiscounts(): Promise<DiscountResponse[]> {
    return fetchAPI<DiscountResponse[]>("/api/discounts/");
  },

  /**
   * Fetch discounts for a specific supermarket.
   *
   * @param supermarket - "albert_heijn" or "jumbo".
   * @returns Discount response for the specified supermarket.
   */
  async getDiscountsByStore(
    supermarket: string
  ): Promise<DiscountResponse> {
    return fetchAPI<DiscountResponse>(
      `/api/discounts/${supermarket}`
    );
  },

  /**
   * Trigger a refresh of discount data.
   *
   * Forces the backend to re-scrape the supermarket websites.
   *
   * @param supermarket - Optional: specific supermarket to refresh.
   * @returns Status message from the backend.
   */
  async refreshDiscounts(
    supermarket?: string
  ): Promise<{ status: string; message: string }> {
    const query = supermarket ? `?supermarket=${supermarket}` : "";
    return fetchAPI(`/api/discounts/refresh${query}`, {
      method: "POST",
    });
  },

  // =============================================
  // RECIPE ENDPOINTS
  // =============================================

  /**
   * Generate AI-powered recipes from current discounts.
   *
   * This calls the AI service on the backend, which may take
   * several seconds. Show a loading state in the UI.
   *
   * @param request - Generation parameters (preferences, budget, etc.).
   * @returns The generated recipes with metadata.
   */
  async generateRecipes(
    request: RecipeGenerateRequest
  ): Promise<RecipeGenerateResponse> {
    return fetchAPI<RecipeGenerateResponse>("/api/recipes/generate", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  /**
   * Fetch all previously generated recipes.
   *
   * @returns Array of recipe objects.
   */
  async getRecipes(): Promise<Recipe[]> {
    return fetchAPI<Recipe[]>("/api/recipes/");
  },

  /**
   * Fetch a specific recipe by its ID.
   *
   * @param recipeId - The unique recipe identifier.
   * @returns The full recipe object.
   */
  async getRecipeById(recipeId: string): Promise<Recipe> {
    return fetchAPI<Recipe>(`/api/recipes/${recipeId}`);
  },
};
