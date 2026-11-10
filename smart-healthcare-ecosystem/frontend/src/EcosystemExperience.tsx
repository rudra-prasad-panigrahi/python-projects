import { useState } from 'react';
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  BedDouble,
  Building2,
  CalendarDays,
  CheckCircle2,
  ClipboardList,
  Clock3,
  FlaskConical,
  HeartPulse,
  LockKeyhole,
  MapPin,
  Pill,
  ShieldCheck,
  Siren,
  Stethoscope,
  Truck,
  Users,
  Workflow,
  Zap,
} from 'lucide-react';

type ExperienceView = 'overview' | 'clinical' | 'emergency';

const modules = [
  {
    id: 'personal' as const,
    number: '01',
    title: 'Personal Intelligence',
    description: 'A lifelong, individual-controlled health record with understandable insights and emergency-ready information.',
    icon: HeartPulse,
    features: ['Profile, records & documents', 'Vitals, trends & explainable insights', 'Medication & appointment management', 'AI assistant, consent & emergency profile'],
    action: 'Open personal gateway',
  },
  {
    id: 'clinical' as const,
    number: '02',
    title: 'Clinical Intelligence',
    description: 'A shared operational workspace for care teams to prepare for, deliver and document coordinated care.',
    icon: Stethoscope,
    features: ['Patient & EHR workflows', 'Laboratory & pharmacy', 'Beds, ICU & resource readiness', 'Consent-based external records'],
    action: 'Preview hospital workspace',
  },
  {
    id: 'emergency' as const,
    number: '03',
    title: 'Emergency Intelligence',
    description: 'A carefully staged response workflow that connects event signals, responders and hospital readiness.',
    icon: Siren,
    features: ['Multisignal event assessment', 'User confirmation & escalation', 'Ambulance and capability matching', 'Minimum-necessary pre-arrival context'],
    action: 'Preview emergency workspace',
  },
];

const journeySteps = [
  { title: 'Before', detail: 'Health profile, records, monitoring and consent', icon: HeartPulse },
  { title: 'During', detail: 'Confirm and coordinate a possible emergency', icon: Siren },
  { title: 'Treatment', detail: 'Prepare a capable care team and resources', icon: Stethoscope },
  { title: 'After', detail: 'Return verified care information to the person', icon: CheckCircle2 },
  { title: 'Continuously', detail: 'Maintain a trusted, longitudinal health record', icon: Activity },
];

export default function EcosystemExperience({ onSelectPersonal }: { onSelectPersonal: () => void }) {
  const [view, setView] = useState<ExperienceView>('overview');
  const [demoStep, setDemoStep] = useState(0);

  const openOverview = () => {
    setView('overview');
    setDemoStep(0);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (view === 'clinical') {
    return <ClinicalPreview onBack={openOverview} onSelectPersonal={onSelectPersonal} />;
  }
  if (view === 'emergency') {
    return <EmergencyPreview onBack={openOverview} demoStep={demoStep} setDemoStep={setDemoStep} />;
  }

  return (
    <div className="ecosystem-page">
      <header className="ecosystem-header">
        <a className="ecosystem-brand" href="#home" aria-label="Smart Healthcare Ecosystem home">
          <span className="ecosystem-brand-mark"><HeartPulse size={22} /></span>
          <span><strong>Smart Healthcare</strong><small>Unified ecosystem</small></span>
        </a>
        <nav className="ecosystem-header-nav" aria-label="Main navigation">
          <a href="#modules">Modules</a>
          <a href="#journey">Care journey</a>
          <a href="#architecture">Architecture</a>
          <button className="ecosystem-signin" onClick={onSelectPersonal}>Personal sign in <ArrowRight size={16} /></button>
        </nav>
      </header>

      <main id="home">
        <section className="ecosystem-hero">
          <div className="ecosystem-hero-copy">
            <span className="ecosystem-eyebrow"><ShieldCheck size={15} /> Connected care · Privacy by design</span>
            <h1>One healthcare journey.<br /><span>Connected intelligence.</span></h1>
            <p>Bring personal health information, clinical operations and emergency response together in a permission-aware ecosystem—from everyday monitoring to treatment and recovery.</p>
            <div className="ecosystem-hero-actions">
              <a className="ecosystem-primary-button" href="#modules">Explore the ecosystem <ArrowRight size={17} /></a>
              <button className="ecosystem-text-button" onClick={onSelectPersonal}>Go to Personal Health <ArrowRight size={16} /></button>
            </div>
            <div className="ecosystem-trust-note"><LockKeyhole size={15} /> Prototype experience · Operational integrations are not live</div>
          </div>
          <div className="ecosystem-hero-visual" aria-label="Three connected healthcare modules">
            <div className="ecosystem-orbit ecosystem-orbit-outer" />
            <div className="ecosystem-orbit ecosystem-orbit-inner" />
            <div className="ecosystem-orbit-center"><HeartPulse size={35} /><span>Connected<br />care</span></div>
            <div className="ecosystem-orbit-node node-person"><HeartPulse size={20} /><span>Personal</span></div>
            <div className="ecosystem-orbit-node node-clinical"><Stethoscope size={20} /><span>Clinical</span></div>
            <div className="ecosystem-orbit-node node-emergency"><Siren size={20} /><span>Emergency</span></div>
            <div className="ecosystem-visual-caption"><span className="live-dot" /> One permission-aware care journey</div>
          </div>
        </section>

        <section className="ecosystem-module-section" id="modules">
          <div className="ecosystem-section-heading">
            <div><span className="ecosystem-eyebrow">One platform · Three connected modules</span><h2>Built around the complete care journey</h2></div>
            <p>Each module has a distinct role. Shared workflows connect them without making every system or user see every piece of data.</p>
          </div>
          <div className="ecosystem-module-grid">
            {modules.map((module) => {
              const Icon = module.icon;
              const action = module.id === 'personal' ? onSelectPersonal : () => setView(module.id);
              return (
                <article className={`ecosystem-module-card module-${module.id}`} key={module.id}>
                  <div className="ecosystem-module-card-top"><span className="ecosystem-module-icon"><Icon size={22} /></span><span className="ecosystem-module-number">MODULE {module.number}</span></div>
                  <h3>{module.title}</h3>
                  <p>{module.description}</p>
                  <ul>{module.features.map((feature) => <li key={feature}><CheckCircle2 size={15} />{feature}</li>)}</ul>
                  <button className="ecosystem-module-link" onClick={action}>{module.action}<ArrowRight size={16} /></button>
                </article>
              );
            })}
          </div>
        </section>

        <section className="ecosystem-journey-section" id="journey">
          <div className="ecosystem-section-heading">
            <div><span className="ecosystem-eyebrow">Continuity, not silos</span><h2>From everyday health to follow-up care</h2></div>
            <p>A connected workflow carries only the information needed at each step and returns verified treatment records to the individual.</p>
          </div>
          <div className="ecosystem-journey">
            {journeySteps.map((step, index) => {
              const Icon = step.icon;
              return <div className="ecosystem-journey-step" key={step.title}>
                <div className="ecosystem-journey-icon"><Icon size={20} /></div>
                <span className="ecosystem-journey-index">0{index + 1}</span>
                <h3>{step.title}</h3><p>{step.detail}</p>
                {index < journeySteps.length - 1 && <ArrowRight className="ecosystem-journey-arrow" size={17} />}
              </div>;
            })}
          </div>
          <div className="ecosystem-flow-callout"><Workflow size={19} /><p><strong>Example workflow:</strong> possible event → user confirmation → consent-aware emergency context → capability-matched hospital → pre-arrival preparation → verified treatment record.</p></div>
        </section>

        <section className="ecosystem-architecture-section" id="architecture">
          <div className="ecosystem-section-heading">
            <div><span className="ecosystem-eyebrow">Designed to evolve</span><h2>A modular foundation for secure coordination</h2></div>
            <p>Start with a manageable application and introduce infrastructure as workload and integrations require.</p>
          </div>
          <div className="ecosystem-architecture">
            <div className="architecture-interfaces"><Users size={19} /><strong>Interfaces</strong><span>Personal web / mobile · Hospital workspace · Emergency coordination</span></div>
            <div className="architecture-gateway"><ShieldCheck size={19} /><strong>API gateway & identity</strong><span>Authentication · Authorization · Consent verification · Rate limiting</span></div>
            <div className="architecture-service-grid">
              <div><HeartPulse size={19} /><strong>Personal services</strong><span>Profile · Records · Vitals · Documents · Medication</span></div>
              <div><Building2 size={19} /><strong>Clinical services</strong><span>Care teams · Labs · Pharmacy · Beds · Resources</span></div>
              <div><Siren size={19} /><strong>Emergency services</strong><span>Detection · Dispatch · Routing · Notifications</span></div>
            </div>
            <div className="architecture-ai"><Zap size={19} /><strong>AI / ML intelligence</strong><span>Grounded retrieval · Signal analysis · Explainability · Evaluation</span></div>
            <div className="architecture-data"><Activity size={19} /><strong>Data & operations</strong><span>PostgreSQL / pgvector · Object storage · Optional Redis / queue · Encryption · Audit · Monitoring · Backup</span></div>
          </div>
        </section>

        <section className="ecosystem-research-section">
          <div className="ecosystem-section-heading">
            <div><span className="ecosystem-eyebrow">Research that can be measured</span><h2>Test the integration—not just the interface</h2></div>
            <p>Proposed contributions and evaluation measures for a prototype. These are research goals, not validated clinical claims.</p>
          </div>
          <div className="ecosystem-research-grid">
            <div className="ecosystem-research-table">
              <div className="ecosystem-research-row ecosystem-research-head"><span>Contribution</span><span>How to evaluate</span></div>
              <div className="ecosystem-research-row"><span>Multisignal emergency assessment</span><span>Precision · Recall · F1 · False alarms / hour</span></div>
              <div className="ecosystem-research-row"><span>Capability-aware hospital matching</span><span>Capability fit · ETA vs nearest-only baseline</span></div>
              <div className="ecosystem-research-row"><span>Grounded personal health assistant</span><span>Retrieval relevance · Citation correctness</span></div>
              <div className="ecosystem-research-row"><span>Privacy-aware information sharing</span><span>Access-control tests · Access latency · Auditability</span></div>
              <div className="ecosystem-research-row"><span>Cross-module care continuity</span><span>Data completeness · End-to-end workflow time</span></div>
            </div>
            <aside className="ecosystem-research-note"><div className="ecosystem-note-icon"><ClipboardList size={20} /></div><h3>Evidence before claims</h3><p>Compare event detection with a threshold baseline and hospital matching with nearest-facility selection. Report synthetic data as synthetic—not as clinical evidence.</p><div className="ecosystem-baselines"><span>Public datasets</span><span>Synthetic records</span><span>Authorized integrations later</span></div></aside>
          </div>
        </section>

        <section className="ecosystem-safety-section">
          <div className="ecosystem-safety-copy"><span className="ecosystem-eyebrow">Non-negotiable safeguards</span><h2>Privacy and safety are part of the workflow.</h2><p>Health information should only move when the right identity, purpose, permission and audit trail are in place.</p></div>
          <div className="ecosystem-safety-grid">
            {['User- and organization-scoped access', 'Consent-controlled sharing', 'Temporary, audited emergency access', 'Minimum-necessary emergency data', 'Encryption in transit and at rest', 'User-scoped AI retrieval', 'Synthetic data for demonstrations', 'Interoperability designed for future standards'].map((item) => <div key={item}><ShieldCheck size={16} />{item}</div>)}
          </div>
        </section>

        <section className="ecosystem-roadmap-section">
          <div className="ecosystem-section-heading">
            <div><span className="ecosystem-eyebrow">Incremental delivery</span><h2>A practical path from foundation to ecosystem</h2></div>
            <p>Preserve the existing Personal Gateway while adding organizational and emergency capabilities in verifiable stages.</p>
          </div>
          <div className="ecosystem-roadmap">
            {[
              ['01', 'Stabilize personal gateway', 'Multi-user isolation · Consent · Provenance · RAG evaluation'],
              ['02', 'Complete clinical workflows', 'Care teams · EHR · Labs · Pharmacy · Bed and resource readiness'],
              ['03', 'Prototype emergency coordination', 'Sensor datasets · Confirmation · Dispatch simulation · Hospital matching'],
              ['04', 'Connect the modules', 'Identity · Shared API contracts · Event workflow · Record continuity'],
              ['05', 'Harden and evaluate', 'Privacy tests · Load tests · Recovery · Monitoring · Model evaluation'],
            ].map(([number, title, detail]) => <div className="ecosystem-roadmap-item" key={number}><span>{number}</span><div><h3>{title}</h3><p>{detail}</p></div></div>)}
          </div>
        </section>
      </main>
      <footer className="ecosystem-footer"><a className="ecosystem-brand" href="#home"><span className="ecosystem-brand-mark"><HeartPulse size={19} /></span><span><strong>Smart Healthcare</strong><small>AI-assisted · privacy-aware · connected care</small></span></a><span>Prototype · Not for emergency use or clinical decision-making</span></footer>
    </div>
  );
}

function PreviewShell({ children, onBack, title, icon: Icon }: { children: React.ReactNode; onBack: () => void; title: string; icon: typeof Building2 }) {
  return <div className="ecosystem-preview-page">
    <header className="ecosystem-preview-header">
      <button className="ecosystem-back-button" onClick={onBack}><ArrowLeft size={16} /> Ecosystem overview</button>
      <a className="ecosystem-brand" href="#preview"><span className="ecosystem-brand-mark"><HeartPulse size={20} /></span><span><strong>Smart Healthcare</strong><small>Connected care prototype</small></span></a>
      <span className="ecosystem-demo-label"><span className="demo-dot" /> DEMONSTRATION DATA</span>
    </header>
    <main className="ecosystem-preview-content" id="preview">
      <div className="ecosystem-preview-title"><span className="ecosystem-module-icon"><Icon size={23} /></span><div><span className="ecosystem-eyebrow">Unified Healthcare Ecosystem</span><h1>{title}</h1></div></div>
      <div className="ecosystem-preview-disclaimer"><ShieldCheck size={17} /><span>Prototype workspace with fictional sample data. No live patient records, hospital systems, ambulance services or emergency calls are connected.</span></div>
      {children}
    </main>
  </div>;
}

function ClinicalPreview({ onBack, onSelectPersonal }: { onBack: () => void; onSelectPersonal: () => void }) {
  return <PreviewShell onBack={onBack} title="Clinical Intelligence" icon={Stethoscope}>
    <section className="ecosystem-preview-intro"><div><h2>Hospital readiness workspace</h2><p>Coordinate incoming care and review operational readiness across a fictional facility.</p></div><span className="ecosystem-status-pill"><span className="demo-dot" /> SIMULATED FACILITY</span></section>
    <div className="ecosystem-kpi-grid">
      <div className="ecosystem-kpi"><span>Available beds</span><strong>18 <small>/ 42</small></strong><div><BedDouble size={16} /> 4 critical-care · simulated</div></div>
      <div className="ecosystem-kpi"><span>Care team on duty</span><strong>12</strong><div><Users size={16} /> 3 teams · sample data</div></div>
      <div className="ecosystem-kpi"><span>Lab queue</span><strong>07</strong><div><FlaskConical size={16} /> 2 priority · simulated</div></div>
      <div className="ecosystem-kpi"><span>Pharmacy readiness</span><strong>92<small>%</small></strong><div><Pill size={16} /> Inventory snapshot · demo</div></div>
    </div>
    <div className="ecosystem-preview-columns">
      <section className="ecosystem-preview-panel ecosystem-arrival-panel">
        <div className="ecosystem-panel-heading"><div><h3>Incoming care coordination</h3><p>Example of emergency-to-hospital handoff</p></div><span className="ecosystem-status-pill">DEMO EVENT</span></div>
        <div className="ecosystem-arrival-card"><div className="ecosystem-arrival-icon"><Siren size={19} /></div><div><strong>Simulated arrival · Case DEMO-104</strong><span>Example trauma workflow · created for this preview</span></div><span className="ecosystem-arrival-eta"><Clock3 size={15} /> 08 min*</span></div>
        <div className="ecosystem-arrival-context"><strong>Minimum-necessary context preview</strong><p>Emergency profile: available with permission in a real deployment. Clinical details are intentionally not shown in this prototype.</p></div>
        <div className="ecosystem-prep-list"><div><CheckCircle2 size={16} /> Trauma team notified <span>Simulated</span></div><div><CheckCircle2 size={16} /> Resource readiness reviewed <span>Simulated</span></div><div><Clock3 size={16} /> Verified record handoff <span>Not connected</span></div></div>
      </section>
      <section className="ecosystem-preview-panel">
        <div className="ecosystem-panel-heading"><div><h3>Clinical operations</h3><p>Prototype areas for the clinical module</p></div></div>
        <div className="ecosystem-feature-list"><div><Users size={17} /><span><strong>Care team workspaces</strong><small>Doctor and nurse workflows</small></span></div><div><ClipboardList size={17} /><span><strong>Patient & EHR</strong><small>Longitudinal clinical records</small></span></div><div><FlaskConical size={17} /><span><strong>Laboratory & diagnostics</strong><small>Orders, results and provenance</small></span></div><div><Pill size={17} /><span><strong>Pharmacy</strong><small>Prescriptions and fulfillment</small></span></div><div><BedDouble size={17} /><span><strong>Beds & resources</strong><small>Capacity and ICU readiness</small></span></div><div><CalendarDays size={17} /><span><strong>Operational analytics</strong><small>Readiness and workflow measures</small></span></div></div>
      </section>
    </div>
    <div className="ecosystem-preview-next"><div><span className="ecosystem-eyebrow">Continuity of care</span><strong>Connect a verified treatment record to a person-controlled health history.</strong></div><button onClick={onSelectPersonal}>Explore Personal Gateway <ArrowRight size={16} /></button></div>
    <p className="ecosystem-footnote">*Illustrative timing only. This screen does not provide hospital availability, routing, triage or clinical guidance.</p>
  </PreviewShell>;
}

function EmergencyPreview({ onBack, demoStep, setDemoStep }: { onBack: () => void; demoStep: number; setDemoStep: (step: number) => void }) {
  const steps = ['Possible event signal', 'Awaiting user confirmation', 'Demo escalation reviewed', 'Hospital pre-arrival notice'];
  return <PreviewShell onBack={onBack} title="Emergency Intelligence" icon={Siren}>
    <section className="ecosystem-emergency-banner"><div className="ecosystem-emergency-icon"><Siren size={23} /></div><div><span className="ecosystem-status-pill">SIMULATION ONLY · NO LIVE DISPATCH</span><h2>Emergency coordination prototype</h2><p>Illustrates a cautious, multi-step workflow. Sensor signals alone are not proof of an accident, and this prototype cannot contact responders.</p></div></section>
    <div className="ecosystem-emergency-grid">
      <section className="ecosystem-preview-panel ecosystem-event-panel">
        <div className="ecosystem-panel-heading"><div><h3>Example event · DEMO-104</h3><p>Fictional road incident scenario</p></div><span className="ecosystem-status-pill">SYNTHETIC</span></div>
        <div className="ecosystem-signal-grid"><div><Activity size={18} /><span>Motion signal</span><strong>Impact-like*</strong></div><div><HeartPulse size={18} /><span>Wearable</span><strong>Not available</strong></div><div><MapPin size={18} /><span>Location</span><strong>Not collected</strong></div></div>
        <div className="ecosystem-confirmation"><div className="ecosystem-confirmation-symbol"><LockKeyhole size={18} /></div><div><strong>Confirmation before escalation</strong><p>Ask the person to confirm when possible. A real escalation policy must be carefully configured, consent-aware and tested for false positives.</p></div></div>
        <div className="ecosystem-emergency-actions">
          <button className="ecosystem-primary-button" onClick={() => setDemoStep((demoStep + 1) % steps.length)}>Advance demo workflow <ArrowRight size={16} /></button>
          <button className="ecosystem-reset-button" onClick={() => setDemoStep(0)}>Reset example</button>
        </div>
        <p className="ecosystem-footnote">*Illustrative signal only; not generated by a sensor or detection model.</p>
      </section>
      <section className="ecosystem-preview-panel ecosystem-response-panel">
        <div className="ecosystem-panel-heading"><div><h3>Coordination stages</h3><p>Illustrative status for this sample case</p></div></div>
        <div className="ecosystem-stage-list">{steps.map((step, index) => <div className={`ecosystem-stage ${index <= demoStep ? 'complete' : ''} ${index === demoStep ? 'current' : ''}`} key={step}><span className="ecosystem-stage-marker">{index < demoStep ? <CheckCircle2 size={15} /> : index + 1}</span><div><strong>{step}</strong><small>{index < demoStep ? 'Completed in simulation' : index === demoStep ? 'Current demonstration stage' : 'Not started'}</small></div></div>)}</div>
        <div className="ecosystem-hospital-match"><div className="ecosystem-hospital-match-title"><Building2 size={17} /><strong>Capability-aware matching</strong></div><p>In a validated deployment, compare travel time, required care capabilities, available resources and response suitability—not distance alone.</p><div className="ecosystem-match-factors"><span><MapPin size={13} /> ETA</span><span><Stethoscope size={13} /> Capability</span><span><BedDouble size={13} /> Capacity</span></div></div>
        <div className="ecosystem-ambulance-row"><Truck size={18} /><div><strong>Ambulance coordination</strong><span>Dispatch and live tracking are not connected in this preview.</span></div></div>
      </section>
    </div>
    <div className="ecosystem-emergency-privacy"><ShieldCheck size={18} /><p><strong>Emergency data minimization:</strong> a future workflow may share verified critical allergies, conditions, relevant medications and emergency contacts only under appropriate authorization, with access logged.</p></div>
    <p className="ecosystem-no-emergency">If you need emergency help, contact your local emergency services directly. This website is not an emergency service.</p>
  </PreviewShell>;
}
