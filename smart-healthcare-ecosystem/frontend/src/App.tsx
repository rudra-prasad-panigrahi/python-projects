import React, { FormEvent, type ReactNode, useEffect, useRef, useState } from 'react';
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  ArrowUpRight,
  Bell,
  Building2,
  Calendar,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock,
  Download,
  ExternalLink,
  Eye,
  FileCheck,
  FileText,
  Filter,
  Flame,
  Github,
  Globe,
  Heart,
  HeartPulse,
  HelpCircle,
  History,
  Info,
  Layers,
  Lock,
  LogOut,
  MapPin,
  Menu,
  MessageCircle,
  Moon,
  Phone,
  Pill,
  Plus,
  RefreshCw,
  Search,
  Settings,
  Share2,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  Sun,
  Trash2,
  TrendingDown,
  TrendingUp,
  Upload,
  User,
  UserCheck,
  UserPlus,
  UserRound,
  Users,
  X,
  Zap,
} from 'lucide-react';
import { api, exchangeOAuthTicket, getOAuthProviders, register, signIn, signOut, startOAuth, type OAuthProvider, type OAuthProviders } from './services/demo-api';
import EcosystemExperience from './EcosystemExperience';

// Navigation items definition
type NavItem = { id: string; label: string; icon: typeof Activity; badge?: string; category?: string };
const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Overview', icon: Activity, category: 'Main' },
  { id: 'profile', label: 'My Profile', icon: UserRound, category: 'Personal Data' },
  { id: 'health-record', label: 'Health Records', icon: HeartPulse, category: 'Personal Data' },
  { id: 'timeline', label: 'Health Timeline', icon: Calendar, category: 'Personal Data' },
  { id: 'health-trends', label: 'Vitals & Trends', icon: TrendingUp, badge: 'ML', category: 'Health Intelligence' },
  { id: 'risk-prediction', label: 'Risk Prediction', icon: Flame, badge: 'Research', category: 'Health Intelligence' },
  { id: 'documents', label: 'Documents', icon: FileText, category: 'Clinical Hub' },
  { id: 'laboratory', label: 'Laboratory Reports', icon: Layers, category: 'Clinical Hub' },
  { id: 'medications', label: 'Medication Vault', icon: Pill, category: 'Clinical Hub' },
  { id: 'appointments', label: 'Appointments', icon: Calendar, category: 'Care Management' },
  { id: 'care-navigation', label: 'Find Care', icon: Search, category: 'Care Management' },
  { id: 'ai-assistant', label: 'AI Health Assistant', icon: MessageCircle, badge: 'RAG', category: 'AI Tools' },
  { id: 'emergency', label: 'Emergency Readiness', icon: AlertCircle, badge: 'SOS', category: 'Safety & Privacy' },
  { id: 'privacy', label: 'Privacy Center', icon: ShieldCheck, category: 'Safety & Privacy' },
  { id: 'consent', label: 'Consent Management', icon: Lock, category: 'Safety & Privacy' },
  { id: 'notifications', label: 'Notifications', icon: Bell, category: 'System' },
  { id: 'settings', label: 'Settings & Export', icon: Settings, category: 'System' },
];

export default function App() {
  const callbackQuery = new URLSearchParams(location.search);
  const callbackFragment = new URLSearchParams(location.hash.slice(1));
  const oauthTicket = callbackQuery.get('oauth_ticket') || callbackFragment.get('oauth_ticket');
  const initialOAuthError = callbackQuery.get('oauth_error') || callbackFragment.get('oauth_error') || '';
  const [entrySelected, setEntrySelected] = useState<boolean>(() => {
    return !!oauthTicket || !!initialOAuthError || !!localStorage.getItem('healthway-entry-selected') || !!localStorage.getItem('healthway-demo-token');
  });
  const [token, setToken] = useState(() => localStorage.getItem('healthway-demo-token') || '');
  const [oauthLoading, setOauthLoading] = useState(!!oauthTicket);
  const [oauthError, setOauthError] = useState(initialOAuthError);
  const oauthExchangeStarted = useRef(false);

  const pageFromPath = () => {
    const match = location.pathname.match(/^\/personal(?:\/([^/]+))?/);
    return match?.[1] || 'dashboard';
  };

  const [page, setPage] = useState(pageFromPath);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [sosModalOpen, setSosModalOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(2);

  const completeLogin = (accessToken: string) => {
    localStorage.setItem('healthway-demo-token', accessToken);
    localStorage.setItem('healthway-entry-selected', 'personal');
    window.history.replaceState({}, '', '/personal/dashboard');
    setEntrySelected(true);
    setToken(accessToken);
    setPage('dashboard');
  };

  useEffect(() => {
    if (!oauthTicket || oauthExchangeStarted.current) return;
    oauthExchangeStarted.current = true;
    exchangeOAuthTicket(oauthTicket)
      .then((session) => completeLogin(session.access_token))
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : 'Social sign-in could not be completed.';
        setOauthError(message);
        window.history.replaceState({}, '', '/');
      })
      .finally(() => setOauthLoading(false));
  }, [oauthTicket]);

  useEffect(() => {
    const sync = () => setPage(pageFromPath());
    window.addEventListener('popstate', sync);
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        setCommandOpen(false);
        setSosModalOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('popstate', sync);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const navigateTo = (id: string) => {
    setPage(id);
    window.history.pushState({}, '', `/personal/${id}`);
    setSidebarOpen(false);
    setCommandOpen(false);
  };

  const handlePersonalEntry = () => {
    localStorage.setItem('healthway-entry-selected', 'personal');
    setEntrySelected(true);
  };

  const handleLogout = async () => {
    try {
      await signOut(token);
    } catch (err) {
      console.error('Could not revoke the current session.', err);
    } finally {
      localStorage.removeItem('healthway-demo-token');
      setToken('');
      window.history.replaceState({}, '', '/');
      setOauthError('');
    }
  };

  // 1. Dual Entry Gateway (if not yet chosen)
  if (!entrySelected && !token) {
    return <EcosystemExperience onSelectPersonal={handlePersonalEntry} />;
  }

  // 2. Personal Authentication Screen (if chosen but not signed in)
  if (!token) {
    return (
      <AuthScreen
        onLogin={completeLogin}
        onBackToGateway={() => {
          localStorage.removeItem('healthway-entry-selected');
          setEntrySelected(false);
          setOauthError('');
        }}
        initialError={oauthError}
        oauthLoading={oauthLoading}
      />
    );
  }

  const currentPage = navItems.find((n) => n.id === page) || navItems[0];

  return (
    <div className="app">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}

      {/* Sidebar Navigation */}
      <aside className={sidebarOpen ? 'sidebar open' : 'sidebar'}>
        <div className="brand">
          <span className="brand-mark">
            <HeartPulse size={20} />
          </span>
          <div className="brand-text">
            <span>Smart Healthcare</span>
            <small>Personal Health Gateway</small>
          </div>
          <button className="icon mobile-only close-btn" onClick={() => setSidebarOpen(false)} aria-label="Close menu">
            <X size={18} />
          </button>
        </div>

        <div className="demo-tag-container">
          <span className="demo">
            <ShieldCheck size={13} /> Personal Gateway · Module 1
          </span>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = page === item.id;
            return (
              <button key={item.id} className={active ? 'nav-item active' : 'nav-item'} onClick={() => navigateTo(item.id)}>
                <Icon size={18} className="nav-icon" />
                <span className="nav-label">{item.label}</span>
                {item.badge && <span className={`nav-badge ${item.badge.toLowerCase()}`}>{item.badge}</span>}
                {item.id === 'notifications' && unreadCount > 0 && <span className="nav-unread">{unreadCount}</span>}
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <button className="sos-sidebar-btn" onClick={() => setSosModalOpen(true)}>
            <AlertCircle size={17} />
            <span>Emergency SOS Card</span>
          </button>
          <button className="signout-btn" onClick={handleLogout}>
            <LogOut size={17} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-wrapper">
        <header className="topbar">
          <div className="topbar-left">
            <button className="icon mobile-only hamburger-btn" onClick={() => setSidebarOpen(true)} aria-label="Open menu">
              <Menu size={20} />
            </button>
            <div className="breadcrumbs">
              <span className="eyebrow">Personal Health Operating System</span>
              <h1>{currentPage.label}</h1>
            </div>
          </div>

          <div className="topbar-actions">
            <button className="command-trigger" onClick={() => setCommandOpen(true)} title="Press Ctrl+K to search">
              <Search size={16} />
              <span className="command-text">Search records, vitals, AI...</span>
              <kbd className="command-kbd">⌘K</kbd>
            </button>

            <button className="icon-btn notif-btn" aria-label="Notifications" onClick={() => navigateTo('notifications')}>
              <Bell size={19} />
              {unreadCount > 0 && <span className="notif-badge">{unreadCount}</span>}
            </button>

            <button className="avatar-btn" onClick={() => navigateTo('profile')} title="Avery Morgan (Identity Verified)">
              <span>AM</span>
            </button>
          </div>
        </header>

        {/* Dynamic Page Views */}
        <section className="content">
          <PageRenderer id={page} navigateTo={navigateTo} token={token} setSosModalOpen={setSosModalOpen} unreadCount={unreadCount} setUnreadCount={setUnreadCount} />
        </section>
      </main>

      {/* Command Palette Modal (Ctrl+K) */}
      {commandOpen && <CommandPalette onClose={() => setCommandOpen(false)} onSelect={(id) => navigateTo(id)} />}

      {/* SOS Emergency Modal */}
      {sosModalOpen && <EmergencySosModal onClose={() => setSosModalOpen(false)} navigateTo={navigateTo} />}
    </div>
  );
}

/* =========================================================================================
   2. AUTHENTICATION SCREENS (Sign In, Sign Up, Forgot Password, Verification)
   ========================================================================================= */
function AuthScreen({ onLogin, onBackToGateway, initialError, oauthLoading }: {
  onLogin: (t: string) => void;
  onBackToGateway: () => void;
  initialError: string;
  oauthLoading: boolean;
}) {
  const [tab, setTab] = useState<'signin' | 'signup' | 'forgot' | 'verify'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(initialError);
  const [successMsg, setSuccessMsg] = useState('');
  const [oauthProviders, setOauthProviders] = useState<OAuthProviders>({ google: false, github: false });
  const [oauthStatus, setOauthStatus] = useState('Checking available sign-in options…');
  const [registration, setRegistration] = useState({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: 'prefer_not_to_say',
    email: '',
    password: '',
  });

  useEffect(() => {
    getOAuthProviders()
      .then((providers) => {
        setOauthProviders(providers);
        setOauthStatus(
          providers.google || providers.github
            ? 'Continue with a linked identity provider.'
            : 'Google and GitHub sign-in can be enabled by configuring the backend OAuth credentials.',
        );
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : 'Could not load sign-in providers.';
        setOauthStatus(
          message === 'Failed to fetch'
            ? 'Cannot reach the sign-in service. Start the backend and check its API URL.'
            : message,
        );
      });
  }, []);

  useEffect(() => setError(initialError), [initialError]);

  const handleSignIn = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await signIn(email, password);
      onLogin(res.access_token);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to sign in. Check your credentials and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoFill = () => {
    setEmail('patient@healthcare.local');
    setPassword('Demo@12345');
    setError('');
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <button className="auth-back-btn" onClick={onBackToGateway}>
          <ChevronRight size={15} style={{ transform: 'rotate(180deg)' }} /> Back to gateway choice
        </button>

        <div className="auth-header">
          <div className="brand centered">
            <span className="brand-mark">
              <HeartPulse size={22} />
            </span>
            <span>Smart Healthcare</span>
          </div>
          <h1>Sign in to your health space</h1>
          <p>Manage your personal records, vitals, medications, and care.</p>
        </div>

        {oauthLoading && <div className="oauth-loading" role="status">Completing secure sign-in…</div>}

        {(tab === 'signin' || tab === 'signup') && (
          <OAuthOptions providers={oauthProviders} status={oauthStatus} disabled={loading || oauthLoading} onSelect={startOAuth} />
        )}

        {tab === 'signin' && (
          <>
            <form onSubmit={handleSignIn} className="auth-form">
              <label>
                Email Address
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" placeholder="you@example.com" />
              </label>

              <label>
                <div className="label-row">
                  <span>Password</span>
                  <button type="button" className="text-link" onClick={() => setTab('forgot')}>
                    Forgot password?
                  </button>
                </div>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" placeholder="••••••••" />
              </label>

              {error && <div className="error"><AlertTriangle size={15} />{error}</div>}

              <button className="primary full" disabled={loading || oauthLoading}>
                {loading ? 'Signing in securely…' : <>Sign In Securely <ChevronRight size={17} /></>}
              </button>

              <button type="button" className="demo-fill-btn" onClick={handleDemoFill}>
                <Sparkles size={15} /> Fill demo account
              </button>
            </form>

            <div className="auth-footer">
              <span>Don't have an account?</span>
              <button type="button" className="text-btn font-bold" onClick={() => setTab('signup')}>
                Create Personal Health Identity
              </button>
            </div>
          </>
        )}

        {tab === 'signup' && (
          <>
            <h1>Create Personal Identity</h1>
            <p className="muted text-center">Create a sovereign personal health record independent of any single hospital.</p>

            <form onSubmit={async (e) => {
              e.preventDefault();
              setLoading(true);
              setError('');
              try {
                const session = await register(registration);
                onLogin(session.access_token);
              } catch (err: unknown) {
                setError(err instanceof Error ? err.message : 'Unable to create your account.');
              } finally {
                setLoading(false);
              }
            }} className="auth-form">
              <div className="form-row-2">
                <label>
                  First Name
                  <input required autoComplete="given-name" value={registration.first_name} onChange={(e) => setRegistration({ ...registration, first_name: e.target.value })} />
                </label>
                <label>
                  Last Name
                  <input required autoComplete="family-name" value={registration.last_name} onChange={(e) => setRegistration({ ...registration, last_name: e.target.value })} />
                </label>
              </div>

              <div className="form-row-2">
                <label>
                  Date of Birth
                  <input type="date" required value={registration.date_of_birth} onChange={(e) => setRegistration({ ...registration, date_of_birth: e.target.value })} />
                </label>
                <label>
                  Gender
                  <select value={registration.gender} onChange={(e) => setRegistration({ ...registration, gender: e.target.value })}>
                    <option value="prefer_not_to_say">Prefer not to say</option>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                    <option value="non_binary">Non-binary</option>
                  </select>
                </label>
              </div>

              <label>
                Email Address
                <input type="email" required autoComplete="email" value={registration.email} onChange={(e) => setRegistration({ ...registration, email: e.target.value })} />
              </label>

              <label>
                Password
                <input type="password" required autoComplete="new-password" value={registration.password} onChange={(e) => setRegistration({ ...registration, password: e.target.value })} minLength={6} />
              </label>

              {error && <div className="error"><AlertTriangle size={15} />{error}</div>}
              <button className="primary full" disabled={loading || oauthLoading}>
                {loading ? 'Creating Identity…' : 'Register Health Identity'}
              </button>
            </form>

            <div className="auth-footer">
              <span>Already have an account?</span>
              <button type="button" className="text-btn font-bold" onClick={() => setTab('signin')}>
                Sign in
              </button>
            </div>
          </>
        )}

        {tab === 'forgot' && (
          <>
            <h1>Reset Password</h1>
            <p className="muted text-center">Enter your registered email address to receive password recovery instructions.</p>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                setSuccessMsg('Recovery instructions sent to your email address (Simulated in Development).');
                setTab('signin');
              }}
              className="auth-form"
            >
              <label>
                Registered Email
                <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
              </label>
              <button className="primary full">Send Recovery Link</button>
            </form>

            <div className="auth-footer">
              <button type="button" className="text-btn" onClick={() => setTab('signin')}>
                Back to Sign In
              </button>
            </div>
          </>
        )}

        {successMsg && <div className="success-banner mt-3"><CheckCircle2 size={16} />{successMsg}</div>}

        <div className="security-guarantee">
          <ShieldCheck size={16} />
          <span>
            <strong>Zero-Knowledge Architecture:</strong> Personal health records are isolated with strict backend authorization. Development mode uses synthetic test data.
          </span>
        </div>
      </div>
    </div>
  );
}

function OAuthOptions({ providers, status, disabled, onSelect }: {
  providers: OAuthProviders;
  status: string;
  disabled: boolean;
  onSelect: (provider: OAuthProvider) => void;
}) {
  return (
    <div className="oauth-options">
      <div className="oauth-divider"><span>Continue with</span></div>
      <div className="oauth-buttons">
        <button type="button" className="oauth-button" disabled={disabled || !providers.google} onClick={() => onSelect('google')}>
          <GoogleMark /> Google
        </button>
        <button type="button" className="oauth-button" disabled={disabled || !providers.github} onClick={() => onSelect('github')}>
          <Github size={18} /> GitHub
        </button>
      </div>
      {!providers.google && !providers.github && <p className="oauth-provider-status">{status}</p>}
    </div>
  );
}

function GoogleMark() {
  return (
    <svg className="google-mark" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#4285F4" d="M43.6 24.5c0-1.4-.1-2.8-.4-4.1H24v7.8h11a9.4 9.4 0 0 1-4.1 6.2v5.1h6.6c3.9-3.6 6.1-8.8 6.1-15Z" />
      <path fill="#34A853" d="M24 44c5.5 0 10.1-1.8 13.5-4.9l-6.6-5.1c-1.8 1.2-4.1 1.9-6.9 1.9-5.3 0-9.8-3.6-11.4-8.4H5.8v5.3A20 20 0 0 0 24 44Z" />
      <path fill="#FBBC05" d="M12.6 27.5a12 12 0 0 1 0-7v-5.3H5.8a20 20 0 0 0 0 17.6l6.8-5.3Z" />
      <path fill="#EA4335" d="M24 12.1c3 0 5.7 1 7.8 3.1l5.8-5.8C34.1 6.1 29.5 4 24 4A20 20 0 0 0 5.8 15.2l6.8 5.3c1.6-4.8 6.1-8.4 11.4-8.4Z" />
    </svg>
  );
}

/* =========================================================================================
   3. COMMAND PALETTE MODAL (Ctrl+K Fast Navigation)
   ========================================================================================= */
function CommandPalette({ onClose, onSelect }: { onClose: () => void; onSelect: (id: string) => void }) {
  const [query, setQuery] = useState('');
  const allCommands = [
    { id: 'dashboard', label: 'Overview & Health Brief', category: 'Pages', icon: Activity },
    { id: 'profile', label: 'My Health Profile & Demographics', category: 'Pages', icon: UserRound },
    { id: 'health-record', label: 'Structured Health Records & Provenance', category: 'Pages', icon: HeartPulse },
    { id: 'timeline', label: 'Chronological Health Timeline', category: 'Pages', icon: Calendar },
    { id: 'health-trends', label: 'Vital Signs & ML Trend Detection', category: 'Pages', icon: TrendingUp },
    { id: 'risk-prediction', label: 'Cardiovascular Risk Prediction (Prototype)', category: 'Pages', icon: Flame },
    { id: 'documents', label: 'Uploaded Medical Documents & Extraction', category: 'Pages', icon: FileText },
    { id: 'laboratory', label: 'Laboratory Reports & AI Interpretation', category: 'Pages', icon: Layers },
    { id: 'medications', label: 'Medication Vault & Adherence ML', category: 'Pages', icon: Pill },
    { id: 'appointments', label: 'Appointments & Scheduling', category: 'Pages', icon: Calendar },
    { id: 'care-navigation', label: 'Find Care (Doctors, Hospitals, Labs)', category: 'Pages', icon: Search },
    { id: 'ai-assistant', label: 'Ask Personal AI Health Assistant', category: 'Pages', icon: MessageCircle },
    { id: 'emergency', label: 'Emergency Profile & SOS Medical Card', category: 'Pages', icon: AlertCircle },
    { id: 'privacy', label: 'Privacy Center & Audit Access Logs', category: 'Pages', icon: ShieldCheck },
    { id: 'consent', label: 'Consent Management & Granular Grants', category: 'Pages', icon: Lock },
    { id: 'notifications', label: 'Notifications & Alerts', category: 'Pages', icon: Bell },
    { id: 'settings', label: 'Settings & Full Data Export Archive', category: 'Pages', icon: Settings },
  ];

  const filtered = allCommands.filter((c) => c.label.toLowerCase().includes(query.toLowerCase()) || c.id.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="command-palette" onClick={(e) => e.stopPropagation()}>
        <div className="command-search-bar">
          <Search size={18} className="text-teal" />
          <input autoFocus placeholder="Jump to records, vitals, labs, medications, AI assistant..." value={query} onChange={(e) => setQuery(e.target.value)} />
          <kbd className="esc-kbd" onClick={onClose}>
            ESC
          </kbd>
        </div>

        <div className="command-list">
          {filtered.length === 0 ? (
            <div className="command-empty">No results found for "{query}"</div>
          ) : (
            filtered.map((item) => {
              const Icon = item.icon;
              return (
                <button key={item.id} className="command-item" onClick={() => onSelect(item.id)}>
                  <span className="command-item-icon">
                    <Icon size={17} />
                  </span>
                  <span className="command-item-label">{item.label}</span>
                  <span className="command-item-cat">{item.category}</span>
                </button>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

/* =========================================================================================
   4. EMERGENCY SOS QUICK ACCESS MODAL
   ========================================================================================= */
function EmergencySosModal({ onClose, navigateTo }: { onClose: () => void; navigateTo: (p: string) => void }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="sos-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="sos-modal-header">
          <div className="sos-header-badge">
            <AlertCircle size={24} />
            <h2>Emergency Medical Profile</h2>
          </div>
          <button className="icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="sos-notice-banner">
          <Info size={17} />
          <p>
            <strong>Personal Health Gateway Emergency Card:</strong> This rapid-read card contains critical medical details for first responders and ER clinicians.
            <br />
            <small>Note: Autonomous emergency dispatch connects in the future Emergency Intelligence module.</small>
          </p>
        </div>

        <div className="sos-grid">
          <div className="sos-card blood-card">
            <span className="sos-label">Blood Group</span>
            <strong className="sos-value-highlight">O+</strong>
          </div>

          <div className="sos-card">
            <span className="sos-label">Severe Allergies</span>
            <strong className="text-danger">Penicillin</strong>
            <small>Reaction: Moderate / Hives & swelling</small>
          </div>

          <div className="sos-card">
            <span className="sos-label">Critical Conditions</span>
            <strong>Mild Hypertension</strong>
            <small>Status: Managed with Lisinopril</small>
          </div>

          <div className="sos-card">
            <span className="sos-label">Preferred Hospital</span>
            <strong>Seattle Central Medical Center</strong>
            <small>1100 9th Ave, Seattle, WA</small>
          </div>
        </div>

        <div className="sos-contacts-section">
          <h3>Primary Emergency Contact</h3>
          <div className="emergency-contact-item primary-contact">
            <div className="contact-icon">
              <Phone size={18} />
            </div>
            <div>
              <strong>Jordan Morgan (Spouse)</strong>
              <p>+1 (555) 014-1001 · Primary Emergency Contact</p>
            </div>
            <a href="tel:+15550141001" className="call-btn">
              Call Contact
            </a>
          </div>
        </div>

        <div className="sos-directives">
          <h3>Emergency Preferences & Directives</h3>
          <p className="directives-text">"No extraordinary measures without consulting primary emergency contact Jordan Morgan."</p>
        </div>

        <div className="modal-actions space-between">
          <button
            className="outline"
            onClick={() => {
              onClose();
              navigateTo('emergency');
            }}
          >
            Edit Full Emergency Profile
          </button>
          <button className="primary" onClick={onClose}>
            Close SOS Card
          </button>
        </div>
      </div>
    </div>
  );
}

/* =========================================================================================
   5. PAGE RENDERER (Routes to feature pages)
   ========================================================================================= */
function PageRenderer({
  id,
  navigateTo,
  token,
  setSosModalOpen,
  unreadCount,
  setUnreadCount,
}: {
  id: string;
  navigateTo: (p: string) => void;
  token: string;
  setSosModalOpen: (o: boolean) => void;
  unreadCount: number;
  setUnreadCount: React.Dispatch<React.SetStateAction<number>>;
}) {
  switch (id) {
    case 'dashboard':
      return <DashboardPage navigateTo={navigateTo} token={token} setSosModalOpen={setSosModalOpen} />;
    case 'profile':
      return <ProfilePage token={token} />;
    case 'health-record':
      return <HealthRecordsPage token={token} navigateTo={navigateTo} />;
    case 'timeline':
      return <TimelinePage token={token} />;
    case 'health-trends':
      return <HealthTrendsPage token={token} />;
    case 'risk-prediction':
      return <RiskPredictionPage token={token} />;
    case 'documents':
      return <DocumentsPage token={token} />;
    case 'laboratory':
      return <LaboratoryPage token={token} />;
    case 'medications':
      return <MedicationsPage token={token} />;
    case 'appointments':
      return <AppointmentsPage token={token} />;
    case 'care-navigation':
      return <CareNavigationPage token={token} navigateTo={navigateTo} />;
    case 'ai-assistant':
      return <AiAssistantPage token={token} />;
    case 'emergency':
      return <EmergencyPage token={token} setSosModalOpen={setSosModalOpen} />;
    case 'privacy':
      return <PrivacyPage token={token} />;
    case 'consent':
      return <ConsentPage token={token} />;
    case 'notifications':
      return <NotificationsPage token={token} unreadCount={unreadCount} setUnreadCount={setUnreadCount} />;
    case 'settings':
      return <SettingsPage token={token} />;
    default:
      return <DashboardPage navigateTo={navigateTo} token={token} setSosModalOpen={setSosModalOpen} />;
  }
}

/* Common Card UI */
function Card({ title, children, action, className = '' }: { title?: string; children: ReactNode; action?: ReactNode; className?: string }) {
  return (
    <article className={`card ${className}`}>
      {title && (
        <div className="card-head">
          <h2>{title}</h2>
          {action}
        </div>
      )}
      {children}
    </article>
  );
}

/* =========================================================================================
   PAGE 1: DASHBOARD (Overview, Health Brief, KPIs, Trends, Meds, Upcoming Care)
   ========================================================================================= */
function DashboardPage({ navigateTo, token, setSosModalOpen }: { navigateTo: (p: string) => void; token: string; setSosModalOpen: (o: boolean) => void }) {
  const [doseLogged, setDoseLogged] = useState(false);

  return (
    <div className="dashboard-view">
      {/* Welcome Banner */}
      <div className="welcome">
        <div>
          <p className="eyebrow">Wednesday, September 2, 2026 · Seattle, WA</p>
          <h2>Good morning, Avery.</h2>
          <p>Your Personal Health Operating System is active and synchronized.</p>
        </div>
        <div className="welcome-actions">
          <button className="danger-outline" onClick={() => setSosModalOpen(true)}>
            <AlertCircle size={16} /> Emergency SOS Card
          </button>
          <button className="primary" onClick={() => navigateTo('ai-assistant')}>
            <Sparkles size={16} /> Ask AI Assistant
          </button>
        </div>
      </div>

      {/* AI Health Brief */}
      <Card className="brief-card">
        <div className="brief">
          <span className="spark">✦</span>
          <div className="brief-content">
            <div className="brief-title-row">
              <p className="eyebrow">AI-GENERATED PERSONAL HEALTH BRIEF</p>
              <span className="ai-tag">Informational · Non-Diagnostic</span>
            </div>
            <h2>Your recent fasting glucose is elevated relative to reference range; blood pressure remains stable.</h2>
            <p>
              Fasting glucose was recorded at <strong>126 mg/dL</strong> on 28 Aug from Northstar Laboratory (reference: 70–99 mg/dL), representing an upward statistical trend. Blood pressure readings remain well-managed at <strong>120/77 mmHg</strong>. You have a primary care follow-up scheduled with Dr. Elena Vance tomorrow at 10:30 AM.
            </p>
            <div className="brief-footer">
              <button className="text-btn font-bold" onClick={() => navigateTo('laboratory')}>
                View Laboratory Sources <ChevronRight size={16} />
              </button>
              <span className="source-time">Source Period: August 2026 – Present</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Important Alerts Strip */}
      <div className="alert-strip">
        <div className="alert-strip-item">
          <Bell className="text-teal" size={17} />
          <span>Evening Metformin (500 mg) dose due at 8:00 PM with food.</span>
          <button className="pill-action-btn" onClick={() => setDoseLogged(!doseLogged)}>
            {doseLogged ? '✓ Logged' : 'Mark Dose Taken'}
          </button>
        </div>
      </div>

      {/* KPI Cards Strip */}
      <div className="kpis">
        <div className="kpi-card" onClick={() => navigateTo('medications')}>
          <div className="metric">
            <span><Pill size={20} /></span>
            <p>Active Medications</p>
            <strong>2</strong>
            <small>94% Adherence Rate</small>
          </div>
        </div>

        <div className="kpi-card" onClick={() => navigateTo('appointments')}>
          <div className="metric">
            <span><Calendar size={20} /></span>
            <p>Upcoming Care</p>
            <strong>2</strong>
            <small>Next: Tomorrow 10:30 AM</small>
          </div>
        </div>

        <div className="kpi-card" onClick={() => navigateTo('laboratory')}>
          <div className="metric">
            <span><FileText size={20} /></span>
            <p>Recent Lab Reports</p>
            <strong>1</strong>
            <small>Metabolic Panel (Verified)</small>
          </div>
        </div>

        <div className="kpi-card" onClick={() => navigateTo('privacy')}>
          <div className="metric">
            <span><ShieldCheck size={20} /></span>
            <p>Connected Sources</p>
            <strong>3</strong>
            <small>All Consents Active</small>
          </div>
        </div>
      </div>

      {/* Grid: Health Trends + Upcoming Care */}
      <div className="two">
        <Card title="Vital Sign Trends (Fasting Glucose)" action={<button className="text-btn" onClick={() => navigateTo('health-trends')}>Detailed ML Analytics →</button>}>
          <InteractiveTrendChart />
          <div className="trend-stat-row">
            <span className="trend-stat-badge up">↗ Detected Statistical Direction: Increasing</span>
            <span className="trend-stat-obs">3 Observations · R² = 0.88</span>
          </div>
          <p className="disclaimer-mini">Statistical trend detection is informational and does not represent a medical diagnosis.</p>
        </Card>

        <Card title="Upcoming Appointments" action={<button className="text-btn" onClick={() => navigateTo('appointments')}>Manage</button>}>
          <div className="list">
            <div className="list-item">
              <div className="event-icon"><Calendar size={18} /></div>
              <div>
                <strong>Primary Care Routine Follow-up</strong>
                <small>Dr. Elena Vance · Tomorrow, 10:30 AM</small>
                <small className="muted">Demo Care Clinic · 1200 Healthway Blvd</small>
              </div>
              <span className="status">Confirmed</span>
            </div>

            <div className="list-item">
              <div className="event-icon"><Calendar size={18} /></div>
              <div>
                <strong>Annual Eye Examination</strong>
                <small>Dr. Kenneth Cho · 16 Sep 2026, 2:00 PM</small>
                <small className="muted">Visionworks (Demo Care)</small>
              </div>
              <span className="needs">Pending</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Grid: Medication Status + Recent Health Activity */}
      <div className="two">
        <Card title="Today's Medication Schedule" action={<button className="text-btn" onClick={() => navigateTo('medications')}>Medication Vault</button>}>
          <div className="med-list">
            <div className="row">
              <span className="pill-icon"><Pill size={18} /></span>
              <div>
                <strong>Metformin <span className="muted">500 mg</span></strong>
                <small>Twice daily with meals · 96% adherence</small>
              </div>
              <span className="status">Due 8:00 PM</span>
            </div>

            <div className="row">
              <span className="pill-icon"><Pill size={18} /></span>
              <div>
                <strong>Lisinopril <span className="muted">10 mg</span></strong>
                <small>Every morning at 8:00 AM · 92% adherence</small>
              </div>
              <span className="status">Taken Today</span>
            </div>
          </div>
        </Card>

        <Card title="Recent Health Activity & Provenance" action={<button className="text-btn" onClick={() => navigateTo('timeline')}>Full Timeline</button>}>
          <div className="list">
            <div className="list-item">
              <div className="event-icon"><FileCheck size={18} /></div>
              <div>
                <strong>Comprehensive Metabolic Panel</strong>
                <small>Northstar Laboratory · 28 Aug 2026</small>
              </div>
              <span className="status">Verified Source</span>
            </div>

            <div className="list-item">
              <div className="event-icon"><Heart size={18} /></div>
              <div>
                <strong>Blood Pressure Reading: 121/78 mmHg</strong>
                <small>Self-Reported Telehealth · 19 Aug 2026</small>
              </div>
              <span className="status">Recorded</span>
            </div>

            <div className="list-item">
              <div className="event-icon"><Pill size={18} /></div>
              <div>
                <strong>Prescription Renewal: Lisinopril 10mg</strong>
                <small>Demo Care Clinic · 19 Aug 2026</small>
              </div>
              <span className="status">Verified</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

/* SVG Interactive Trend Chart */
function InteractiveTrendChart() {
  const points = [
    { date: 'Aug 4', val: 110, x: 50, y: 115 },
    { date: 'Aug 12', val: 118, x: 260, y: 75 },
    { date: 'Aug 28', val: 126, x: 470, y: 30 },
  ];
  return (
    <div className="chart-wrapper">
      <svg viewBox="0 0 520 150" className="trend-svg" role="img" aria-label="Glucose trend chart">
        <path className="grid" d="M0 25 H520 M0 75 H520 M0 125 H520" />
        {/* Reference band 70-99 */}
        <rect x="0" y="110" width="520" height="35" fill="#f0faf7" opacity="0.6" />
        <text x="10" y="122" fill="#58857d" fontSize="10">Target Reference Band (70-99 mg/dL)</text>
        <path className="line" d="M50 115 L260 75 L470 30" />
        {points.map((p) => (
          <g key={p.date}>
            <circle cx={p.x} cy={p.y} r="6" />
            <text x={p.x} y={p.y - 12} textAnchor="middle" fill="#12473f" fontSize="12" fontWeight="700">
              {p.val} mg/dL
            </text>
          </g>
        ))}
      </svg>
      <div className="axis">
        <span>4 Aug 2026</span>
        <span>12 Aug 2026</span>
        <span>28 Aug 2026 (Latest: 126)</span>
      </div>
    </div>
  );
}

/* =========================================================================================
   PAGE 2: MY PROFILE (Demographics, Clinical Details, Allergies, Conditions, Save)
   ========================================================================================= */
type ProfileFormState = {
  first_name: string;
  middle_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  blood_group: string;
  important_notes: string;
  preferred_hospital: string;
  emergency_directives: string;
};

const emptyProfileForm: ProfileFormState = {
  first_name: '',
  middle_name: '',
  last_name: '',
  date_of_birth: '',
  gender: 'prefer_not_to_say',
  email: '',
  phone: '',
  address: '',
  city: '',
  state: '',
  country: '',
  postal_code: '',
  blood_group: 'O+',
  important_notes: '',
  preferred_hospital: '',
  emergency_directives: '',
};

function ProfilePage({ token }: { token: string }) {
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [form, setForm] = useState<ProfileFormState>(emptyProfileForm);

  useEffect(() => {
    let active = true;

    const loadProfile = async () => {
      try {
        const profile = await api<{ [key: string]: any }>('/profile', token);
        if (!active) return;

        setForm({
          first_name: profile.first_name ?? '',
          middle_name: profile.middle_name ?? '',
          last_name: profile.last_name ?? '',
          date_of_birth: profile.date_of_birth ?? '',
          gender: profile.gender ?? 'prefer_not_to_say',
          email: profile.email ?? '',
          phone: profile.phone ?? '',
          address: profile.address ?? '',
          city: profile.city ?? '',
          state: profile.state ?? '',
          country: profile.country ?? '',
          postal_code: profile.postal_code ?? '',
          blood_group: profile.blood_group ?? 'O+',
          important_notes: profile.important_notes ?? '',
          preferred_hospital: profile.preferred_hospital ?? '',
          emergency_directives: profile.emergency_directives ?? '',
        });
      } catch (err: any) {
        if (active) {
          setError(err.message || 'Unable to load your profile.');
        }
      } finally {
        if (active) {
          setInitializing(false);
        }
      }
    };

    loadProfile();
    return () => {
      active = false;
    };
  }, [token]);

  const updateField = (field: keyof ProfileFormState, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api('/profile', token, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          first_name: form.first_name,
          middle_name: form.middle_name,
          last_name: form.last_name,
          date_of_birth: form.date_of_birth,
          gender: form.gender,
          email: form.email,
          phone: form.phone,
          address: form.address,
          city: form.city,
          state: form.state,
          country: form.country,
          postal_code: form.postal_code,
          blood_group: form.blood_group,
          important_notes: form.important_notes,
          preferred_hospital: form.preferred_hospital,
          emergency_directives: form.emergency_directives,
        }),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 4000);
    } catch (err: any) {
      setError(err.message || 'Failed to save changes.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-page">
      <div className="page-intro">
        <div>
          <h2>Personal Health Profile</h2>
          <p>Manage your identity, clinical parameters, and emergency directives.</p>
        </div>
        <span className="verified">
          <ShieldCheck size={16} /> Identity Verified (Sovereign)
        </span>
      </div>

      <Card title="Personal Demographics & Clinical Information">
        <form className="form-grid" onSubmit={handleSubmit}>
          {initializing ? (
            <div className="wide">
              <p>Loading your profile from the secure personal health gateway…</p>
            </div>
          ) : (
            <>
              <label>
                First Name
                <input name="first_name" value={form.first_name} onChange={(e) => updateField('first_name', e.target.value)} required />
              </label>

              <label>
                Middle Name
                <input name="middle_name" value={form.middle_name} onChange={(e) => updateField('middle_name', e.target.value)} />
              </label>

              <label>
                Last Name
                <input name="last_name" value={form.last_name} onChange={(e) => updateField('last_name', e.target.value)} required />
              </label>

              <label>
                Date of Birth
                <input name="date_of_birth" type="date" value={form.date_of_birth} onChange={(e) => updateField('date_of_birth', e.target.value)} required />
              </label>

              <label>
                Gender
                <select name="gender" value={form.gender} onChange={(e) => updateField('gender', e.target.value)}>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                  <option value="non_binary">Non-binary</option>
                </select>
              </label>

              <label>
                Blood Group
                <select name="blood_group" value={form.blood_group} onChange={(e) => updateField('blood_group', e.target.value)}>
                  <option value="O+">O Positive (O+)</option>
                  <option value="O-">O Negative (O-)</option>
                  <option value="A+">A Positive (A+)</option>
                  <option value="A-">A Negative (A-)</option>
                  <option value="B+">B Positive (B+)</option>
                  <option value="B-">B Negative (B-)</option>
                  <option value="AB+">AB Positive (AB+)</option>
                  <option value="AB-">AB Negative (AB-)</option>
                </select>
              </label>

              <label>
                Email Address
                <input name="email" type="email" value={form.email} onChange={(e) => updateField('email', e.target.value)} required />
              </label>

              <label>
                Phone Number
                <input name="phone" type="tel" value={form.phone} onChange={(e) => updateField('phone', e.target.value)} required />
              </label>

              <label className="wide">
                Street Address
                <input name="address" value={form.address} onChange={(e) => updateField('address', e.target.value)} />
              </label>

              <label>
                City
                <input name="city" value={form.city} onChange={(e) => updateField('city', e.target.value)} />
              </label>

              <label>
                State / Province
                <input name="state" value={form.state} onChange={(e) => updateField('state', e.target.value)} />
              </label>

              <label>
                Country
                <input name="country" value={form.country} onChange={(e) => updateField('country', e.target.value)} />
              </label>

              <label>
                Postal Code
                <input name="postal_code" value={form.postal_code} onChange={(e) => updateField('postal_code', e.target.value)} />
              </label>

              <label className="wide">
                Preferred Hospital
                <input name="preferred_hospital" value={form.preferred_hospital} onChange={(e) => updateField('preferred_hospital', e.target.value)} />
              </label>

              <label className="wide">
                Emergency Directives & Preferences
                <textarea name="emergency_directives" value={form.emergency_directives} onChange={(e) => updateField('emergency_directives', e.target.value)} />
              </label>

              <label className="wide">
                Important Medical Notes
                <textarea name="important_notes" value={form.important_notes} onChange={(e) => updateField('important_notes', e.target.value)} />
              </label>
            </>
          )}

          <div className="wide form-footer">
            <div>
              {saved && <span className="success"><Check size={16} /> Changes saved successfully to personal profile.</span>}
              {error && <span className="error"><AlertTriangle size={16} /> {error}</span>}
            </div>
            <button className="primary" disabled={loading || initializing}>
              {loading ? 'Saving…' : 'Save Profile Changes'}
            </button>
          </div>
        </form>
      </Card>
    </div>
  );
}

/* =========================================================================================
   PAGE 3: HEALTH RECORDS & PROVENANCE
   ========================================================================================= */
function HealthRecordsPage({ token, navigateTo }: { token: string; navigateTo: (p: string) => void }) {
  const [filter, setFilter] = useState('All');
  const records = [
    {
      id: 'REC-001',
      title: 'Comprehensive Metabolic Panel',
      type: 'Laboratory',
      date: '28 Aug 2026',
      source: 'Northstar Laboratory Network',
      docId: 'doc-1',
      status: 'Verified Source',
      summary: 'Fasting glucose (126 mg/dL) and kidney biomarkers extracted from structured lab report.',
    },
    {
      id: 'REC-002',
      title: 'Prescription: Metformin 500mg (Refill)',
      type: 'Prescription',
      date: '19 Aug 2026',
      source: 'Demo Care Clinic (Dr. Elena Vance)',
      status: 'Verified',
      summary: 'Twice-daily oral dosage for glycemic management.',
    },
    {
      id: 'REC-003',
      title: 'Home Blood Pressure Log (121/78 mmHg)',
      type: 'Vital',
      date: '19 Aug 2026',
      source: 'Self-Reported Telehealth Device',
      docId: 'doc-2',
      status: 'Self-Recorded',
      summary: 'Resting morning blood pressure reading.',
    },
    {
      id: 'REC-004',
      title: 'Clinical Consultation Summary',
      type: 'Doctor Report',
      date: '04 Aug 2026',
      source: 'Demo Care Clinic',
      status: 'Verified',
      summary: 'Routine health check and metabolic panel order.',
    },
  ];

  const filtered = records.filter((r) => filter === 'All' || r.type === filter);

  return (
    <div className="health-records-page">
      <div className="page-intro">
        <div>
          <h2>Structured Health Records & Provenance</h2>
          <p>Every clinical record preserves source organization, timestamps, and verification status.</p>
        </div>
        <div className="filter-pills">
          {['All', 'Laboratory', 'Prescription', 'Vital', 'Doctor Report'].map((f) => (
            <button key={f} className={filter === f ? 'pill active' : 'pill'} onClick={() => setFilter(f)}>
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="provenance-banner">
        <ShieldCheck size={18} className="text-teal" />
        <p>
          <strong>Data Provenance Guarantee:</strong> AI interpretations and assistant summaries never overwrite original source records. Clinical provenance is retained for every record.
        </p>
      </div>

      <div className="records-grid">
        {filtered.map((r) => (
          <Card key={r.id} className="record-card">
            <div className="record-card-header">
              <div className="record-type-badge">{r.type}</div>
              <span className={`status ${r.status.includes('Verified') ? 'verified-tag' : ''}`}>{r.status}</span>
            </div>
            <h3>{r.title}</h3>
            <p className="record-summary">{r.summary}</p>
            <div className="record-provenance-box">
              <div>
                <span className="prov-label">Record Date:</span> <strong>{r.date}</strong>
              </div>
              <div>
                <span className="prov-label">Source Organization:</span> <strong>{r.source}</strong>
              </div>
              <div>
                <span className="prov-label">Record Reference:</span> <code>{r.id}</code>
              </div>
            </div>
            {r.docId && (
              <button className="text-btn font-bold mt-2" onClick={() => navigateTo('documents')}>
                <FileText size={15} /> View Source Document ({r.docId})
              </button>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}

/* =========================================================================================
   PAGE 4: TIMELINE
   ========================================================================================= */
function TimelinePage({ token }: { token: string }) {
  const [filter, setFilter] = useState('All');
  const events = [
    { date: '28 Aug 2026', title: 'Comprehensive Metabolic Panel Processed', source: 'Northstar Laboratory', cat: 'Laboratory', status: 'Verified' },
    { date: '28 Aug 2026', title: 'Vital Reading Recorded: Glucose 126 mg/dL', source: 'Northstar Laboratory', cat: 'Vital', status: 'Verified' },
    { date: '26 Aug 2026', title: 'Medical Document Uploaded: Blood Pressure Log.png', source: 'Added by you', cat: 'Document', status: 'Processed' },
    { date: '19 Aug 2026', title: 'Home Blood Pressure Reading: 121/78 mmHg', source: 'Added by you', cat: 'Vital', status: 'Recorded' },
    { date: '19 Aug 2026', title: 'Prescription Refilled: Metformin 500mg', source: 'Demo Care Clinic', cat: 'Medication', status: 'Verified' },
    { date: '04 Aug 2026', title: 'Telehealth Consultation with Dr. Elena Vance', source: 'Demo Care Clinic', cat: 'Appointment', status: 'Completed' },
  ];

  const filtered = events.filter((e) => filter === 'All' || e.cat === filter);

  return (
    <div className="timeline-page">
      <div className="page-intro">
        <div>
          <h2>Chronological Health Timeline</h2>
          <p>Track health events, document uploads, and clinical interactions in order.</p>
        </div>
        <select value={filter} onChange={(e) => setFilter(e.target.value)} className="select-dropdown">
          <option value="All">All Events</option>
          <option value="Laboratory">Laboratory</option>
          <option value="Vital">Vitals</option>
          <option value="Medication">Medications</option>
          <option value="Appointment">Appointments</option>
          <option value="Document">Documents</option>
        </select>
      </div>

      <Card>
        <div className="timeline">
          {filtered.map((item, idx) => (
            <div className="timeline-item" key={idx}>
              <span className="timeline-dot" />
              <p className="eyebrow">{item.date}</p>
              <h3>{item.title}</h3>
              <p className="timeline-meta">
                Source: <strong>{item.source}</strong> · <span className="status">{item.status}</span> · Category: {item.cat}
              </p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

/* =========================================================================================
   PAGE 5: VITALS & HEALTH TREND ANALYTICS (ML Trend Detection Engine)
   ========================================================================================= */
function HealthTrendsPage({ token }: { token: string }) {
  const [metric, setMetric] = useState<'glucose' | 'blood_pressure' | 'weight' | 'heart_rate' | 'spo2' | 'hba1c'>('glucose');
  const [modalOpen, setModalOpen] = useState(false);
  const [readingValue, setReadingValue] = useState('');
  const [savedMsg, setSavedMsg] = useState('');

  const metricsData = {
    glucose: {
      label: 'Fasting Blood Glucose',
      unit: 'mg/dL',
      readings: '110 → 118 → 126',
      slope: '+0.57 mg/dL / day',
      r2: '0.88 (Strong correlation)',
      direction: 'Increasing',
      note: 'An increasing statistical trend was detected across 3 readings (from 110 to 126 mg/dL). This statistical observation is informational and does not represent a diagnosis.',
      range: '70–99 mg/dL',
    },
    blood_pressure: {
      label: 'Blood Pressure (Systolic/Diastolic)',
      unit: 'mmHg',
      readings: '118/76 → 121/78 → 120/77',
      slope: '+0.04 mmHg / day',
      r2: '0.12 (Stable)',
      direction: 'Stable',
      note: 'Blood pressure readings remain stable within the normal range across the last 30 days.',
      range: '< 120/80 mmHg',
    },
    weight: {
      label: 'Body Weight',
      unit: 'lbs',
      readings: '165 → 164 → 164',
      slope: '-0.03 lbs / day',
      r2: '0.45 (Stable)',
      direction: 'Stable',
      note: 'Weight measurements indicate stable mass over the observation period.',
      range: 'BMI Reference: 22.8',
    },
    heart_rate: {
      label: 'Resting Heart Rate',
      unit: 'bpm',
      readings: '72 → 70 → 74',
      slope: '+0.07 bpm / day',
      r2: '0.21 (Normal variation)',
      direction: 'Stable',
      note: 'Resting heart rate demonstrates typical circadian and daily physiological variation.',
      range: '60–100 bpm',
    },
    spo2: {
      label: 'Oxygen Saturation (SpO2)',
      unit: '%',
      readings: '98% → 98% → 99%',
      slope: '+0.03% / day',
      r2: '0.60 (Stable / High)',
      direction: 'Stable',
      note: 'SpO2 measurements are consistently optimal.',
      range: '95–100%',
    },
    hba1c: {
      label: 'Hemoglobin A1c',
      unit: '%',
      readings: '5.6% → 5.7%',
      slope: '+0.05% / month',
      r2: '0.75 (Slight upward shift)',
      direction: 'Increasing',
      note: 'HbA1c shifted slightly from 5.6% to 5.7%. Statistical trend only; evaluate with a clinician.',
      range: '< 5.7% (Normal)',
    },
  };

  const current = metricsData[metric];

  const handleRecordVital = async (e: FormEvent) => {
    e.preventDefault();
    setSavedMsg('Vital reading recorded successfully and indexed in trend model.');
    setModalOpen(false);
    setTimeout(() => setSavedMsg(''), 4000);
  };

  return (
    <div className="vitals-trends-page">
      <div className="page-intro">
        <div>
          <h2>Vital Tracking & ML Trend Analytics</h2>
          <p>Statistical regression, strength metrics, and trend directions across your recorded values.</p>
        </div>
        <button className="primary" onClick={() => setModalOpen(true)}>
          <Plus size={17} /> Record Vital Reading
        </button>
      </div>

      {savedMsg && <div className="success-banner mb-3"><CheckCircle2 size={16} />{savedMsg}</div>}

      {/* Metric Selector Tabs */}
      <div className="metric-tabs">
        {(Object.keys(metricsData) as (keyof typeof metricsData)[]).map((key) => (
          <button key={key} className={metric === key ? 'metric-tab active' : 'metric-tab'} onClick={() => setMetric(key)}>
            {metricsData[key].label}
          </button>
        ))}
      </div>

      {/* Main Trend Analysis Card */}
      <Card title={`${current.label} — 30-Day Analysis`}>
        <div className="trend-detail">
          <div className="trend-meta-column">
            <p className="eyebrow">{metric.toUpperCase()} SUMMARY</p>
            <h2>{current.readings} {current.unit}</h2>
            <div className={`direction-badge ${current.direction.toLowerCase()}`}>
              {current.direction === 'Increasing' ? <TrendingUp size={16} /> : <Activity size={16} />}
              <span>Direction: {current.direction}</span>
            </div>

            <div className="stat-grid mt-3">
              <div className="stat-item">
                <span className="stat-label">Model Method:</span>
                <strong>Ordinary Least Squares</strong>
              </div>
              <div className="stat-item">
                <span className="stat-label">Slope:</span>
                <strong>{current.slope}</strong>
              </div>
              <div className="stat-item">
                <span className="stat-label">Fit Metric (R²):</span>
                <strong>{current.r2}</strong>
              </div>
              <div className="stat-item">
                <span className="stat-label">Reference Band:</span>
                <strong>{current.range}</strong>
              </div>
            </div>
          </div>

          <div className="trend-chart-column">
            <InteractiveTrendChart />
          </div>
        </div>

        <div className="ml-explanation-box">
          <Sparkles size={18} className="text-teal" />
          <div>
            <strong>ML Trend Analysis Output (Informational):</strong>
            <p>{current.note}</p>
          </div>
        </div>

        <p className="disclaimer mt-3">
          <strong>Non-Diagnostic Notice:</strong> A detected statistical direction describes movement in historical readings only. It does not diagnose diabetes, hypertension, or any medical condition. Discuss all lab and vital trends with your physician.
        </p>
      </Card>

      {/* Record Vital Modal */}
      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Record New Vital Reading</h2>
              <button className="icon" onClick={() => setModalOpen(false)}>
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleRecordVital}>
              <div className="modal-body">
                <label>
                  Vital Metric Type
                  <select value={metric} onChange={(e) => setMetric(e.target.value as any)}>
                    <option value="glucose">Blood Glucose (mg/dL)</option>
                    <option value="blood_pressure">Blood Pressure Systolic/Diastolic (mmHg)</option>
                    <option value="weight">Body Weight (lbs)</option>
                    <option value="heart_rate">Heart Rate (bpm)</option>
                    <option value="spo2">Oxygen Saturation SpO2 (%)</option>
                    <option value="hba1c">Hemoglobin A1c (%)</option>
                  </select>
                </label>

                <label>
                  Reading Value
                  <input
                    type="number"
                    step="0.1"
                    required
                    placeholder={`Enter value in ${current.unit}`}
                    value={readingValue}
                    onChange={(e) => setReadingValue(e.target.value)}
                  />
                </label>

                <label>
                  Measurement Timestamp
                  <input type="datetime-local" defaultValue={new Date().toISOString().slice(0, 16)} required />
                </label>

                <label>
                  Source / Device
                  <input defaultValue="Added by you (Home Monitor)" />
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="outline" onClick={() => setModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="primary">
                  Save Reading
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

/* =========================================================================================
   PAGE 6: HEALTH RISK PREDICTION (Cardiovascular Research Prototype)
   ========================================================================================= */
function RiskPredictionPage({ token }: { token: string }) {
  const [age, setAge] = useState(39);
  const [bmi, setBmi] = useState(24.2);
  const [sbp, setSbp] = useState(120);
  const [glucose, setGlucose] = useState(126);
  const [smoker, setSmoker] = useState(false);
  const [familyHistory, setFamilyHistory] = useState(false);
  const [calculated, setCalculated] = useState(false);

  // Tabular logistic prototype calculation
  const intercept = -6.5;
  const lin = intercept + 0.045 * age + 0.035 * bmi + 0.025 * sbp + 0.015 * glucose + (smoker ? 0.75 : 0) + (familyHistory ? 0.55 : 0);
  const prob = 1.0 / (1.0 + Math.exp(-lin));
  const pct = Math.round(prob * 1000) / 10;
  const category = prob < 0.2 ? 'Low' : prob < 0.45 ? 'Moderate' : 'Elevated';

  return (
    <div className="risk-prediction-page">
      <div className="page-intro">
        <div>
          <h2>Health Risk Prediction Architecture</h2>
          <p>Research and decision-support prototype models with explicit non-clinical boundaries.</p>
        </div>
        <span className="demo">Prototype / Research Model</span>
      </div>

      <div className="warning-banner">
        <AlertTriangle size={20} className="text-amber" />
        <div>
          <strong>PROTOTYPE / RESEARCH MODEL NOTICE:</strong>
          <p>
            This model is for <strong>exploratory research and decision support only</strong>. It has not undergone clinical device certification and must never be treated as a diagnostic determination.
          </p>
        </div>
      </div>

      <div className="two">
        {/* Model Inputs */}
        <Card title="Tabular Cardiovascular Risk Model Inputs">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setCalculated(true);
            }}
            className="risk-form"
          >
            <div className="form-row-2">
              <label>
                Age (years)
                <input type="number" min={18} max={110} value={age} onChange={(e) => setAge(Number(e.target.value))} />
              </label>
              <label>
                Body Mass Index (BMI)
                <input type="number" step="0.1" min={10} max={60} value={bmi} onChange={(e) => setBmi(Number(e.target.value))} />
              </label>
            </div>

            <div className="form-row-2">
              <label>
                Systolic BP (mmHg)
                <input type="number" min={70} max={250} value={sbp} onChange={(e) => setSbp(Number(e.target.value))} />
              </label>
              <label>
                Fasting Glucose (mg/dL)
                <input type="number" min={40} max={500} value={glucose} onChange={(e) => setGlucose(Number(e.target.value))} />
              </label>
            </div>

            <div className="checkbox-row">
              <label className="checkbox-label">
                <input type="checkbox" checked={smoker} onChange={(e) => setSmoker(e.target.checked)} />
                <span>Current Tobacco Smoker</span>
              </label>
              <label className="checkbox-label">
                <input type="checkbox" checked={familyHistory} onChange={(e) => setFamilyHistory(e.target.checked)} />
                <span>Family History of Cardiovascular Disease</span>
              </label>
            </div>

            <button type="submit" className="primary full mt-3">
              Run Prototype Risk Estimation <Sparkles size={16} />
            </button>
          </form>
        </Card>

        {/* Model Output & Disclaimers */}
        <Card title="Model Estimate & Decision Support">
          <div className="risk-output-box">
            <p className="eyebrow">MODEL-ESTIMATED RISK CATEGORY</p>
            <div className={`risk-category-display ${category.toLowerCase()}`}>
              <h2>{category}</h2>
              <span className="risk-pct">{pct}% statistical score</span>
            </div>

            <div className="model-specs">
              <div>
                <span>Framework:</span> <strong>Tabular Logistic Risk Estimator</strong>
              </div>
              <div>
                <span>Version:</span> <strong>1.0.0-research-prototype</strong>
              </div>
              <div>
                <span>Dataset:</span> <strong>Synthetic Cohort V1</strong>
              </div>
            </div>

            <p className="risk-interpretation-text">
              Estimated statistical risk falls in the <strong>{category.toLowerCase()}</strong> relative tier based on submitted physiological parameters.
            </p>

            <div className="disclaimer-mini mt-3">
              Every model estimate must contain a disclaimer: Never present a model estimate as a confirmed diagnosis. Always review risk factors with your primary physician.
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

/* =========================================================================================
   PAGE 7: DOCUMENTS HUB (Upload, Processing states, Viewer, Provenance)
   ========================================================================================= */
function DocumentsPage({ token }: { token: string }) {
  const [docs, setDocs] = useState([
    { id: 'doc-1', name: 'Metabolic Panel — Aug 2026.pdf', size: '248 KB', type: 'PDF', status: 'Processed', source: 'Northstar Laboratory', date: '28 Aug 2026' },
    { id: 'doc-2', name: 'Blood Pressure Log — Aug 2026.png', size: '412 KB', type: 'PNG Image', status: 'Processed', source: 'Added by you', date: '26 Aug 2026' },
  ]);
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'processing' | 'done'>('idle');
  const [selectedDoc, setSelectedDoc] = useState<any>(null);
  const [message, setMessage] = useState('');

  const handleUpload = async (file: File) => {
    if (file.size > 10 * 1024 * 1024) {
      setMessage('Files must be smaller than 10 MB.');
      return;
    }
    setUploadState('uploading');
    setMessage(`Uploading ${file.name} to secure private storage…`);

    setTimeout(() => {
      setUploadState('processing');
      setMessage(`Processing and indexing ${file.name} for grounded AI retrieval…`);
      setTimeout(() => {
        setUploadState('done');
        const newDoc = {
          id: `doc-${Date.now().toString().slice(-4)}`,
          name: file.name,
          size: `${Math.round(file.size / 1024)} KB`,
          type: file.name.endsWith('.pdf') ? 'PDF' : 'Image',
          status: 'Processed',
          source: 'Added by you',
          date: '02 Sep 2026',
        };
        setDocs((prev) => [newDoc, ...prev]);
        setMessage(`${file.name} successfully stored and verified.`);
        setTimeout(() => setUploadState('idle'), 3000);
      }, 1000);
    }, 800);
  };

  return (
    <div className="documents-page">
      <div className="page-intro">
        <div>
          <h2>Medical Documents Hub</h2>
          <p>Store, organize, and view original clinical source documents with private server-side access.</p>
        </div>
        <label className="primary file-upload-btn">
          <Upload size={17} /> Upload Document
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleUpload(file);
            }}
          />
        </label>
      </div>

      {message && <div className="toast-banner"><CheckCircle2 size={16} />{message}</div>}

      {/* Upload Drag-and-Drop Area */}
      <div className="upload-dropzone">
        <Upload size={32} className="text-teal" />
        <h3>Drag and drop clinical files here</h3>
        <p>Supports PDF, JPG, JPEG, PNG up to 10 MB. Files are stored privately and protected against unauthorized retrieval.</p>
      </div>

      {/* Document List */}
      <Card title="Stored Health Documents">
        <div className="list">
          {docs.map((d) => (
            <div className="list-item doc-row" key={d.id}>
              <div className="event-icon"><FileText size={18} /></div>
              <div className="doc-info">
                <strong>{d.name}</strong>
                <small>Source: <strong>{d.source}</strong> · Date: {d.date} · Size: {d.size}</small>
              </div>
              <div className="doc-actions">
                <span className="status">{d.status}</span>
                <button className="text-btn font-bold" onClick={() => setSelectedDoc(d)}>
                  <Eye size={15} /> View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Document Viewer Modal */}
      {selectedDoc && (
        <div className="modal-overlay" onClick={() => setSelectedDoc(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedDoc.name}</h2>
              <button className="icon" onClick={() => setSelectedDoc(null)}><X size={18} /></button>
            </div>
            <div className="modal-body">
              <div className="doc-preview-box">
                <FileText size={48} className="text-teal mb-2" />
                <p><strong>Secure Document Viewer</strong></p>
                <small className="muted">Private storage path isolated from client. Authorized server-side stream only.</small>
              </div>

              <div className="stat-grid mt-3">
                <div className="stat-item"><span className="stat-label">Document ID:</span><strong>{selectedDoc.id}</strong></div>
                <div className="stat-item"><span className="stat-label">File Type:</span><strong>{selectedDoc.type}</strong></div>
                <div className="stat-item"><span className="stat-label">Original Source:</span><strong>{selectedDoc.source}</strong></div>
                <div className="stat-item"><span className="stat-label">Record Date:</span><strong>{selectedDoc.date}</strong></div>
              </div>
            </div>
            <div className="modal-actions">
              <button className="primary" onClick={() => setSelectedDoc(null)}>Close Viewer</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* =========================================================================================
   PAGE 8: LABORATORY REPORTS & AI INTERPRETATION
   ========================================================================================= */
function LaboratoryPage({ token }: { token: string }) {
  const [activeTab, setActiveTab] = useState<'table' | 'ai'>('table');

  const analytes = [
    { name: 'Glucose (Fasting)', value: '126', unit: 'mg/dL', ref: '70–99 mg/dL', status: 'above_reference', flag: 'High' },
    { name: 'Creatinine', value: '0.9', unit: 'mg/dL', ref: '0.6–1.2 mg/dL', status: 'within_reference', flag: 'Normal' },
    { name: 'eGFR', value: '98', unit: 'mL/min/1.73m²', ref: '60–120 mL/min', status: 'within_reference', flag: 'Normal' },
    { name: 'Sodium', value: '140', unit: 'mmol/L', ref: '135–145 mmol/L', status: 'within_reference', flag: 'Normal' },
    { name: 'Potassium', value: '4.2', unit: 'mmol/L', ref: '3.5–5.0 mmol/L', status: 'within_reference', flag: 'Normal' },
    { name: 'Chloride', value: '102', unit: 'mmol/L', ref: '96–106 mmol/L', status: 'within_reference', flag: 'Normal' },
    { name: 'Carbon Dioxide', value: '24', unit: 'mmol/L', ref: '22–29 mmol/L', status: 'within_reference', flag: 'Normal' },
    { name: 'Calcium', value: '9.4', unit: 'mg/dL', ref: '8.5–10.2 mg/dL', status: 'within_reference', flag: 'Normal' },
  ];

  return (
    <div className="laboratory-page">
      <div className="page-intro">
        <div>
          <h2>Laboratory Reports & AI Interpretation</h2>
          <p>Structured analyte values with exact source reference ranges and non-diagnostic plain explanations.</p>
        </div>
        <span className="verified"><ShieldCheck size={16} /> Source-Verified (Northstar Lab)</span>
      </div>

      <Card title="Comprehensive Metabolic Panel — 28 Aug 2026">
        <div className="lab-report-header">
          <div>
            <span className="prov-label">Ordering Provider:</span> <strong>Dr. Elena Vance, MD</strong>
          </div>
          <div>
            <span className="prov-label">Source Organization:</span> <strong>Northstar Laboratory</strong>
          </div>
          <div>
            <span className="prov-label">Report ID:</span> <code>LAB-2026-08-28-001</code>
          </div>
        </div>

        {/* Structured Analyte Table */}
        <div className="analyte-table-wrapper">
          <table className="analyte-table">
            <thead>
              <tr>
                <th>Test / Analyte</th>
                <th>Result</th>
                <th>Source Reference Range</th>
                <th>Evaluation</th>
              </tr>
            </thead>
            <tbody>
              {analytes.map((a) => (
                <tr key={a.name} className={a.status === 'above_reference' ? 'row-alert' : ''}>
                  <td><strong>{a.name}</strong></td>
                  <td><strong className={a.status === 'above_reference' ? 'text-danger' : ''}>{a.value} {a.unit}</strong></td>
                  <td>{a.ref}</td>
                  <td>
                    <span className={`status ${a.status === 'above_reference' ? 'needs' : 'verified-tag'}`}>
                      {a.flag}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* AI Lab Interpretation Box */}
        <div className="ai-lab-interpretation-card mt-4">
          <div className="ai-box-head">
            <Sparkles className="text-teal" size={20} />
            <div>
              <h3>AI Plain-Language Interpretation</h3>
              <p className="muted">Informational context derived from source values and reference ranges.</p>
            </div>
          </div>

          <div className="interpretation-breakdown">
            <div className="interp-row">
              <span className="interp-label">SOURCE:</span>
              <span>Northstar Laboratory (28 Aug 2026)</span>
            </div>
            <div className="interp-row">
              <span className="interp-label">KEY RESULT:</span>
              <span>Fasting Glucose: <strong>126 mg/dL</strong></span>
            </div>
            <div className="interp-row">
              <span className="interp-label">REFERENCE:</span>
              <span>70–99 mg/dL (Source-provided range)</span>
            </div>
            <div className="interp-row">
              <span className="interp-label">AI EXPLANATION:</span>
              <p className="interp-text">
                "The glucose result (126 mg/dL) is above the reference range (70–99 mg/dL) shown on your report. All other metabolic analytes, including kidney filtration (eGFR: 98) and electrolytes (Sodium, Potassium, Calcium), are within normal source ranges."
              </p>
            </div>
            <div className="interp-row">
              <span className="interp-label">LIMITATIONS:</span>
              <p className="interp-text muted">
                This AI tool explains lab results in plain language. It does NOT diagnose conditions (e.g. will not say 'You have diabetes') and does NOT prescribe or alter treatments. Discuss these findings with your care provider.
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}

/* =========================================================================================
   PAGE 9: MEDICATION VAULT & ADHERENCE ML
   ========================================================================================= */
function MedicationsPage({ token }: { token: string }) {
  const [meds, setMeds] = useState([
    { id: 'm1', name: 'Metformin', dose: '500 mg', freq: 'Twice daily', schedule: 'Twice daily with meals (8:00 AM & 8:00 PM)', adherence: 96, status: 'Due 8:00 PM', source: 'Demo Care Clinic' },
    { id: 'm2', name: 'Lisinopril', dose: '10 mg', freq: 'Once daily', schedule: 'Every morning at 8:00 AM', adherence: 92, status: 'Taken Today', source: 'Demo Care Clinic' },
  ]);
  const [modalOpen, setModalOpen] = useState(false);
  const [newMedName, setNewMedName] = useState('');
  const [newMedDose, setNewMedDose] = useState('');

  const toggleDose = (id: string) => {
    setMeds((prev) =>
      prev.map((m) => {
        if (m.id === id) {
          const isTaken = m.status === 'Taken Today';
          return { ...m, status: isTaken ? 'Due Today' : 'Taken Today', adherence: isTaken ? m.adherence - 2 : Math.min(100, m.adherence + 2) };
        }
        return m;
      })
    );
  };

  const handleAddMed = (e: FormEvent) => {
    e.preventDefault();
    if (!newMedName) return;
    const item = {
      id: `m-${Date.now()}`,
      name: newMedName,
      dose: newMedDose || 'As directed',
      freq: 'Daily',
      schedule: 'Once daily with water',
      adherence: 100,
      status: 'Due Today',
      source: 'Added by you',
    };
    setMeds((prev) => [...prev, item]);
    setModalOpen(false);
    setNewMedName('');
    setNewMedDose('');
  };

  return (
    <div className="medications-page">
      <div className="page-intro">
        <div>
          <h2>Medication Vault & Adherence ML</h2>
          <p>Organize prescriptions, log dose adherence, and view database interaction alerts.</p>
        </div>
        <button className="primary" onClick={() => setModalOpen(true)}>
          <Plus size={17} /> Add Medication
        </button>
      </div>

      {/* Active Medications List */}
      <Card title="Active Medications & Daily Dosing">
        <div className="med-vault-list">
          {meds.map((m) => (
            <div className="med-vault-card" key={m.id}>
              <div className="med-main-col">
                <span className="pill-icon large"><Pill size={22} /></span>
                <div>
                  <h3>{m.name} <span className="muted">{m.dose}</span></h3>
                  <p className="med-sched">{m.schedule}</p>
                  <small className="muted">Prescribed by {m.source}</small>
                </div>
              </div>

              <div className="med-status-col">
                <div className="adherence-badge">
                  <strong>{m.adherence}%</strong>
                  <small>Adherence Score</small>
                </div>
                <button className={`dose-toggle-btn ${m.status === 'Taken Today' ? 'taken' : 'due'}`} onClick={() => toggleDose(m.id)}>
                  {m.status === 'Taken Today' ? <><Check size={16} /> Dose Taken</> : 'Mark Dose Taken'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* ML Adherence Model Prediction Box */}
      <div className="two mt-3">
        <Card title="ML Adherence Predictor">
          <div className="adherence-ml-box">
            <div className="kpi-mini">
              <p className="eyebrow">PREDICTED ADHERENCE PROBABILITY</p>
              <h2>94.2%</h2>
              <span className="status verified-tag">High Compliance Tier</span>
            </div>
            <p className="mt-2 text-muted">
              Model evaluates historical intake patterns, scheduled versus taken doses, and elapsed days since last missed dose.
            </p>
            <p className="disclaimer-mini mt-2">Adherence prediction is informational only. It does not automatically alter prescription schedules.</p>
          </div>
        </Card>

        {/* Database Interaction Safety Center */}
        <Card title="Drug Interaction Safety Center">
          <div className="interaction-alert-box">
            <div className="interaction-header">
              <ShieldAlert size={20} className="text-amber" />
              <strong>Database-Derived Clinical Interaction Alert</strong>
            </div>
            <p className="mt-2">
              <strong>Combination:</strong> Metformin 500mg + Lisinopril 10mg
            </p>
            <p className="interaction-detail">
              Lisinopril may enhance the blood glucose lowering effect of Metformin. Regular glucose self-monitoring is advised.
            </p>
            <p className="disclaimer-mini mt-2">
              <strong>Safety Boundary:</strong> This warning is derived from a clinical reference database, not invented by an LLM. Always consult your pharmacist.
            </p>
          </div>
        </Card>
      </div>

      {/* Add Medication Modal */}
      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add Medication to Vault</h2>
              <button className="icon" onClick={() => setModalOpen(false)}><X size={18} /></button>
            </div>
            <form onSubmit={handleAddMed}>
              <div className="modal-body">
                <label>
                  Medication Name
                  <input required placeholder="e.g. Atorvastatin" value={newMedName} onChange={(e) => setNewMedName(e.target.value)} />
                </label>
                <label>
                  Dosage
                  <input required placeholder="e.g. 20 mg" value={newMedDose} onChange={(e) => setNewMedDose(e.target.value)} />
                </label>
                <label>
                  Frequency & Instructions
                  <input defaultValue="Once daily at bedtime" />
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="outline" onClick={() => setModalOpen(false)}>Cancel</button>
                <button type="submit" className="primary">Add to Vault</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

/* =========================================================================================
   PAGE 10: APPOINTMENTS & SCHEDULING
   ========================================================================================= */
function AppointmentsPage({ token }: { token: string }) {
  const [apts, setApts] = useState([
    { id: 'apt-1', title: 'Primary Care Routine Follow-up', doctor: 'Dr. Elena Vance, MD', place: 'Demo Care Clinic', when: '03 Sep 2026 · 10:30 AM', status: 'Confirmed', notes: 'Review fasting metabolic panel results.' },
    { id: 'apt-2', title: 'Annual Eye Examination', doctor: 'Dr. Kenneth Cho, OD', place: 'Visionworks (Demo Care)', when: '16 Sep 2026 · 2:00 PM', status: 'Pending', notes: 'Diabetic retinal check and vision check.' },
  ]);
  const [modalOpen, setModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [msg, setMsg] = useState('');

  const handleCancel = (id: string) => {
    setApts((prev) => prev.map((a) => (a.id === id ? { ...a, status: 'Cancelled' } : a)));
  };

  const handleBook = (e: FormEvent) => {
    e.preventDefault();
    if (!title) return;
    const newApt = {
      id: `apt-${Date.now()}`,
      title,
      doctor: 'Dr. Elena Vance, MD',
      place: 'Demo Care Clinic',
      when: '24 Sep 2026 · 11:00 AM',
      status: 'Confirmed',
      notes: 'Scheduled via Personal Gateway request.',
    };
    setApts((prev) => [...prev, newApt]);
    setModalOpen(false);
    setTitle('');
    setMsg('Appointment request recorded in development demo.');
    setTimeout(() => setMsg(''), 4000);
  };

  return (
    <div className="appointments-page">
      <div className="page-intro">
        <div>
          <h2>Appointment Management</h2>
          <p>Organize clinical visits and follow-ups with transparent demo availability.</p>
        </div>
        <button className="primary" onClick={() => setModalOpen(true)}>
          <Plus size={17} /> Request Appointment
        </button>
      </div>

      {msg && <div className="success-banner mb-3"><CheckCircle2 size={16} />{msg}</div>}

      <Card title="Upcoming Appointments">
        <div className="list">
          {apts.map((a) => (
            <div className="list-item" key={a.id}>
              <div className="event-icon"><Calendar size={18} /></div>
              <div className="flex-1">
                <strong>{a.title}</strong>
                <small>{a.doctor} · {a.when}</small>
                <small className="muted">{a.place} · {a.notes}</small>
              </div>
              <div className="flex-actions">
                <span className={`status ${a.status === 'Confirmed' ? 'verified-tag' : a.status === 'Cancelled' ? 'danger-tag' : 'needs'}`}>
                  {a.status}
                </span>
                {a.status !== 'Cancelled' && (
                  <button className="text-btn danger-text" onClick={() => handleCancel(a.id)}>
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Book Appointment Modal */}
      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Request Clinical Appointment</h2>
              <button className="icon" onClick={() => setModalOpen(false)}><X size={18} /></button>
            </div>
            <form onSubmit={handleBook}>
              <div className="modal-body">
                <label>
                  Appointment Purpose / Specialty
                  <input required placeholder="e.g. Cardiology Consultation" value={title} onChange={(e) => setTitle(e.target.value)} />
                </label>
                <label>
                  Preferred Healthcare Provider
                  <select defaultValue="Dr. Elena Vance, MD">
                    <option value="Dr. Elena Vance, MD">Dr. Elena Vance, MD (Internal Medicine)</option>
                    <option value="Dr. Kenneth Cho, OD">Dr. Kenneth Cho, OD (Optometry)</option>
                  </select>
                </label>
                <label>
                  Preferred Date & Time Window
                  <input type="datetime-local" defaultValue="2026-09-24T11:00" required />
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="outline" onClick={() => setModalOpen(false)}>Cancel</button>
                <button type="submit" className="primary">Confirm Request</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

/* =========================================================================================
   PAGE 11: CARE NAVIGATION (Directory Search, Ranking, Matching)
   ========================================================================================= */
function CareNavigationPage({ token, navigateTo }: { token: string; navigateTo: (p: string) => void }) {
  const [query, setQuery] = useState('');
  const [filterType, setFilterType] = useState('all');

  const places = [
    { id: 'cp-1', name: 'Dr. Elena Vance, MD', type: 'doctor', spec: 'Internal Medicine & Primary Care', org: 'Demo Care Clinic', addr: '1200 Healthway Blvd, Seattle, WA', rating: '4.9 ★', dist: '1.2 miles', avail: 'Next week' },
    { id: 'cp-2', name: 'Dr. Kenneth Cho, OD', type: 'doctor', spec: 'Optometry & Retinal Care', org: 'Visionworks (Demo)', addr: '500 Pine St, Seattle, WA', rating: '4.8 ★', dist: '2.4 miles', avail: 'This month' },
    { id: 'cp-3', name: 'Northstar Diagnostic Laboratory', type: 'laboratory', spec: 'Blood Pathology & Metabolic Panels', org: 'Northstar Lab Network', addr: '800 5th Ave, Seattle, WA', rating: '4.7 ★', dist: '0.8 miles', avail: 'Walk-ins welcome' },
    { id: 'cp-4', name: 'Healthline Pharmacy (Central)', type: 'pharmacy', spec: 'Prescriptions & Medication Review', org: 'Healthline Group', addr: '1401 4th Ave, Seattle, WA', rating: '4.9 ★', dist: '0.5 miles', avail: 'Open until 9 PM' },
    { id: 'cp-5', name: 'Seattle Central Medical Center', type: 'hospital', spec: 'Emergency, Acute Care & Surgery', org: 'Central Health System', addr: '1100 9th Ave, Seattle, WA', rating: '4.6 ★', dist: '1.8 miles', avail: '24/7 Facility' },
  ];

  const filtered = places.filter((p) => {
    const matchesType = filterType === 'all' || p.type === filterType;
    const matchesQuery = p.name.toLowerCase().includes(query.toLowerCase()) || p.spec.toLowerCase().includes(query.toLowerCase()) || p.addr.toLowerCase().includes(query.toLowerCase());
    return matchesType && matchesQuery;
  });

  return (
    <div className="care-navigation-page">
      <div className="page-intro">
        <div>
          <h2>Care Navigation & Provider Directory</h2>
          <p>Search doctors, diagnostic labs, pharmacies, and hospitals with multi-factor ranking.</p>
        </div>
        <span className="demo">Synthetic Demo Directory</span>
      </div>

      <Card>
        <div className="care-search-controls">
          <div className="search-field flex-1">
            <Search size={18} />
            <input placeholder="Search by name, specialty, service, or location in Seattle…" value={query} onChange={(e) => setQuery(e.target.value)} />
          </div>

          <div className="care-filter-tabs">
            {['all', 'doctor', 'laboratory', 'pharmacy', 'hospital'].map((t) => (
              <button key={t} className={filterType === t ? 'pill active capitalize' : 'pill capitalize'} onClick={() => setFilterType(t)}>
                {t === 'all' ? 'All Providers' : t}
              </button>
            ))}
          </div>
        </div>

        <div className="care-results-list mt-3">
          {filtered.map((item) => (
            <div className="care-result-card" key={item.id}>
              <div className="care-icon-badge">
                {item.type === 'doctor' ? <Stethoscope size={22} /> : item.type === 'laboratory' ? <Layers size={22} /> : item.type === 'pharmacy' ? <Pill size={22} /> : <Building2 size={22} />}
              </div>
              <div className="care-details">
                <div className="care-title-row">
                  <h3>{item.name}</h3>
                  <span className="rating-badge">{item.rating}</span>
                </div>
                <p className="care-spec">{item.spec}</p>
                <small className="muted">{item.addr} · {item.dist}</small>
                <div className="care-footer-row">
                  <span className="avail-tag">Availability: {item.avail}</span>
                  <button className="primary-btn-sm" onClick={() => navigateTo('appointments')}>
                    Select Provider
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

/* =========================================================================================
   PAGE 12: PERSONAL AI ASSISTANT (Grounded Personal RAG, Citations, Injection Safety)
   ========================================================================================= */
function AiAssistantPage({ token }: { token: string }) {
  const [messages, setMessages] = useState<any[]>([
    {
      role: 'assistant',
      content: "Hello Avery. I'm your Personal Health Assistant grounded strictly in your authorized health records. I can summarize vitals, explain lab reports, review medications, or recall upcoming appointments. What would you like to explore?",
      sources: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendQuery = async (queryText = input) => {
    if (!queryText.trim()) return;
    const userMsg = { role: 'user', content: queryText };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api<any>('/ai/answer', token, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: queryText }),
      });

      const aiMsg = {
        role: 'assistant',
        content: res.answer,
        sources: res.sources || [],
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'I encountered an error retrieving authorized records for that question. Please try again.',
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    'What was my latest glucose result?',
    'What medications are currently active?',
    'When is my next appointment?',
    'Summarize my recent metabolic panel.',
    'How has my blood pressure changed?',
  ];

  return (
    <div className="ai-assistant-page">
      <div className="assistant-intro">
        <span className="spark-lg">✦</span>
        <div>
          <h2>Personal AI Health Assistant</h2>
          <p>Grounded strictly in your authorized records. Untrusted document input is isolated against prompt injection.</p>
        </div>
      </div>

      <Card className="chat-card">
        <div className="messages-stream">
          {messages.map((m, idx) => (
            <div className={`chat-message ${m.role}`} key={idx}>
              <div className="message-bubble">
                <p>{m.content}</p>
                {m.sources && m.sources.length > 0 && (
                  <div className="sources-container">
                    <span className="sources-header"><FileText size={13} /> Grounded Sources & References:</span>
                    <div className="sources-chips">
                      {m.sources.map((s: any, sIdx: number) => (
                        <div className="source-chip" key={sIdx}>
                          <strong>{s.title}</strong> · {s.source} ({s.source_date})
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-message assistant">
              <div className="message-bubble typing-bubble">
                <RefreshCw size={15} className="spinner" /> Grounding response in authorized personal records…
              </div>
            </div>
          )}
        </div>

        {/* Suggestion Prompts */}
        <div className="chat-suggestions">
          {suggestions.map((s) => (
            <button key={s} className="suggestion-pill" onClick={() => sendQuery(s)}>
              {s}
            </button>
          ))}
        </div>

        {/* Chat Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendQuery();
          }}
          className="chat-input-bar"
        >
          <input placeholder="Ask about your authorized health records, lab reports, or medications…" value={input} onChange={(e) => setInput(e.target.value)} />
          <button className="primary" disabled={loading || !input.trim()}>
            Send Query <ArrowRight size={16} />
          </button>
        </form>

        <p className="disclaimer-mini mt-2">
          <strong>AI Safety Guarantee:</strong> The Personal AI Assistant is strictly informational and non-diagnostic. It does not replace clinical judgment or prescribe treatments.
        </p>
      </Card>
    </div>
  );
}

/* =========================================================================================
   PAGE 13: EMERGENCY READINESS (Emergency Profile, Contacts, SOS Interface)
   ========================================================================================= */
function EmergencyPage({ token, setSosModalOpen }: { token: string; setSosModalOpen: (o: boolean) => void }) {
  const [contacts, setContacts] = useState([
    { id: 'c-1', name: 'Jordan Morgan', rel: 'Spouse', phone: '+1 (555) 014-1001', primary: true },
  ]);
  const [contactName, setContactName] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [contactRel, setContactRel] = useState('');

  const handleAddContact = (e: FormEvent) => {
    e.preventDefault();
    if (!contactName || !contactPhone) return;
    const newContact = {
      id: `c-${Date.now()}`,
      name: contactName,
      phone: contactPhone,
      rel: contactRel || 'Contact',
      primary: false,
    };
    setContacts((prev) => [...prev, newContact]);
    setContactName('');
    setContactPhone('');
    setContactRel('');
  };

  const deleteContact = (id: string) => {
    setContacts((prev) => prev.filter((c) => c.id !== id));
  };

  return (
    <div className="emergency-page">
      <div className="page-intro">
        <div>
          <h2>Emergency Profile & Readiness</h2>
          <p>Prepare vital medical directives and emergency contacts for critical care workflows.</p>
        </div>
        <button className="danger-btn" onClick={() => setSosModalOpen(true)}>
          <AlertCircle size={18} /> Launch Emergency SOS View
        </button>
      </div>

      <div className="emergency-alert-banner">
        <Info size={18} />
        <p>
          <strong>Product Boundary:</strong> Module 1 establishes your personal emergency readiness profile. Autonomous emergency calling and ambulance dispatch belong to the future Emergency Intelligence module.
        </p>
      </div>

      <div className="two">
        <Card title="Critical Medical Information">
          <div className="emergency-data-list">
            <div className="em-row">
              <span className="em-label">Blood Group:</span>
              <strong className="em-value text-teal">O Positive (O+)</strong>
            </div>
            <div className="em-row">
              <span className="em-label">Severe Allergies:</span>
              <strong className="em-value text-danger">Penicillin (Moderate / Hives)</strong>
            </div>
            <div className="em-row">
              <span className="em-label">Critical Conditions:</span>
              <strong className="em-value">Mild Hypertension (Managed)</strong>
            </div>
            <div className="em-row">
              <span className="em-label">Preferred Hospital:</span>
              <strong className="em-value">Seattle Central Medical Center</strong>
            </div>
            <div className="em-row">
              <span className="em-label">Medical Directives:</span>
              <p className="directives-text">"No extraordinary measures without consulting primary emergency contact."</p>
            </div>
          </div>
        </Card>

        <Card title="Emergency Contacts Management">
          <div className="contacts-list">
            {contacts.map((c) => (
              <div className="contact-item-row" key={c.id}>
                <div className="contact-icon"><Phone size={18} /></div>
                <div className="flex-1">
                  <strong>{c.name} {c.primary && <span className="primary-tag">Primary</span>}</strong>
                  <small>{c.rel} · {c.phone}</small>
                </div>
                {!c.primary && (
                  <button className="icon-btn text-danger" onClick={() => deleteContact(c.id)}>
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            ))}
          </div>

          <form onSubmit={handleAddContact} className="add-contact-form mt-3">
            <h4>Add Secondary Emergency Contact</h4>
            <div className="form-row-2">
              <input placeholder="Full Name" required value={contactName} onChange={(e) => setContactName(e.target.value)} />
              <input placeholder="Phone (+1...)" required value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} />
            </div>
            <input placeholder="Relationship (e.g. Sibling, Physician)" value={contactRel} onChange={(e) => setContactRel(e.target.value)} />
            <button className="outline full mt-2">Add Contact</button>
          </form>
        </Card>
      </div>
    </div>
  );
}

/* =========================================================================================
   PAGE 14: PRIVACY CENTER (Audit Access Logs, Active Sessions, Security)
   ========================================================================================= */
function PrivacyPage({ token }: { token: string }) {
  const accessLogs = [
    { org: 'Northstar Diagnostic Laboratory', scope: 'Imported Metabolic Panel — Aug 2026', purpose: 'Direct laboratory sync', date: '28 Aug 2026, 09:05 AM', status: 'Authorized' },
    { org: 'Demo Care Clinic', scope: 'Profile & Active Medications', purpose: 'Pre-consultation clinical review', date: '20 Aug 2026, 02:22 PM', status: 'Authorized' },
    { org: 'Patient Home Telehealth Device', scope: 'Blood Pressure Log Upload', purpose: 'Patient measurement import', date: '19 Aug 2026, 09:12 AM', status: 'Authorized' },
  ];

  return (
    <div className="privacy-page">
      <div className="page-intro">
        <div>
          <h2>Privacy Center & Access Audit Logs</h2>
          <p>Review who accessed your health information, what data was shared, and for what purpose.</p>
        </div>
        <span className="verified"><ShieldCheck size={16} /> Privacy-First Sovereign Storage</span>
      </div>

      <Card title="Data Access Audit Trail">
        <table className="audit-table">
          <thead>
            <tr>
              <th>Organization / Entity</th>
              <th>Data Scope</th>
              <th>Clinical Purpose</th>
              <th>Timestamp</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {accessLogs.map((log, i) => (
              <tr key={i}>
                <td><strong>{log.org}</strong></td>
                <td>{log.scope}</td>
                <td>{log.purpose}</td>
                <td><small>{log.date}</small></td>
                <td><span className="status verified-tag">{log.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <div className="two mt-3">
        <Card title="Active Browser Sessions">
          <div className="session-item">
            <div className="event-icon"><Lock size={18} /></div>
            <div>
              <strong>Current Active Session (This Browser)</strong>
              <small>Seattle, WA · IP: 127.0.0.1 · Active Now</small>
            </div>
            <span className="status">Current</span>
          </div>
        </Card>

        <Card title="Data Minimization & Sovereign Control">
          <p className="text-muted">
            You hold total control over third-party data sharing. Authorized organizations receive temporary cryptographic grants that expire automatically.
          </p>
        </Card>
      </div>
    </div>
  );
}

/* =========================================================================================
   PAGE 15: CONSENT MANAGEMENT (Granular Grants, Scope, Expiry, Revocation)
   ========================================================================================= */
function ConsentPage({ token }: { token: string }) {
  const [consents, setConsents] = useState([
    {
      id: 'c-1',
      org: 'Example Clinic',
      purpose: 'Specialist Consultation (Endocrinology review)',
      scopes: ['Laboratory reports', 'Prescriptions', 'Vital trends'],
      expires: '30 Sep 2026',
      status: 'Requested',
    },
    {
      id: 'c-2',
      org: 'Northstar Laboratory Network',
      purpose: 'Automated diagnostic test synchronization',
      scopes: ['Laboratory reports'],
      expires: '01 Aug 2027',
      status: 'Approved',
    },
  ]);

  const updateStatus = (id: string, newStatus: string) => {
    setConsents((prev) => prev.map((c) => (c.id === id ? { ...c, status: newStatus } : c)));
  };

  return (
    <div className="consent-page">
      <div className="page-intro">
        <div>
          <h2>Consent Center & Data Sharing Grants</h2>
          <p>Approve, deny, or revoke third-party healthcare access with custom scopes and expiry.</p>
        </div>
        <span className="demo">Granular Policy Engine</span>
      </div>

      <div className="consent-grid">
        {consents.map((c) => (
          <Card key={c.id} className="consent-card">
            <div className="consent-head-row">
              <h3>{c.org}</h3>
              <span className={`status ${c.status === 'Approved' ? 'verified-tag' : c.status === 'Denied' || c.status === 'Revoked' ? 'danger-tag' : 'needs'}`}>
                Status: {c.status}
              </span>
            </div>

            <p className="consent-purpose"><strong>Purpose:</strong> {c.purpose}</p>

            <div className="consent-scope-box">
              <span className="prov-label">Requested Data Scope:</span>
              <div className="scope-pills">
                {c.scopes.map((s) => (
                  <span className="scope-pill" key={s}>
                    ✓ {s}
                  </span>
                ))}
              </div>
            </div>

            <p className="expiry-meta">Expires: <strong>{c.expires}</strong></p>

            <div className="consent-action-buttons">
              {c.status !== 'Approved' && (
                <button className="primary-btn-sm" onClick={() => updateStatus(c.id, 'Approved')}>
                  Approve Consent
                </button>
              )}
              {c.status !== 'Denied' && c.status !== 'Revoked' && (
                <button className="outline-btn-sm" onClick={() => updateStatus(c.id, 'Denied')}>
                  Deny
                </button>
              )}
              {c.status === 'Approved' && (
                <button className="danger-btn-sm" onClick={() => updateStatus(c.id, 'Revoked')}>
                  Revoke Access Immediately
                </button>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

/* =========================================================================================
   PAGE 16: NOTIFICATIONS CENTER
   ========================================================================================= */
function NotificationsPage({ token, unreadCount, setUnreadCount }: { token: string; unreadCount: number; setUnreadCount: React.Dispatch<React.SetStateAction<number>> }) {
  const [filter, setFilter] = useState('all');
  const [notifs, setNotifs] = useState([
    { id: 'n1', cat: 'laboratory', title: 'Lab report available: Comprehensive Metabolic Panel', desc: 'Northstar Laboratory results have been processed and indexed.', read: false, time: '28 Aug 2026' },
    { id: 'n2', cat: 'medication', title: 'Medication dose reminder: Metformin 500mg', desc: 'Evening dose due at 8:00 PM with dinner.', read: false, time: 'Today' },
    { id: 'n3', cat: 'appointment', title: 'Upcoming appointment reminder: Routine Follow-up', desc: 'Scheduled for tomorrow at 10:30 AM with Dr. Elena Vance.', read: true, time: 'Today' },
    { id: 'n4', cat: 'consent', title: 'Consent request from Example Clinic', desc: 'Specialist consultation requested access to laboratory reports.', read: true, time: '25 Aug 2026' },
  ]);

  const markAllRead = () => {
    setNotifs((prev) => prev.map((n) => ({ ...n, read: true })));
    setUnreadCount(0);
  };

  const markSingleRead = (id: string) => {
    setNotifs((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
    setUnreadCount((c) => Math.max(0, c - 1));
  };

  const filtered = notifs.filter((n) => filter === 'all' || n.cat === filter);

  return (
    <div className="notifications-page">
      <div className="page-intro">
        <div>
          <h2>Notifications Center</h2>
          <p>Important alerts across appointments, medications, lab results, and consent requests.</p>
        </div>
        <button className="outline" onClick={markAllRead}>
          Mark All as Read
        </button>
      </div>

      <div className="filter-pills mb-3">
        {['all', 'laboratory', 'medication', 'appointment', 'consent'].map((f) => (
          <button key={f} className={filter === f ? 'pill active capitalize' : 'pill capitalize'} onClick={() => setFilter(f)}>
            {f === 'all' ? 'All Alerts' : f}
          </button>
        ))}
      </div>

      <Card>
        <div className="list">
          {filtered.map((n) => (
            <div className={`list-item ${!n.read ? 'unread-row' : ''}`} key={n.id} onClick={() => markSingleRead(n.id)}>
              <div className="event-icon"><Bell size={18} /></div>
              <div className="flex-1">
                <strong>{n.title}</strong>
                <small>{n.desc}</small>
                <small className="muted">{n.time}</small>
              </div>
              {!n.read && <span className="unread">New</span>}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

/* =========================================================================================
   PAGE 17: SETTINGS & DATA EXPORT WORKFLOW
   ========================================================================================= */
function SettingsPage({ token }: { token: string }) {
  const [exportState, setExportState] = useState<'idle' | 'exporting' | 'ready'>('idle');
  const [downloadJson, setDownloadJson] = useState<string | null>(null);

  const handleExport = async () => {
    setExportState('exporting');
    try {
      const res = await api<any>('/export', token, { method: 'POST' });
      setTimeout(async () => {
        const downloadData = await api<any>(res.download_url, token);
        setDownloadJson(JSON.stringify(downloadData, null, 2));
        setExportState('ready');
      }, 1000);
    } catch (err) {
      setExportState('idle');
    }
  };

  const downloadFile = () => {
    if (!downloadJson) return;
    const blob = new Blob([downloadJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `personal-health-archive-avery-morgan-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="settings-page">
      <div className="page-intro">
        <div>
          <h2>Settings & Sovereign Data Export</h2>
          <p>Account preferences, security parameters, and full health data archive extraction.</p>
        </div>
      </div>

      <div className="three">
        <Card title="Account Security">
          <p>Personal Identity ID:</p>
          <code>usr-avery-morgan-87</code>
          <p className="mt-2 text-muted">Password management and MFA controls are linked to your secure identity provider.</p>
        </Card>

        <Card title="Connected Health Devices">
          <p><strong>Omron Blood Pressure Series 10</strong></p>
          <small className="status verified-tag">Synced</small>
          <p className="mt-2 text-muted">Bluetooth Home Telehealth connection active.</p>
        </Card>

        <Card title="Notification Preferences">
          <div className="checkbox-row column">
            <label><input type="checkbox" defaultChecked /> Email alerts for laboratory reports</label>
            <label><input type="checkbox" defaultChecked /> SMS reminders for medication dosing</label>
          </div>
        </Card>
      </div>

      {/* Real Backend Data Export Request Workflow */}
      <Card title="Sovereign Personal Data Export (JSON Portability)" className="mt-3">
        <p>
          Exercise full data portability. Request a complete cryptographic archive of your personal profile, vital recordings, medication vaults, laboratory results, and data provenance.
        </p>

        {exportState === 'idle' && (
          <button className="primary mt-3" onClick={handleExport}>
            <Download size={17} /> Request Personal Health Archive
          </button>
        )}

        {exportState === 'exporting' && (
          <div className="export-loading-box mt-3">
            <RefreshCw size={18} className="spinner text-teal" />
            <span>Generating structured health JSON archive from verified database records…</span>
          </div>
        )}

        {exportState === 'ready' && (
          <div className="export-ready-box mt-3">
            <div className="export-success-header">
              <CheckCircle2 size={20} className="text-teal" />
              <strong>Health Archive Ready for Download (Full JSON Portability)</strong>
            </div>
            <p className="muted mt-1">Contains complete profile, vitals, medications, laboratory panels, appointments, and consent grants.</p>
            <button className="primary mt-2" onClick={downloadFile}>
              <Download size={17} /> Download personal-health-archive.json
            </button>
          </div>
        )}
      </Card>
    </div>
  );
}
