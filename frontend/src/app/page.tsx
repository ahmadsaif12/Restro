import Link from 'next/link';
import {
  UtensilsCrossed,
  ArrowRight,
  Zap,
  Users,
  Globe,
  ShoppingBag,
  CreditCard,
  ChefHat,
  QrCode,
  Package,
  BarChart3,
  Info,
} from 'lucide-react';

const stats = [
  { icon: ShoppingBag, value: '10K+', label: 'Orders Processed' },
  { icon: Users, value: '500+', label: 'Active Users' },
  { icon: Zap, value: '99.9%', label: 'Uptime' },
  { icon: Globe, value: '5+', label: 'Countries' },
];

const features = [
  {
    icon: CreditCard,
    title: 'IRD-Compliant POS',
    desc: 'Complete billing system with multiple payment methods',
    color: '#E3F2FD',
    iconBg: '#1E88E5',
  },
  {
    icon: ChefHat,
    title: 'Kitchen Workflow',
    desc: 'Real-time prep board with multi-station routing',
    color: '#FFF3E0',
    iconBg: '#FF7043',
    highlight: true,
  },
  {
    icon: QrCode,
    title: 'Digital QR Menu',
    desc: 'Contactless ordering with real-time updates',
    color: '#F3E5F5',
    iconBg: '#AB47BC',
  },
  {
    icon: Package,
    title: 'Inventory System',
    desc: 'Recipe-based costing and waste management',
    color: '#E8F5E9',
    iconBg: '#43A047',
  },
  {
    icon: BarChart3,
    title: 'Live Analytics',
    desc: 'Real-time sales reports and insights',
    color: '#E8EAF6',
    iconBg: '#5C6BC0',
  },
  {
    icon: Users,
    title: 'Multi-Role Access',
    desc: 'Manager, waiter, and kitchen dashboards',
    color: '#FFF8E1',
    iconBg: '#FFA726',
  },
];

export default function HomePage() {
  return (
    <div className="landing">
      {/* ─── Hero ─── */}
      <section className="hero">
        <div className="hero-bg" />
        <div className="hero-content">
          <div className="hero-logo">
            <UtensilsCrossed color="white" size={40} />
          </div>
          <h1 className="hero-title">Handle My Restro</h1>
          <p className="hero-tagline">
            ✨ Complete Restaurant Management for Nepal ✨
          </p>
          <p className="hero-desc">
            Streamline your restaurant operations with our comprehensive full-stack system.
            From POS billing to kitchen workflow, inventory management, and analytics —
            everything you need in one place.
          </p>
          <div className="hero-actions">
            <Link href="/register" className="btn-hero-primary">
              Get Started Now <ArrowRight size={18} />
            </Link>
            <Link href="#features" className="btn-hero-secondary">
              <Info size={18} /> Learn More
            </Link>
          </div>

          {/* Stats */}
          <div className="stats-row">
            {stats.map((s) => (
              <div key={s.label} className="stat-card">
                <s.icon size={24} className="stat-icon" />
                <span className="stat-value">{s.value}</span>
                <span className="stat-label">{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Features ─── */}
      <section className="features" id="features">
        <h2 className="section-title">Powerful Features</h2>
        <p className="section-subtitle">Everything you need to run a successful restaurant</p>
        <div className="features-grid">
          {features.map((f) => (
            <div
              key={f.title}
              className={`feature-card ${f.highlight ? 'feature-card--highlight' : ''}`}
              style={{ backgroundColor: f.color }}
            >
              <div className="feature-icon" style={{ backgroundColor: f.iconBg }}>
                <f.icon color="white" size={22} />
              </div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
              {f.highlight && (
                <Link href="/register" className="feature-link">
                  Explore <ArrowRight size={14} />
                </Link>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ─── CTA ─── */}
      <section className="cta-section">
        <div className="cta-card">
          <div className="cta-icon-wrap">
            <UtensilsCrossed size={32} className="cta-icon" />
          </div>
          <h2 className="cta-title">Ready to Transform Your Restaurant?</h2>
          <p className="cta-desc">Join hundreds of restaurants already using Handle My Restro</p>
          <Link href="/register" className="btn-hero-primary">
            Start Your Journey <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer className="landing-footer">
        <p>© 2026 Handle My Restro. Built for restaurants in Nepal and beyond.</p>
      </footer>
    </div>
  );
}
