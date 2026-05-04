# User Accounts, Authentication, and Profile Management

## 1. Introduction

The user account system is the foundational identity layer of the e-commerce platform. It transforms anonymous browsers into recognized customers, enabling personalized experiences, secure transactions, and historical tracking. This document details the technical mechanics of authentication, the data structure of user profiles, and the self-service management capabilities provided to the customer.

For the RAG AI, understanding account mechanics is crucial, as issues related to login, password resets, and profile updates are among the highest volume support requests.

## 2. Authentication Architecture (Supabase Auth)

We leverage **Supabase Auth** as our identity provider. This system provides a robust, secure, and scalable backend for managing user credentials and session states.

### 2.1. The `auth.users` Database Table
Supabase maintains a secure, isolated schema specifically for authentication (`auth.users`). This table stores the core identity data:
- **UUID:** A globally unique identifier for the user. This is the ultimate reference point linking a user to their orders, cart, and profile data in the public schemas.
- **Email Address:** Serves as the primary unique identifier for login.
- **Encrypted Password:** Passwords are never stored in plain text. They are hashed using robust cryptographic algorithms (e.g., bcrypt or Argon2) with unique salts. Even database administrators cannot see user passwords.
- **Authentication Metadata:** Data regarding last sign-in time, email confirmation status, and authentication providers used.

### 2.2. Session Management via JWT
When a user successfully logs in, Supabase issues a **JSON Web Token (JWT)**.
- **Stateless Authentication:** The backend API does not need to look up the database for every request to verify if a user is logged in. Instead, the frontend attaches this JWT to the header of every API request. The backend cryptographically verifies the token's signature.
- **Token Expiry and Refresh:** JWTs are intentionally short-lived (e.g., expiring in 1 hour) for security. However, Supabase also issues a long-lived "Refresh Token." When the JWT expires, the frontend automatically uses the Refresh Token to request a new JWT behind the scenes, keeping the user seamlessly logged in without forcing them to re-enter their credentials constantly.

## 3. Account Creation and Onboarding

The process of converting a guest to a registered user must be smooth but secure.

### 3.1. Registration Flow
1. The user provides their Email, Password, and basic details (First Name, Last Name).
2. The frontend validates the inputs (e.g., ensuring the password meets complexity requirements: minimum 8 characters, inclusion of numbers/special characters).
3. The data is sent to the Supabase Auth signup endpoint.
4. Supabase creates the user record in `auth.users` and simultaneously triggers a database trigger to create a corresponding row in the public `users` profile table.

### 3.2. Email Verification (Double Opt-In)
To prevent spam accounts and ensure communication lines are valid, we employ email verification.
- Upon registration, the account is created but placed in an "unverified" state.
- Supabase dispatches an email containing a secure, unique confirmation link.
- The user must click this link to verify their email address. Until this happens, their ability to place orders or access certain platform features may be restricted.

## 4. The User Profile: Data and Management

Once authenticated, the user has access to a dedicated "Profile" dashboard. This is their control center.

### 4.1. The Public `users` Table Structure
While `auth.users` handles secure login data, the public `users` table stores the application-level data.
- **User ID (`id`):** The foreign key matching the Supabase Auth UUID.
- **Name Data:** First Name, Last Name.
- **Contact Information:** Phone number (optional).
- **Role:** Typically defaults to 'customer'. This field is critical for Role-Based Access Control (RBAC); if this field is changed to 'admin', the user gains access to the backend dashboard.
- **Created Timestamp:** When the account was registered.

### 4.2. Profile Management Capabilities
Within the Profile interface, users can perform several self-service actions:
- **Personal Details Update:** Modifying their name or phone number.
- **Address Book Management:** Users can save multiple shipping and billing addresses to expedite future checkouts. They can designate one as the "Default" address.
- **Password Reset:** Initiating a password change securely while logged in.
- **Order History:** A comprehensive, paginated list of all past and current orders, linking to detailed views (as described in the Orders documentation).

## 5. Account Security and Recovery

### 5.1. The "Forgot Password" Flow
If a user forgets their password, they must prove ownership of the email address.
1. User enters their email in the "Forgot Password" form.
2. Supabase generates a temporary, single-use, time-limited reset token.
3. An email is dispatched with a link containing this token.
4. Clicking the link takes the user to a specific reset page on the frontend, where they can enter a new password. The token is consumed and invalidated upon successful reset.

### 5.2. Account Deletion (GDPR/CCPA Compliance)
Users have the right to request the deletion of their personal data.
- Deleting an account involves removing the identity from `auth.users` and the profile from the `users` table.
- However, financial records (like past `orders`) must often be retained for legal, tax, and accounting purposes. In these cases, the user data on the order record is typically anonymized or pseudonymized, severing the link to the deleted identity while preserving the transaction's financial integrity.

## 6. RAG Interaction Guidelines

When assisting users with account issues, the AI must adhere to strict security protocols:
- **Never Handle Credentials:** The AI must never ask for, accept, or attempt to process a user's password.
- **Guidance Over Execution:** If a user says "Change my password to X", the AI must politely refuse and instead provide step-by-step instructions on how the user can use the "Forgot Password" link or navigate to their Profile to change it themselves.
- **Explaining Verification:** If a user complains they cannot log in immediately after registering, the AI should remind them to check their email (including spam folders) for the verification link.
- **Addressing Login Failures:** Guide users experiencing persistent login failures to clear their browser cache, ensure they are not using a VPN that might trigger security blocks, or utilize the password reset function.
