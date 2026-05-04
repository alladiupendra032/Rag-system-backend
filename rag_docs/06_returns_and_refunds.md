# Returns, Refunds, and Exchange Policies

## 1. Introduction

This document outlines the comprehensive policies and operational procedures regarding product returns, financial refunds, and item exchanges. A clear, fair, and easily understandable return policy is critical for building customer trust and mitigating purchase hesitation. For the RAG AI assistant, this document serves as the absolute source of truth when advising customers on how to send items back, what conditions apply, and when they can expect their money back.

## 2. Core Return Policy Framework

Our platform operates on a customer-centric return philosophy, balanced with necessary protections against fraud and inventory degradation.

### 2.1. The Return Window
We offer a standard **30-day return window**. 
- **Start Date:** The 30-day period begins on the date the order status is marked as 'Delivered' by the courier, *not* the date the order was placed.
- **Expiration:** If a return is not initiated within this 30-day timeframe via the customer portal or support channels, the sale is considered final, and the system will no longer accept automated return requests for that specific order item.

### 2.2. Condition of Returned Items
To be eligible for a full refund, the item must meet strict condition criteria:
- **Unused and Unworn:** The item must be in its original, brand-new condition. 
- **Original Packaging:** It must be returned in its original, undamaged packaging, complete with all original tags, protective films, manuals, and accessories.
- **Hygiene and Safety Seals:** Certain items (like intimate apparel, opened software, or consumable goods) cannot be returned once their hygiene or safety seals have been broken, unless the item is fundamentally defective out of the box.

### 2.3. Proof of Purchase
A valid proof of purchase is required for all returns. Because our platform mandates user accounts for purchases, the digital order history stored in the `orders` database table serves as the primary proof of purchase. The Order ID must be referenced in all return communications.

## 3. The Return Procedure (Step-by-Step)

The RAG AI must be capable of guiding a user through this exact workflow.

1.  **Initiation:** The customer logs into their account, navigates to their Profile, and selects "Order History." They locate the specific order and click the "Request Return" button next to the eligible item.
2.  **Reason Selection:** The system prompts the user to select a reason for the return from a predefined list (e.g., "Wrong size," "Item defective," "Changed my mind," "Item differs from description"). Providing a reason is mandatory as it feeds into our quality control analytics.
3.  **Authorization (RMA Generation):** If the request is within the 30-day window and the item is fundamentally eligible, the system automatically generates a Return Merchandise Authorization (RMA) number.
4.  **Label Generation:** The system generates a printable, pre-paid return shipping label (PDF) via an integration with our shipping partners. The cost of this label is generally deducted from the final refund amount unless the return is due to our error (e.g., defective item, wrong item sent).
5.  **Packaging and Shipping:** The customer is instructed to securely pack the item, attach the RMA label to the outside of the box, and drop it off at the designated courier location within 14 days of label generation.
6.  **Inspection:** Once the package arrives at our returns processing facility, warehouse staff inspect the item against the stated return reason and condition requirements.
7.  **Resolution:** Based on the inspection, the return is either 'Approved' or 'Rejected'.

## 4. Refund Processing and Financial Logic

Understanding how and when money is returned is the most frequent question handled by support.

### 4.1. Refund Timelines
- **Inspection Period:** Upon physical receipt of the return, it takes our facility 2 to 3 business days to inspect the item.
- **Issuance:** Once approved, the refund is immediately triggered by our backend systems communicating with the payment gateway (e.g., Stripe).
- **Bank Processing Time:** *Crucially*, while we issue the refund instantly, it typically takes the customer's bank or credit card company an additional **3 to 7 business days** to post the funds back to their account. The AI must explicitly state this external delay to prevent follow-up complaints.

### 4.2. Original Form of Payment
Refunds are strictly issued back to the original form of payment used for the purchase. We cannot refund to a different credit card or issue a bank transfer if the original payment was made via credit card. If the original card is cancelled or expired, the customer must negotiate with their bank, as the gateway will route the funds to the account associated with the old card.

### 4.3. Non-Refundable Costs
- **Original Shipping Fees:** If the customer paid for Expedited or Overnight shipping on the original order, those shipping fees are non-refundable. Only the cost of the product itself and associated taxes are refunded.
- **Return Shipping Deductions:** As noted, if the return is for "buyer's remorse" (changed mind, wrong size ordered), a standard return shipping fee (e.g., $5.99) is deducted from the refund total to cover the cost of the pre-paid label. If the item was defective or incorrect, this fee is waived, resulting in a full refund.

## 5. Exchanges

Our system handles exchanges as a two-step process: Return and Re-order.

- **Why?** Handling direct, asynchronous exchanges (e.g., swapping a size Medium for a size Large) creates significant complexities regarding inventory management and price fluctuations. If the Large size goes out of stock while the Medium is in transit back to us, the exchange fails.
- **The Protocol:** We require the customer to initiate a standard return for the unwanted item for a refund. They are then advised to immediately place a completely new, separate order for the desired item (the new size/color). This ensures the new item's stock is instantly secured and shipped without waiting for the return process to conclude.

## 6. Damaged, Defective, or Incorrect Items

Exceptions are made when the fault lies with the platform or the manufacturer.

- **Immediate Reporting:** If a customer receives an item that is physically damaged in transit, fundamentally defective, or incorrect (e.g., ordered a red shirt, received a blue one), they must report it to support within **48 hours** of delivery.
- **Evidence Requirement:** We typically require photographic evidence of the damage or the incorrect item to be uploaded to the support ticket.
- **Resolution:** For these specific cases, we waive all return shipping fees. Upon verification, the customer may choose between a full refund (including original shipping costs) or a free, expedited replacement sent immediately (without waiting for the return to arrive back at our facility).

## 7. RAG Interaction Guidelines

When addressing return inquiries, the AI must:
1.  **Always ask for the Order Date:** Before confirming eligibility, the AI must establish if the order is within the 30-day window.
2.  **Explain the Financial Flow:** Always clarify that return shipping costs may be deducted and explicitly mention the 3-7 day bank processing delay.
3.  **Explain the Exchange Policy:** Clearly articulate that exchanges are processed as a return followed by a new purchase to guarantee stock availability.
4.  **Empathize with Damage Claims:** If a user reports a defective item, the AI should express regret for the inconvenience and urgently guide them to contact human support with photographic evidence to expedite a replacement.
