# Admin Guide: E-Commerce Web Platform

## 1. Introduction
This document serves as the operational manual for Administrators of the E-Commerce Web Platform. It details the capabilities and responsibilities of the admin role, specifically tailored to our current architecture and dataset.

## 2. Administrator Access
To gain access to the Admin Dashboard:
1. You must have a registered account on the platform.
2. Your account's `role` field in the `public.profiles` database table must be set to `'admin'` (the default is `'user'`). 
3. Note: The AI assistant cannot elevate user roles. This must be done directly via the Supabase database interface by a superuser.

## 3. Managing the Product Catalog
Our store currently boasts an active catalog of **33 products** across Electronics, Fashion, and Home categories. Admins are responsible for maintaining this data.

### 3.1. Inventory Management
The most critical task is monitoring the `stock` levels in the `products` table.
- When an order is placed, stock is decremented automatically.
- If an order is cancelled, stock must be manually or programmatically restored.
- Example: We currently have 45 units of the "Apple MacBook Air M3" in stock. If 45 are sold, the stock becomes 0, and the frontend will display it as "Out of Stock". Admins must restock and update the value when new shipments arrive.

### 3.2. Price Adjustments
Admins can modify the `price` and `original_price` fields.
- The `price` field dictates the current selling cost.
- The `original_price` field is used to calculate and display discounts on the frontend (e.g., The "Samsung 4K OLED TV 55\"" has a `price` of $1199.00 and an `original_price` of $1499.00, showing a $300 discount).

### 3.3. Adding New Products
When adding new products, ensure all required fields are filled:
- A descriptive `name` and `description`.
- A valid `price` (must be >= 0).
- An initial `stock` count.
- The correct `category` (Electronics, Fashion, or Home).
- An `image_url` hosted securely (preferably in Supabase Storage).

## 4. Managing Orders
The `public.orders` table tracks all customer purchases. Admins must manage the lifecycle of these orders.

### 4.1. The Order Status Workflow
Orders transition through specific states defined in our database schema:
1.  **`pending`**: The order is placed and payment is authorized. This is the default state upon creation.
2.  **`processing`**: Admin manually updates the order to this state when the warehouse begins picking and packing the items.
3.  **`shipped`**: Admin updates the state to shipped when the package is handed to the courier. Tracking information should be communicated to the customer.
4.  **`delivered`**: The final successful state, indicating the customer received the package.
5.  **`cancelled`**: Can be triggered if an item is out of stock, payment fails post-authorization, or the customer requests cancellation before shipping.

### 4.2. Handling Returns and Refunds
Currently, refunds must be processed via the payment gateway's external dashboard (e.g., Stripe). Once the financial refund is complete, the admin must:
1. Update the order status to `cancelled` or a custom "refunded" state if implemented.
2. Manually increment the `stock` of the returned items in the `products` table if the items are in sellable condition.

## 5. RAG AI Assistant Guidelines
The RAG AI is programmed to assist customers, not perform admin actions.
- The AI **cannot** change product prices, update stock levels, or alter order statuses.
- If an admin asks the AI to perform these actions, the AI must politely decline and direct the admin to use the official Admin Dashboard UI or direct Supabase SQL queries.
