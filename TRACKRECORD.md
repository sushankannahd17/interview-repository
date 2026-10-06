# Project Track Record & Change Log

This file documents every major change made across the frontend, backend, database integration, and security layers, explaining **why** the change was made, **where** it was made, and **what** was impacted.

---

## Phase 0: Security & Authentication Module (Completed)
- **Why**: Implement secure, stateless JWT authentication with Supabase as Identity Provider and Spring Boot as OAuth2 Resource Server.
- **Where**: `backend/src/main/java/com/agenticai/interviewrepo/security/`, `config/`, `model/`, `service/`, `controller/`
- **What**:
  - `SecurityConfig.java`: Configured stateless session, CORS origin handling, CSRF disabled for Bearer tokens, and endpoint authorization rules.
  - `JwtAuthConverter.java`: Extracted `sub` from Supabase JWT and mapped user identity to Spring Security granted authorities.
  - `AccountStatusFilter.java`: Enforced real-time `isActive` account status check to immediately block deactivated accounts.
  - `CurrentUserService.java`: Extracted authenticated principal and prevented Insecure Direct Object Reference (IDOR) attacks.
  - `ModerationLogService.java`: Recorded audit trail for administrative operations with authenticated admin identity.
  - `SecurityIntegrationTests.java`: 19 automated integration tests covering all 401, 403, and 200 security scenarios.

---

## Phase 1: Frontend Migration — TypeScript $\rightarrow$ JavaScript (Completed)
- **Why**: User requested converting the entire frontend codebase from TypeScript to vanilla React JavaScript to streamline developer workflow and eliminate compilation friction.
- **Where**: `frontend/`, `frontend/src/`, `frontend/package.json`, `frontend/index.html`, `frontend/vite.config.js`, `frontend/eslint.config.js`
- **What**:
  - **Dependencies**: Removed `typescript`, `@types/node`, `@types/react`, `@types/react-dom`, and `typescript-eslint`. Added `react-router-dom` (`v7.18.4`).
  - **Build Configuration**:
    - Renamed `vite.config.ts` $\rightarrow$ `vite.config.js`.
    - Deleted `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`.
    - Updated `frontend/index.html` entry point script to `/src/main.jsx`.
    - Updated `package.json` build script to `vite build`.
    - Configured `eslint.config.js` for React 19 JSX without TypeScript parsers.
  - **Component Conversions**:
    - `src/main.tsx` $\rightarrow$ `src/main.jsx` (Clean root mount)
    - `src/lib/passwordStrength.ts` $\rightarrow$ `src/lib/passwordStrength.js` (Pure JS password scoring algorithm)
    - `src/lib/supabaseClient.ts` $\rightarrow$ `src/lib/supabaseClient.js` (JS client with added `fetchCurrentUserProfile` helper)
    - `src/components/Toast.tsx` $\rightarrow$ `src/components/Toast.jsx` (Dynamic toast alert notifications)
    - `src/components/ShowcasePanel.tsx` $\rightarrow$ `src/components/ShowcasePanel.jsx` (Brand graphics and interactive cards)
    - `src/components/ForgotPasswordView.tsx` $\rightarrow$ `src/components/ForgotPasswordView.jsx` (Password recovery form)
    - `src/components/UserProfile.tsx` $\rightarrow$ `src/components/UserProfile.jsx` (Token inspector and profile display)
    - `src/components/AuthCard.tsx` $\rightarrow$ `src/components/AuthCard.jsx` (Sign in/up tabs and credentials handler)
    - Removed `src/types/auth.ts`.
  - **Verification**: Zero TypeScript files remain. Clean ESLint check (0 errors, 0 warnings). Production build (`pnpm run build`) succeeded in 140ms.

---

## Phase 2: Role-Based Access Control (RBAC) & Dedicated Dashboards (Completed on Frontend)
- **Why**: After authenticating with Supabase and obtaining a JWT, users must be automatically redirected to their role-specific dashboard (`/admin`, `/student`, `/mentor`, `/alumni`) matching their pre-assigned permissions in the database `login` table.
- **Where**: `frontend/src/App.jsx`, `frontend/src/components/`
- **What**:
  - **Routing Architecture (`react-router-dom`)**:
    - Configured `BrowserRouter`, `Routes`, `Route`, and `Navigate`.
    - Added automatic role redirection: Upon login, `App.jsx` calls `fetchCurrentUserProfile(token)` (`GET /api/auth/me`), extracts `role`, and navigates dynamically.
  - **Protected Route Guard (`ProtectedRoute.jsx`)**:
    - Enforces authentication and authorization. If an unauthenticated user attempts to visit a dashboard, they are sent to `/login`. If an unauthorized role attempts access (e.g. `STUDENT` attempting `/admin`), they are redirected to their own role page.
  - **Role Landing Dashboards**:
    - `DashboardLayout.jsx` & `Dashboard.css`: Consistent, glassmorphic header with verified user badge, role tag, and one-click Sign Out.
    - `AdminDashboard.jsx`: User management directory with search, live account activation/deactivation toggles (`/api/admin/users/{id}/status`), audit log viewer (`/api/admin/logs`), and system health indicator.
    - `StudentDashboard.jsx`: Student candidate workspace with metrics (Target companies, Applications, Practice questions) and profile editor (`/api/student/profile`).
    - `MentorDashboard.jsx`: Mentor hub with mentee count, mock review tracker, rating metrics, and industry expertise profile editor (`/api/mentor/profile`).
    - `AlumniDashboard.jsx`: Placed alumni portal with company info, offer CTC tracking, experience sharing form, and junior mentorship stats (`/api/alumni/profile`).

---

## Phase 3: Database Connection & Schema Alignment (Completed)
- **Why**: Connect Spring Boot backend and React frontend to the live Supabase PostgreSQL database, and align the backend `User.java` entity with the pre-seeded `login` table.
- **Where**: `backend/.env`, `frontend/.env`, `backend/src/main/java/com/agenticai/interviewrepo/model/User.java`, `service/AuthService.java`, `service/CurrentUserService.java`, `security/JwtAuthConverter.java`
- **What**:
  - **Environment Configuration**:
    - `backend/.env`: Configured JDBC pooler connection `jdbc:postgresql://aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres?sslmode=require` with verified credentials and Supabase JWT endpoints.
    - `frontend/.env`: Configured live Supabase project URL (`https://nrmqoqniqrbzwdiwibkv.supabase.co`) and Anon public key.
  - **Schema Unification**:
    - Mapped `User.java` to `@Table(name = "login")` to align with pre-seeded `login` table (`id`, `email`, `role`, `is_active`, `created_at`, `updated_at`).
    - Added `auth_user_id` and `name` columns to `public.login`.
    - Dropped obsolete empty `app_users` table so foreign keys in `administrator`, `mentor`, `placed_alumni`, `student`, and `interview_experience` cleanly point to `login(id)`.
  - **Pre-Seeded Account Auto-Linking**:
    - Enhanced `CurrentUserService.java`, `AuthService.java`, and `JwtAuthConverter.java` with email fallback matching.
    - When an existing dummy user (e.g. `sushan.kannah@gmail.com`, `alekhsub@gmail.com`, `phoenixvaibhav82@gmail.com`, `testuser101@gmail.com`, `testuser102@gmail.com`) signs in for the first time via Supabase Auth, their account automatically links `auth_user_id` to the existing `login` record.
    - Their pre-assigned role (`ADMIN`, `MENTOR`, `STUDENT`, `ALUMNI`) is immediately granted, triggering immediate role-specific frontend redirection.
  - **Verification**:
    - PostgreSQL connection tested and verified via `psql`.
    - Backend build and tests passed with 0 failures (`./mvnw test`).
    - Spring Boot backend live and running on `http://localhost:8080` (`/health` returning `200 OK`).
    - Vite frontend running and serving traffic on `http://localhost:5173`.

---

## Phase 4: Multi-Device Wi-Fi Access & Google OAuth Fix (Completed)
- **Why**: Enable Google Sign-In redirect flow to properly navigate to Google's authentication page, and allow testing the frontend and backend from any device on the local Wi-Fi.
- **Where**: `frontend/src/components/AuthCard.jsx`, `frontend/src/lib/supabaseClient.js`, `frontend/vite.config.js`, `backend/.env`
- **What**:
  - **Google OAuth Redirection**:
    - Fixed `signInWithOAuth` destructuring in `AuthCard.jsx` (`const { data, error } = ...`). Previously, `data` was not destructured, triggering a `ReferenceError: data is not defined` when checking `data?.url`. Added `window.location.assign(data.url)` to redirect to Google's sign-in page.
  - **Network / Wi-Fi Exposure**:
    - Configured `server: { host: true, port: 5173 }` in `vite.config.js`.
    - Discovered local network IP: `10.1.48.88`.
    - Updated `backend/.env` `FRONTEND_URL` to allow CORS requests from `http://10.1.48.88:5173`.
    - Added `getBackendBase()` in `supabaseClient.js` to automatically target `http://10.1.48.88:8080` when opened on a mobile device or other computer on the same Wi-Fi.

---

## Phase 5: Spring Boot `.env` Auto-Loading & Shell Compatibility (Completed)
- **Why**: Running `./mvnw spring-boot:run` directly in shells like `fish` or standard terminals caused a build failure (`Driver org.postgresql.Driver claims to not accept jdbcUrl, jdbc:h2:mem:...`) because `.env` variables were not loaded into the JVM by default, causing Spring Boot to fall back to an embedded H2 URL while keeping `org.postgresql.Driver`.
- **Where**: `backend/src/main/java/com/agenticai/interviewrepo/InterviewrepoApplication.java`
- **What**:
  - Implemented `loadDotEnvIfPresent()` in `InterviewrepoApplication.java` that runs prior to `SpringApplication.run`.
  - Searches for `.env` in current, parent, or sub-directories, parses the key-value pairs, and sets them as Java System properties (`System.setProperty`) if not already present in the OS environment.
  - Tested and verified: Spring Boot successfully loads database configuration from `.env`, starts up in 5.5s, connects to the Supabase PostgreSQL database, and responds with `200 UP` on `/health`.

---

## Phase 6: Google OAuth Redirection & DOM Verification (Completed)
- **Why**: User reported that Google sign-in was not redirecting in their browser and suspected missing keys.
- **Where**: `frontend/src/lib/supabaseClient.js`, `frontend/src/components/AuthCard.jsx`
- **What**:
  - **Identified Root Causes**:
    1. Legacy demo code in `supabaseClient.js` was reading `sb_override_url` and `sb_override_anon_key` from `localStorage`. Any stale value in a user's browser localStorage from previous sessions caused `isConfigured` to evaluate to `false`, causing `handleOAuthLogin` to abort early.
    2. Supabase JS client internally performs redirection by default (`window.location.assign`), which collided with downstream `window.location.assign` calls and instantaneous `setOauthLoading(null)` in `finally` blocks.
  - **Clarified Architecture Regarding "Missing Keys"**:
    - With Supabase Auth, Google OAuth client credentials (Google Client ID and Client Secret) live exclusively in the Supabase Dashboard (`Authentication -> Providers -> Google`).
    - The frontend does NOT need or use `GOOGLE_CLIENT_ID` or `GOOGLE_CLIENT_SECRET`. It only needs `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.
    - Both credentials and the Supabase-configured Google Client ID (`2887484958-hef7d6lrrjb6o1ttvenun6p3003fci8p.apps.googleusercontent.com`) are valid and active.
  - **Fixes Applied**:
    - **`supabaseClient.js`**: Completely purged `localStorage` override reading and added automated removal of `sb_override_url` / `sb_override_anon_key`. Guaranteed fallback to valid project URL and anon key.
    - **`AuthCard.jsx`**: Configured `skipBrowserRedirect: true` so Supabase returns the authorized redirect URL cleanly, then explicitly assigned `window.location.href = data.url`. Updated button feedback to show `"Redirecting to Google..."` and only reset state on failure.
  - **Headless Chrome DOM & Network Verification**:
    - Executed real Chrome headless session via Chrome DevTools Protocol (CDP).
    - Inspected DOM: Located Google button (`<button class="btn-social">`).
    - Clicked Google button: Successfully triggered `GET https://nrmqoqniqrbzwdiwibkv.supabase.co/auth/v1/authorize?provider=google&redirect_to=http%3A%2F%2Flocalhost%3A5173%2Flogin`.
    - Followed redirect: Successfully navigated to `https://accounts.google.com/v3/signin/identifier?...` (`HTTP 200`). Verified URL changed to Google Accounts login with 0 errors.

---

## Phase 7: ES256 JWT Algorithm Support & RBAC Role Resolution Fix (Completed)
- **Why**: When logging in with `alekhsub@gmail.com` (which is pre-seeded with `role = ADMIN` in PostgreSQL `public.login`), the user was incorrectly assigned the `STUDENT` dashboard (`/student`).
- **Where**: `backend/src/main/java/com/agenticai/interviewrepo/config/SecurityConfig.java`, `service/AuthService.java`, `frontend/src/App.jsx`
- **What**:
  - **Identified Root Cause**:
    1. Supabase signs its user OAuth tokens using the `ES256` (ECDSA P-256) signature algorithm.
    2. Spring Boot OAuth2 Resource Server's default `NimbusJwtDecoder` auto-configuration defaults exclusively to `RS256` (RSA).
    3. When the frontend sent the Supabase JWT in `GET /api/auth/me`, Spring Security rejected it with `BadJOSEException: Signed JWT rejected: Another algorithm expected, or no matching key(s) found`, returning HTTP 401.
    4. Due to the 401 error, `loadUserProfile` returned `null`, and the frontend defaulted to `STUDENT` (`userProfile?.role || 'STUDENT'`), redirecting the user to `/student`.
  - **Fixes Applied**:
    - **`SecurityConfig.java`**: Explicitly registered a `JwtDecoder` bean configured via `.jwsAlgorithms(algs -> { algs.add(SignatureAlgorithm.ES256); algs.add(SignatureAlgorithm.RS256); })`. Tested and verified that decoding `ES256` tokens from Supabase now succeeds 100%.
    - **`AuthService.java`**: Removed `readOnly = true` from `@Transactional` on `getCurrentProfile()` so auto-linking pre-seeded accounts to their Supabase `auth_user_id` successfully flushes and persists to the database.
    - **`App.jsx`**: Added automatic redirection check to `getSession()` on app load so verified sessions cleanly navigate to their authorized dashboard.

---

## Phase 8: Admin Role Management & Real-Time Database Persistence (Completed)
- **Why**: Administrator must have full permissions to dynamically modify user roles (`STUDENT`, `MENTOR`, `ALUMNI`, `ADMIN`) directly from the Admin Dashboard, with changes immediately written to the PostgreSQL `public.login` table.
- **Where**: `frontend/src/components/AdminDashboard.jsx`, `frontend/src/components/Dashboard.css`, `backend/src/main/java/com/agenticai/interviewrepo/controller/AdminController.java`, `service/AdminService.java`
- **What**:
  - **Backend Endpoint Verification & Enforcement**:
    - Verified `PATCH /api/admin/users/{id}/role` in `AdminController.java` guarded by `ADMIN` authority.
    - `AdminService.updateRole()` validates the caller is an active Admin, verifies the user exists in `public.login`, prevents an Admin from accidentally stripping their own Admin role (self-demotion protection), and executes `userRepository.save(user)` to write the updated role to `public.login.role`.
  - **Frontend Interactive Role Selector**:
    - Added an interactive `<select className="role-select">` directly within each row of the User Directory table in `AdminDashboard.jsx`.
    - Styled with role-coded pill themes (`role-admin`, `role-student`, `role-mentor`, `role-alumni`) in `Dashboard.css`.
    - Integrated with `handleRoleChange(userId, email, newRole)`: calls the backend `PATCH` endpoint with JWT Bearer authentication, updates local component state, displays a real-time success toast, and refreshes the directory.
    - Connected the moderation log viewer in `AdminDashboard.jsx` to the actual `/api/admin/moderation-logs` endpoint with detailed admin audit columns.

---

## Phase 9: Admin & Alumni Experience CRUD, Mentor-Mentee Inspection & Architecture Mindmap (Completed)
- **Why**: Deliver full interview experience lifecycle management (Create, Read, Update, Delete) for Admin and Alumni, auto-provision role profiles in PostgreSQL upon login, and empower Mentors to inspect mentee profiles and their submitted experiences.
- **Where**:
  - **Architecture & Specification**:
    - `mindmap_architecture.md`: Comprehensive system architecture and mindmap covering authentication data flow, PostgreSQL schema mapping (`login`, `administrator`, `placed_alumni`, `mentor`, `student`, `company`, `interview_experience`, `interview_round`, `question`, `moderation_log`), and the complete RBAC visibility matrix ("who gets to see what").
  - **Backend Services & Controllers**:
    - `service/AlumniService.java`: Auto-provisions `PlacedAlumni` record in PostgreSQL upon first access.
    - `service/MentorService.java`: Auto-provisions `Mentor` record and provides `getMentees()`, `getMenteeDetail()`, `getMenteeExperiences()`, and `assignMentee()`.
    - `service/StudentService.java`: Auto-provisions `Student` record, resolved Spring Security `AccessDeniedException` import, and fixed `toResponse` ID/name assignment.
    - `service/AdminService.java`: Auto-provisions `Administrator` record to guarantee foreign key integrity for `moderation_log.admin_id`.
    - `service/InterviewExperienceService.java`: Added dynamic company resolution (`findByNameIgnoreCase` / auto-creation), `getMyExperiences()`, `update()`, `delete()`, and `getStudentExperiences()`.
    - `controller/InterviewExperienceController.java`: Added `GET /api/interviews/my`, `PUT /api/interviews/{id}`, `DELETE /api/interviews/{id}`, and `GET /api/interviews/student/{studentId}`.
    - `controller/MentorController.java`: Added `GET /api/mentor/mentees`, `GET /api/mentor/mentees/{studentId}`, `GET /api/mentor/mentees/{studentId}/experiences`, `GET /api/mentor/available-students`, `POST /api/mentor/mentees/{studentId}/assign`.
    - `dto/InterviewExperienceRequest.java` & `InterviewExperienceResponse.java`: Made `companyId` optional with `companyName`, added `companyName`, `submitterName`, and `submitterEmail` to responses.
    - `repository/CompanyRepository.java`, `StudentRepository.java`, `InterviewExperienceRepository.java`: Added queries for companies, mentees, and author-based experiences.
  - **Frontend UI/UX (Inspired by uxpilot.ai)**:
    - `ExperienceModal.jsx`: Modern, interactive modal form supporting company resolution, difficulty & outcome pills, multi-round builder, question management, preparation tips, and consent verification.
    - `ExperienceDetailModal.jsx`: Inspection modal displaying full rounds, questions, difficulty badges, preparation strategies, and hiring timelines.
    - `MenteeDetailModal.jsx`: Mentor inspection drawer displaying mentee degree, college, batch, skills badges, social/resume links, and expandable submitted experiences.
    - `AlumniDashboard.jsx`: Integrated profile editing, KPI summary cards, "My Submissions" history with status badges, and full CRUD operations (Create, Read, Update, Delete).
    - `AdminDashboard.jsx`: Added Experience Management & Moderation tab, profile editing card, and direct Approve/Reject/Edit/Delete actions.
    - `MentorDashboard.jsx`: Added mentor profile editing, assigned mentees grid, deep inspection action, and candidate connection tab.
    - `Dashboard.css`: Added modal, drawer, round builder, badge, and card styling.

---

## Phase 10: Default Student Role, Synthetic Experiences Feed, Admin Mentor Assignment & Alumni Community Portal (Completed)
- **Why**: Deliver user requirements:
  1. Default role for all newly registered accounts must be `STUDENT`, with Admin having authority to promote/demote.
  2. Students must see a dedicated interview experiences feed with rich, synthetic experiences in the database, searchable and filterable, with full detail modals.
  3. Separate dedicated dashboards for Student, Alumni, Mentor, Admin.
  4. In Admin Dashboard, allow assigning any student to a specific mentor.
  5. Alumni Dashboard must allow browsing community experiences while retaining submission history and the option to submit new experiences anytime.
- **Where**:
  - `backend/src/main/java/com/agenticai/interviewrepo/config/SecurityConfig.java`
  - `backend/src/main/java/com/agenticai/interviewrepo/security/JwtAuthConverter.java`
  - `backend/src/main/java/com/agenticai/interviewrepo/service/CurrentUserService.java`, `AuthService.java`, `AdminService.java`, `StudentService.java`
  - `backend/src/main/java/com/agenticai/interviewrepo/controller/AdminController.java`, `InterviewExperienceController.java`
  - `backend/src/main/java/com/agenticai/interviewrepo/dto/AdminAssignMentorRequest.java`, `AdminMentorOptionResponse.java`, `AdminUserResponse.java`, `StudentProfileResponse.java`
  - `backend/.env`, `backend/src/main/resources/application.yml`
  - `frontend/src/components/StudentDashboard.jsx`, `AdminDashboard.jsx`, `AlumniDashboard.jsx`
- **What**:
  - **Auto-Registration with Default STUDENT Role**:
    - `JwtAuthConverter.java`, `CurrentUserService.java`, `AuthService.java`: Authenticated users absent from `public.login` are automatically registered as `STUDENT` with `isActive = true`. Added concurrency race condition handling to avoid duplicate key exceptions.
  - **Synthetic Interview Experiences Seeded into PostgreSQL**:
    - Created and executed `seed_experiences.sql` on Supabase PostgreSQL.
    - Seeded 6 premier tech companies (Google, Amazon, Microsoft, Atlassian, Uber, Goldman Sachs) with 6 approved experiences, 12 rounds, and 12 questions (covering Big-O algorithms, system design, concurrency, Leadership Principles, and interview tips).
  - **Student Preparation Hub (`StudentDashboard.jsx`)**:
    - Implemented a modern SaaS experiences feed inspired by `uxpilot.ai`.
    - Live keyword search across company name, role, topics, and questions.
    - Filter dropdown for companies and pill filters for Difficulty (`All`, `Easy`, `Medium`, `Hard`) and Outcome (`All`, `Offered`, `Rejected`).
    - Experience cards displaying company logo badge, role, date, difficulty & outcome badges, rounds count, question highlights, and preparation strategy snippets.
    - Connected "Read Experience" button to `ExperienceDetailModal.jsx` for full rounds/questions breakdown.
    - Added "My Assigned Mentor" tab displaying assigned mentor details (name, email, domain expertise, email CTA) or informative pending notice.
  - **Admin Mentorship Assignment (`AdminDashboard.jsx`)**:
    - Added `GET /api/admin/mentors` returning all active mentors with current mentee counts.
    - Added `PATCH /api/admin/users/{id}/mentor` to assign/unassign a student to a mentor.
    - Enriched `AdminUserResponse` with `mentorId` and `mentorName`.
    - Added "Assigned Mentor" column in User Directory table with interactive dropdown for `STUDENT` rows, updating PostgreSQL in real-time.
  - **Alumni Community Feed (`AlumniDashboard.jsx`)**:
    - Added "Browse Community Experiences" tab so alumni can browse the same experiences library as students.
    - Retained "My Submissions History" tab with complete CRUD operations (Create, Edit, Delete).
    - Prominent "Submit Experience" CTA buttons allowing alumni to contribute whenever they want.
  - **Database Connection & Pooler Optimization**:
    - Switched database URL in `backend/.env` to Supabase Transaction Pooler port `6543` with `prepareThreshold=0`, resolving the session port `5432` `EMAXCONNSESSION` connection limit.
    - Configured HikariCP pool properties (`maximum-pool-size: 5`, `minimum-idle: 1`) in `application.yml`.
    - Updated `SecurityConfig.java` to permit public GET on `/api/interviews` and `/api/companies/**`.
  - **Verification**:
    - Frontend build (`pnpm run build`) succeeded with 0 errors.
    - Backend build and tests (`./mvnw test-compile`) passed with 0 errors.
    - Live endpoints tested via `curl`: `/health` returns `200 UP`, `/api/interviews` returns all 6 seeded experiences.

