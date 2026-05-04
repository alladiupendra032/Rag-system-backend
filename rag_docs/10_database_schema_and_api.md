# Database Schema and API Architecture

## 1. Introduction
This document details the exact PostgreSQL database schema hosted on Supabase for the "E-Commerce Web Platform". It is crucial for the RAG AI to understand the precise tables, columns, and relationships in order to comprehend how data is stored, such as how the 33 products in our catalog are related to user orders and carts.

## 2. PostgreSQL Schema Overview

Our Supabase project (ID: `catrhmifbzirsglcglqa`) uses the `public` schema for all application data, alongside the `auth` schema managed by Supabase for authentication.

Below is the detailed schema breakdown:

### 2.1. `public.profiles`
This table extends the Supabase `auth.users` table to store public-facing user data and role-based access information.
- `id` (uuid, Primary Key): Foreign key linking directly to `auth.users.id`.
- `name` (text, nullable): The user's full name.
- `role` (text): Defines user permissions. Restricted by a CHECK constraint to either `'user'` or `'admin'`. Defaults to `'user'`.
- `avatar_url` (text, nullable): URL to the user's profile picture.
- `created_at` (timestamptz): Timestamp of profile creation.
- `updated_at` (timestamptz): Timestamp of the last profile update.

### 2.2. `public.products`
This table holds our catalog of 33 active products, ranging from Electronics (like the Apple MacBook Air M3) to Fashion and Home goods.
- `id` (uuid, Primary Key): Unique identifier for the product.
- `name` (text): The product's title.
- `description` (text, nullable): Detailed product description.
- `price` (numeric): Current selling price (CHECK: `price >= 0`).
- `original_price` (numeric, nullable): Previous price for calculating discounts.
- `stock` (integer): Current inventory level (CHECK: `stock >= 0`). Defaults to 0.
- `category` (text): The product category (e.g., 'Electronics', 'Fashion', 'Home').
- `image_url` (text, nullable): URL for the product image.
- `rating` (numeric, nullable): Average user rating (CHECK: `rating >= 0 AND rating <= 5`).
- `review_count` (integer, nullable): Total number of reviews.
- `is_active` (boolean): Toggle for product visibility. Defaults to `true`.
- `created_at` (timestamptz): When the product was added.
- `updated_at` (timestamptz): When the product was last modified.

### 2.3. `public.cart`
Represents the current, un-purchased shopping carts of users.
- `id` (uuid, Primary Key): Unique cart item ID.
- `user_id` (uuid): Foreign key referencing `auth.users.id`.
- `product_id` (uuid): Foreign key referencing `public.products.id`.
- `quantity` (integer): Number of units added (CHECK: `quantity > 0`). Defaults to 1.
- `created_at` (timestamptz): When the item was added to the cart.

### 2.4. `public.orders`
Stores the high-level transactional data for completed purchases.
- `id` (uuid, Primary Key): The Order ID.
- `user_id` (uuid): Foreign key referencing `auth.users.id`.
- `total_price` (numeric): Final order total (CHECK: `total_price >= 0`).
- `status` (text): Order lifecycle state. Restricted by CHECK constraint to: `'pending'`, `'processing'`, `'shipped'`, `'delivered'`, or `'cancelled'`. Defaults to `'pending'`.
- `shipping_address` (jsonb, nullable): Stored as JSONB to preserve the exact address used at the time of order, protecting against future profile updates.
- `created_at` (timestamptz): Order placement time.
- `updated_at` (timestamptz): Last status update time.

### 2.5. `public.order_items`
Details the specific products purchased within an order. This acts as a historical snapshot.
- `id` (uuid, Primary Key): Line item ID.
- `order_id` (uuid): Foreign key referencing `public.orders.id`.
- `product_id` (uuid, nullable): Foreign key referencing `public.products.id`.
- `name` (text): A snapshot of the product's name at the time of purchase.
- `price` (numeric): A snapshot of the product's price at the time of purchase.
- `quantity` (integer): Units purchased (CHECK: `quantity > 0`).
- `image_url` (text, nullable): Snapshot of the product image URL.

## 3. RLS (Row Level Security)

All tables have RLS enabled (`rls_enabled: true`). This ensures:
- Users can only `SELECT`, `INSERT`, `UPDATE`, or `DELETE` their own rows in `profiles`, `cart`, and `orders`.
- The `products` table allows public `SELECT` access, but only users with `role = 'admin'` in their `profiles` can `INSERT`, `UPDATE`, or `DELETE` products.

## 4. RAG AI Integration Notes

When answering user questions regarding technical implementation or data architecture, the AI should reference this schema. For example, if a user asks how order statuses are tracked, the AI should explain the `status` field in the `public.orders` table and list the allowed ENUM values (`pending`, `processing`, `shipped`, `delivered`, `cancelled`). If asked about roles, the AI should mention the `role` field in `public.profiles`.
