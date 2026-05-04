# Shipping, Delivery, and Fulfillment Protocols

## 1. Introduction

This document details the logistical protocols and theoretical frameworks governing the shipping and delivery of physical goods purchased on the e-commerce platform. For a Retrieval-Augmented Generation (RAG) AI, this information is critical, as shipping inquiries ("When will this arrive?", "How much is shipping?") constitute a significant percentage of customer support interactions.

The platform is designed to provide transparent, reliable, and reasonably fast delivery services while managing the logistical complexities in the backend.

## 2. Shipping Methods and Options

We offer multiple shipping tiers to accommodate different customer needs regarding speed and cost. These options are presented to the user during the checkout flow, after they have entered their shipping address but before final payment confirmation.

### 2.1. Standard Shipping
- **Theoretical Speed:** 3 to 7 business days from the date of order processing.
- **Cost Structure:** Often offered at a flat rate, or calculated dynamically based on the total weight of the cart and the distance to the destination.
- **Promotional Usage:** We frequently offer "Free Standard Shipping" as a promotional tool, typically triggered when the `cart.total_price` exceeds a specific threshold (e.g., "Free Shipping on orders over $50").

### 2.2. Expedited (Two-Day) Shipping
- **Theoretical Speed:** Guaranteed delivery within 2 business days from the date of processing.
- **Cost Structure:** Incurs a premium flat fee.
- **Limitations:** May not be available for certain remote geographic locations or for extremely oversized items (which require freight shipping).

### 2.3. Overnight (Next-Day) Shipping
- **Theoretical Speed:** Delivery by the end of the next business day.
- **Cost Structure:** The most expensive tier.
- **Cut-off Times:** Crucially, next-day shipping relies on strict processing cut-off times. For example, an order must be placed before 2:00 PM EST to be processed and handed to the courier the same day. Orders placed after the cut-off are processed the following business day. The AI must understand this nuance when setting delivery expectations.

## 3. The Fulfillment Process Pipeline

Understanding the timeline between clicking "Buy" and the package arriving at the door is essential for managing customer expectations.

### 3.1. Order Processing Time
"Processing time" is distinct from "Shipping time." Processing is the internal warehouse operation required to prepare the order.
- Typically, processing takes 1 to 2 business days.
- During peak seasons (holidays, major sales), processing times may theoretically extend. The AI should be programmed to recognize these periods and adjust its answers accordingly.
- An order's status remains 'Pending' or 'Processing' during this phase.

### 3.2. Handover to Courier
Once the package is packed and a shipping label is generated, it is physically handed over to a third-party logistics provider (e.g., FedEx, UPS, USPS).
- At this exact moment, the backend system updates the `orders.status` to 'Shipped'.
- A Tracking Number is injected into the database record.
- An automated notification (email/SMS) is dispatched to the customer containing this tracking information.

### 3.3. Transit Time
This is the duration the package spends in the courier's network. This duration correlates directly with the Shipping Method selected at checkout (Standard, Expedited, etc.).

*Note: Total Delivery Time = Order Processing Time + Transit Time.* The AI must always communicate this clearly to avoid customer frustration. If an item takes 2 days to process and 3 days to ship, the customer receives it in 5 days, not 3.

## 4. Geographic Shipping Zones and Restrictions

The platform's shipping logic is constrained by geographic realities.

### 4.1. Domestic Shipping
We currently provide comprehensive shipping coverage across the contiguous United States.
- **Non-Contiguous Areas:** Shipping to Alaska, Hawaii, Puerto Rico, and other territories may incur higher fees and longer transit times. Expedited options are often unavailable for these regions.

### 4.2. International Shipping
At this stage in the platform's MVP lifecycle, international shipping is **not supported**. The checkout system will reject addresses outside the supported domestic zones. If a user asks the AI about international shipping, the AI must clearly state this limitation.

### 4.3. P.O. Boxes and APO/FPO Addresses
- Standard shipping is generally available to P.O. Boxes via national postal services.
- Expedited and Overnight shipping options via private couriers (like FedEx or UPS) generally **cannot** deliver to P.O. Boxes. The checkout validation logic enforces this rule.

## 5. Tracking and Visibility

Transparency is key to a positive customer experience.
- **The Tracking Link:** The most vital piece of information post-purchase is the tracking link. This link directs the user to the specific courier's tracking portal.
- **Backend Integration:** In future iterations, the platform may integrate via webhooks with couriers to pull tracking events (e.g., "Out for Delivery") directly into our database, allowing users to track their packages natively within their Profile page without leaving the site.
- **"Lost in Transit" Protocol:** If tracking shows no movement for an extended period (typically 7+ days past the expected delivery date), the customer is advised to contact support. We then initiate an investigation with the courier and, if deemed lost, either issue a replacement order or a full refund.

## 6. RAG Interaction Guidelines for Shipping

When queried about shipping, the RAG AI should employ the following logic:

1.  **Cost Inquiries:** If asked "How much is shipping?", the AI should explain the dynamic nature of shipping costs (based on weight/distance) but immediately highlight the "Free Shipping over $X" threshold as a positive selling point.
2.  **Delivery Time Estimates:** If asked "When will I get my order?", the AI must differentiate between processing time and transit time, clearly outlining the options (Standard vs. Expedited).
3.  **Tracking Status:** If an authenticated user asks "Where is my package?", the AI should check the order status. If 'Shipped', it must provide the tracking number. If 'Pending', it should remind the user of the standard processing time.
4.  **International Inquiries:** Firmly but politely inform users that international fulfillment is currently unavailable.
