import { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { getSupabaseClient, fetchCurrentUserProfile } from './lib/supabaseClient';
import { ProtectedRoute, ProfileGate } from './components/ProtectedRoute';
import { ToastContainer } from './components/Toast';
import './components/Auth.css';

const AuthPage = lazy(() => import('./components/AuthPage').then((module) => ({ default: module.AuthPage })));
const StudentDashboard = lazy(() => import('./components/StudentDashboard').then((module) => ({ default: module.StudentDashboard })));
const MentorDashboard = lazy(() => import('./components/MentorDashboard').then((module) => ({ default: module.MentorDashboard })));
const AlumniDashboard = lazy(() => import('./components/AlumniDashboard').then((module) => ({ default: module.AlumniDashboard })));
const DashboardPage = lazy(() => import('./components/admin/DashboardPage').then((module) => ({ default: module.DashboardPage })));
const StudentsPage = lazy(() => import('./components/admin/StudentsPage').then((module) => ({ default: module.StudentsPage })));
const MentorsPage = lazy(() => import('./components/admin/MentorsPage').then((module) => ({ default: module.MentorsPage })));
const AlumniPage = lazy(() => import('./components/admin/AlumniPage').then((module) => ({ default: module.AlumniPage })));
const ModerationPage = lazy(() => import('./components/admin/ModerationPage').then((module) => ({ default: module.ModerationPage })));

function AppContent() {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [profileError, setProfileError] = useState(null);
  const [initializing, setInitializing] = useState(true);
  const [toasts, setToasts] = useState([]);
  const navigate = useNavigate();

  const showToast = useCallback((type, message, title) => {
    const id = Date.now().toString() + Math.random().toString(36).substring(2, 5);
    setToasts((prev) => [...prev, { id, type, message, title }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  }, []);

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const loadUserProfile = async (token) => {
    if (!token) return;
    const res = await fetchCurrentUserProfile(token);
    if (res.success && res.data) {
      setProfileError(null);
      setUserProfile(res.data);
      return res.data;
    }
    setUserProfile(null);
    setProfileError(res.error || 'Could not load your account.');
    return null;
  };

  const retryProfile = async () => {
    setProfileError(null);
    const client = getSupabaseClient();
    const {
      data: { session: current },
    } = await client.auth.getSession();
    if (current?.access_token) await loadUserProfile(current.access_token);
    else navigate('/login', { replace: true });
  };

  const signOut = async () => {
    try {
      await getSupabaseClient().auth.signOut();
    } finally {
      setUserProfile(null);
      setProfileError(null);
      navigate('/login', { replace: true });
    }
  };

  const getRoleDestination = (role) => {
    switch (role?.toUpperCase()) {
      case 'ADMIN':
        return '/admin/dashboard';
      case 'MENTOR':
        return '/mentor';
      case 'ALUMNI':
        return '/alumni';
      case 'STUDENT':
      default:
        return '/student';
    }
  };

  useEffect(() => {
    let unsubscribeFn = null;
    try {
      const client = getSupabaseClient();

      client.auth.getSession().then(async ({ data: { session }, error }) => {
        if (!error && session) {
          setSession(session);
          setUser(session.user);
          const profile = await loadUserProfile(session.access_token);
          if (profile?.role) {
            const currentPath = window.location.pathname;
            if (currentPath === '/' || currentPath === '/login') {
              navigate(getRoleDestination(profile.role), { replace: true });
            }
          }
        } else {
          setSession(null);
          setUser(null);
          setUserProfile(null);
        }
        setInitializing(false);
      });

      const {
        data: { subscription },
      } = client.auth.onAuthStateChange(async (_event, session) => {
        setSession(session);
        setUser(session?.user ?? null);
        if (session) {
          const profile = await loadUserProfile(session.access_token);
          if (profile?.role) {
            // Auto-redirect to appropriate role page if currently at root or login
            const currentPath = window.location.pathname;
            if (currentPath === '/' || currentPath === '/login') {
              navigate(getRoleDestination(profile.role), { replace: true });
            }
          }
        } else {
          setUserProfile(null);
          setProfileError(null);
        }
        setInitializing(false);
      });

      unsubscribeFn = () => subscription.unsubscribe();
    } catch {
      queueMicrotask(() => {
        setInitializing(false);
      });
    }

    return () => {
      if (unsubscribeFn) unsubscribeFn();
    };
  }, [navigate]);

  const handleLoginSuccess = async (newSession) => {
    if (!newSession?.access_token) return;
    const profile = await loadUserProfile(newSession.access_token);
    // Only route once the real role is known; on failure the ProfileGate shows the reason.
    if (profile?.role) navigate(getRoleDestination(profile.role), { replace: true });
  };

  const currentRole = userProfile?.role?.toUpperCase();
  const gate = <ProfileGate profileError={profileError} onRetry={retryProfile} onSignOut={signOut} />;

  return (
    <>
      <Suspense fallback={<div role="status" style={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}>Loading page…</div>}>
      <Routes>
        {/* Public Login Route */}
        <Route
          path="/login"
          element={
            user ? (
              currentRole ? <Navigate to={getRoleDestination(currentRole)} replace /> : gate
            ) : (
              <AuthPage
                onShowToast={showToast}
                onLoginSuccess={handleLoginSuccess}
              />
            )
          }
        />

        {/* Root Route: Redirect based on authentication status */}
        <Route
          path="/"
          element={
            user ? (
              currentRole ? <Navigate to={getRoleDestination(currentRole)} replace /> : gate
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Role-Based Protected Routes */}
        <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />

        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute
              user={user}
              userProfile={userProfile}
              initializing={initializing}
              profileError={profileError}
              onRetryProfile={retryProfile}
              onSignOut={signOut}
              allowedRoles={['ADMIN']}
            >
              <DashboardPage
                user={user}
                session={session}
                userProfile={userProfile}
              />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/students"
          element={
            <ProtectedRoute
              user={user}
              userProfile={userProfile}
              initializing={initializing}
              profileError={profileError}
              onRetryProfile={retryProfile}
              onSignOut={signOut}
              allowedRoles={['ADMIN']}
            >
              <StudentsPage
                user={user}
                session={session}
                userProfile={userProfile}
              />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/mentors"
          element={
            <ProtectedRoute
              user={user}
              userProfile={userProfile}
              initializing={initializing}
              profileError={profileError}
              onRetryProfile={retryProfile}
              onSignOut={signOut}
              allowedRoles={['ADMIN']}
            >
              <MentorsPage
                user={user}
                session={session}
                userProfile={userProfile}
              />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/alumni"
          element={
            <ProtectedRoute
              user={user}
              userProfile={userProfile}
              initializing={initializing}
              profileError={profileError}
              onRetryProfile={retryProfile}
              onSignOut={signOut}
              allowedRoles={['ADMIN']}
            >
              <AlumniPage
                user={user}
                session={session}
                userProfile={userProfile}
              />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/moderation"
          element={
            <ProtectedRoute
              user={user}
              userProfile={userProfile}
              initializing={initializing}
              profileError={profileError}
              onRetryProfile={retryProfile}
              onSignOut={signOut}
              allowedRoles={['ADMIN']}
            >
              <ModerationPage
                user={user}
                session={session}
                userProfile={userProfile}
              />
            </ProtectedRoute>
          }
        />

        <Route
          path="/student/*"
          element={
            <ProtectedRoute
              user={user}
              userProfile={userProfile}
              initializing={initializing}
              profileError={profileError}
              onRetryProfile={retryProfile}
              onSignOut={signOut}
              allowedRoles={['STUDENT']}
            >
              <StudentDashboard
                user={user}
                session={session}
                userProfile={userProfile}
              />
            </ProtectedRoute>
          }
        />

        <Route
          path="/mentor"
          element={
            <ProtectedRoute
              user={user}
              userProfile={userProfile}
              initializing={initializing}
              profileError={profileError}
              onRetryProfile={retryProfile}
              onSignOut={signOut}
              allowedRoles={['MENTOR']}
            >
              <MentorDashboard
                user={user}
                session={session}
                userProfile={userProfile}
              />
            </ProtectedRoute>
          }
        />

        <Route
          path="/alumni"
          element={
            <ProtectedRoute
              user={user}
              userProfile={userProfile}
              initializing={initializing}
              profileError={profileError}
              onRetryProfile={retryProfile}
              onSignOut={signOut}
              allowedRoles={['ALUMNI']}
            >
              <AlumniDashboard
                user={user}
                session={session}
                userProfile={userProfile}
              />
            </ProtectedRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      </Suspense>

      {/* Global Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
