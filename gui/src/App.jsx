import React, { useState, useEffect } from "react";
import {
  Brain,
  Activity,
  FileText,
  CheckSquare,
  Compass,
  BookOpen,
  Heart,
  Wind,
  Sliders,
  Search,
  Plus,
  Trash2,
  CheckCircle2,
  Circle,
  RefreshCw,
  AlertCircle,
  ArrowRight,
  ChevronRight,
  Download,
  Upload,
  ShieldCheck,
  TrendingUp,
  Sparkles,
  Clock,
  X,
  Flame,
  Trophy,
  Target,
  Layers,
  HelpCircle,
  Eye,
  Smile,
  Zap,
} from "lucide-react";

import {
  fetchStatus,
  fetchEntries,
  createEntry,
  deleteEntry,
  fetchStats,
  fetchDistortions,
  fetchEmotions,
  fetchExperiments,
  createExperiment,
  completeExperiment,
  deleteExperiment,
  fetchTasks,
  createTask,
  completeTask,
  deleteTask,
  fetchLadders,
  createLadder,
  addLadderStep,
  practiceLadderStep,
  deleteLadder,
  deleteExposureStep,
  fetchActions,
  createAction,
  toggleAction,
  deleteAction,
  fetchDasQuestions,
  fetchDasHistory,
  submitDas,
  fetchMethods,
  fetchVerifyAudit,
  evaluateThought,
  fetchBackup,
  restoreBackup,
  triggerSync,
} from "./api";

export default function App() {
  // Navigation
  const [activeTab, setActiveTab] = useState("journal"); // journal | studios | behavioral | tools
  const [studioSubTab, setStudioSubTab] = useState("5col"); // 5col | 3col | decat | wins
  const [behavioralSubTab, setBehavioralSubTab] = useState("experiments"); // experiments | procrastination | ladders | actions
  const [toolsSubTab, setToolsSubTab] = useState("grounding"); // grounding | das | methods | audit

  // Data state
  const [status, setStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [entries, setEntries] = useState([]);
  const [distortionsCatalog, setDistortionsCatalog] = useState([]);
  const [emotionsList, setEmotionsList] = useState([]);
  const [experiments, setExperiments] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [ladders, setLadders] = useState([]);
  const [actions, setActions] = useState([]);

  // UI / Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [distortionFilter, setDistortionFilter] = useState("");
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [notification, setNotification] = useState(null);

  // Quick Action Inline View: null | "checkin"
  const [inlineQuickView, setInlineQuickView] = useState(null);

  const showNotification = (msg) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 4000);
  };

  // Initial Data Load
  const reloadData = async () => {
    try {
      const [st, ent, sts, dist, emo, exp, tsk, lad, act] = await Promise.all([
        fetchStatus().catch(() => null),
        fetchEntries({ q: searchQuery, distortion: distortionFilter }).catch(() => ({ entries: [] })),
        fetchStats().catch(() => null),
        fetchDistortions().catch(() => []),
        fetchEmotions().catch(() => []),
        fetchExperiments().catch(() => []),
        fetchTasks().catch(() => []),
        fetchLadders().catch(() => []),
        fetchActions().catch(() => []),
      ]);
      if (st) setStatus(st);
      if (ent?.entries) setEntries(ent.entries);
      if (sts) setStats(sts);
      if (dist) setDistortionsCatalog(dist);
      if (emo) setEmotionsList(emo);
      if (exp) setExperiments(exp);
      if (tsk) setTasks(tsk);
      if (lad) setLadders(lad);
      if (act) setActions(act);
    } catch (err) {
      console.error("Failed to load initial data", err);
    }
  };

  useEffect(() => {
    reloadData();
  }, [searchQuery, distortionFilter]);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      await triggerSync();
      showNotification("Markdown notes synchronized successfully with vault!");
      reloadData();
    } catch (err) {
      showNotification("Sync failed: " + err.message);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans selection:bg-indigo-600 selection:text-white">
      {/* Toast Notification */}
      {notification && (
        <div className="fixed top-5 right-5 z-50 flex items-center gap-3 bg-indigo-600/95 backdrop-blur-md text-white px-5 py-3 rounded-xl shadow-2xl border border-indigo-400/40 animate-slide-left">
          <Sparkles className="w-5 h-5 text-amber-300 animate-spin" />
          <span className="text-sm font-medium">{notification}</span>
        </div>
      )}

      {/* Primary Sidebar */}
      <aside className="w-64 border-r border-slate-800/80 bg-slate-900/70 flex flex-col justify-between shrink-0 select-none">
        <div>
          {/* Header */}
          <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-600/20">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
                  Leahe <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">CBT</span>
                </h1>
                <p className="text-[11px] text-slate-400 font-medium">David Burns Protocol</p>
              </div>
            </div>
            <button
              onClick={handleSync}
              title="Sync notes with Obsidian vault"
              disabled={isSyncing}
              className={`p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition ${isSyncing ? "animate-spin text-indigo-400" : ""}`}
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {/* Nav Links */}
          <nav className="p-3 space-y-1">
            <NavItem
              active={activeTab === "journal"}
              onClick={() => { setActiveTab("journal"); setInlineQuickView(null); }}
              icon={<FileText className="w-4 h-4" />}
              label="Journal & Timeline"
              badge={entries.length > 0 ? entries.length : null}
            />
            <NavItem
              active={activeTab === "studios"}
              onClick={() => { setActiveTab("studios"); setInlineQuickView(null); }}
              icon={<Sparkles className="w-4 h-4 text-amber-400" />}
              label="Cognitive Studios"
              sub="Reframing & Buster"
            />
            <NavItem
              active={activeTab === "behavioral"}
              onClick={() => { setActiveTab("behavioral"); setInlineQuickView(null); }}
              icon={<Target className="w-4 h-4 text-emerald-400" />}
              label="Behavioral Lab"
              sub="Experiments & Ladders"
            />
            <NavItem
              active={activeTab === "tools"}
              onClick={() => { setActiveTab("tools"); setInlineQuickView(null); }}
              icon={<Compass className="w-4 h-4 text-sky-400" />}
              label="Diagnostics & Aid"
              sub="DAS, Grounding, Audit"
            />
          </nav>
        </div>

        {/* Bottom Status Panel */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Local Engine
            </span>
            <span className="text-[11px] text-slate-500 font-mono">127.0.0.1:14200</span>
          </div>
          {stats && (
            <div className="bg-slate-950/60 rounded-lg p-2.5 border border-slate-800/60 text-[11px] space-y-1">
              <div className="flex justify-between text-slate-300">
                <span>Relief Rate:</span>
                <span className="font-semibold text-emerald-400">+{stats.avg_relief_percent}%</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Mastered Steps:</span>
                <span className="text-slate-200">{stats.exposure_stats?.mastered_steps || 0}</span>
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-950 overflow-hidden relative">
        {/* Top Header Toolbar */}
        <header className="h-14 border-b border-slate-800/80 bg-slate-900/30 backdrop-blur-md px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-sm font-semibold capitalize tracking-wide text-slate-200">
              {activeTab === "journal" && "Clinical Journal & Cognitive Timeline"}
              {activeTab === "studios" && "Cognitive Restructuring Studios"}
              {activeTab === "behavioral" && "Behavioral Activation & Desensitization"}
              {activeTab === "tools" && "Clinical Assessments & Grounding First-Aid"}
            </span>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => {
                setActiveTab("journal");
                setInlineQuickView(inlineQuickView === "checkin" ? null : "checkin");
              }}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition flex items-center gap-1.5 ${
                inlineQuickView === "checkin"
                  ? "bg-indigo-600/20 text-indigo-300 border-indigo-500/50"
                  : "bg-slate-800/60 text-slate-300 border-slate-700/60 hover:bg-slate-700/60"
              }`}
            >
              <Heart className="w-3.5 h-3.5 text-rose-400" />
              Quick Check-in
            </button>

            <button
              onClick={() => {
                setActiveTab("studios");
                setStudioSubTab("5col");
                setInlineQuickView(null);
              }}
              className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              New Thought Record
            </button>
          </div>
        </header>

        {/* Content View Router */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Quick Check-in Inline Studio */}
          {inlineQuickView === "checkin" && (
            <div className="mb-6 animate-fade-in">
              <QuickCheckinStudio
                emotions={emotionsList}
                onSaved={() => {
                  setInlineQuickView(null);
                  showNotification("Quick check-in logged to timeline!");
                  reloadData();
                }}
                onCancel={() => setInlineQuickView(null)}
              />
            </div>
          )}

          {/* TAB 1: JOURNAL */}
          {activeTab === "journal" && (
            <JournalView
              entries={entries}
              distortions={distortionsCatalog}
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              distortionFilter={distortionFilter}
              setDistortionFilter={setDistortionFilter}
              onSelectEntry={(entry) => setSelectedEntry(entry)}
              onDeleteEntry={async (id) => {
                await deleteEntry(id);
                showNotification("Entry removed from record.");
                reloadData();
                if (selectedEntry?.id === id) setSelectedEntry(null);
              }}
              onOpenNewRecord={() => {
                setActiveTab("studios");
                setStudioSubTab("5col");
              }}
              onOpen3Column={() => {
                setActiveTab("studios");
                setStudioSubTab("3col");
              }}
            />
          )}

          {/* TAB 2: COGNITIVE STUDIOS */}
          {activeTab === "studios" && (
            <CognitiveStudiosView
              subTab={studioSubTab}
              setSubTab={setStudioSubTab}
              distortions={distortionsCatalog}
              emotions={emotionsList}
              onRecordSaved={(msg) => {
                showNotification(msg || "Cognitive exercise saved successfully!");
                reloadData();
                setActiveTab("journal");
              }}
            />
          )}

          {/* TAB 3: BEHAVIORAL ACTIVATION */}
          {activeTab === "behavioral" && (
            <BehavioralLabView
              subTab={behavioralSubTab}
              setSubTab={setBehavioralSubTab}
              experiments={experiments}
              tasks={tasks}
              ladders={ladders}
              actions={actions}
              onRefresh={reloadData}
              showNotification={showNotification}
            />
          )}

          {/* TAB 4: DIAGNOSTICS & FIRST-AID */}
          {activeTab === "tools" && (
            <DiagnosticsAndAidView
              subTab={toolsSubTab}
              setSubTab={setToolsSubTab}
              showNotification={showNotification}
              onRefresh={reloadData}
            />
          )}
        </div>

        {/* Slide-over Detail Drawer */}
        {selectedEntry && (
          <EntryDetailDrawer
            entry={selectedEntry}
            onClose={() => setSelectedEntry(null)}
            onDelete={async () => {
              await deleteEntry(selectedEntry.id);
              setSelectedEntry(null);
              showNotification("Record deleted.");
              reloadData();
            }}
          />
        )}
      </main>
    </div>
  );
}

// -------------------------------------------------------------
// Sub-Components & Navigation
// -------------------------------------------------------------

function NavItem({ active, onClick, icon, label, sub, badge }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left transition group ${
        active
          ? "bg-indigo-600/15 text-indigo-300 font-medium border border-indigo-500/30"
          : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
      }`}
    >
      <div className="flex items-center gap-3 min-w-0">
        <span className={`${active ? "text-indigo-400" : "text-slate-400 group-hover:text-slate-200"}`}>{icon}</span>
        <div className="truncate">
          <div className="text-xs truncate">{label}</div>
          {sub && <div className="text-[10px] text-slate-500 font-normal truncate">{sub}</div>}
        </div>
      </div>
      {badge !== null && badge !== undefined && (
        <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700 font-mono">
          {badge}
        </span>
      )}
    </button>
  );
}

// -------------------------------------------------------------
// TAB 1: JOURNAL VIEW
// -------------------------------------------------------------
function JournalView({
  entries,
  distortions,
  searchQuery,
  setSearchQuery,
  distortionFilter,
  setDistortionFilter,
  onSelectEntry,
  onDeleteEntry,
  onOpenNewRecord,
  onOpen3Column,
}) {
  return (
    <div className="space-y-5 max-w-6xl mx-auto">
      {/* Search & Distortion Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search situations, thoughts, reframes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-transparent text-xs text-slate-200 placeholder-slate-500 focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={distortionFilter}
            onChange={(e) => setDistortionFilter(e.target.value)}
            className="bg-slate-800 text-slate-300 text-xs rounded-lg px-3 py-1.5 border border-slate-700/80 focus:outline-none"
          >
            <option value="">All Distortions ({distortions.length})</option>
            {distortions.map((d) => (
              <option key={d.code} value={d.name}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Entries List or Empty State */}
      {entries.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl bg-slate-900/20">
          <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto mb-4 border border-indigo-500/20">
            <Brain className="w-7 h-7" />
          </div>
          <h3 className="text-base font-semibold text-slate-200 mb-1">No Entries Found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-6">
            Log negative automatic thoughts to dismantle cognitive distortions using rational restructuring.
          </p>
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={onOpenNewRecord}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition"
            >
              5-Step Thought Record
            </button>
            <button
              onClick={onOpen3Column}
              className="px-4 py-2 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              Rapid 3-Column Buster
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {entries.map((entry) => (
            <div
              key={entry.id}
              onClick={() => onSelectEntry(entry)}
              className="group p-4 rounded-xl bg-slate-900/60 hover:bg-slate-800/70 border border-slate-800/80 hover:border-indigo-500/40 transition cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-2">
                  <span className="font-mono">{entry.timestamp?.slice(0, 16).replace("T", " ")}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                    entry.entry_type === "cbt_record"
                      ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                      : "bg-slate-800 text-slate-400"
                  }`}>
                    {entry.entry_type === "cbt_record" ? "CBT Record" : entry.entry_type}
                  </span>
                </div>

                <div className="mb-3">
                  <div className="text-[11px] text-slate-400 font-medium">Automatic Thought:</div>
                  <p className="text-xs font-semibold text-slate-200 line-clamp-2 mt-0.5">
                    "{entry.automatic_thought || entry.situation || "Quick emotional check-in"}"
                  </p>
                </div>

                {entry.distortions?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {entry.distortions.slice(0, 2).map((d, idx) => (
                      <span
                        key={idx}
                        className="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20"
                      >
                        {d}
                      </span>
                    ))}
                    {entry.distortions.length > 2 && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                        +{entry.distortions.length - 2}
                      </span>
                    )}
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Mood:</span>
                  <span className="font-semibold text-slate-300">{entry.initial_mood}/10</span>
                  {entry.final_mood !== null && entry.final_mood !== undefined && (
                    <>
                      <ArrowRight className="w-3 h-3 text-slate-500" />
                      <span className="font-semibold text-emerald-400">{entry.final_mood}/10</span>
                    </>
                  )}
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm("Delete this entry?")) onDeleteEntry(entry.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 transition p-1"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// -------------------------------------------------------------
// TAB 2: COGNITIVE STUDIOS (5-Column, 3-Column, Decatastrophizing, Wins)
// -------------------------------------------------------------
function CognitiveStudiosView({ subTab, setSubTab, distortions, emotions, onRecordSaved }) {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Studio Tab Pills */}
      <div className="flex border-b border-slate-800 pb-3 gap-2">
        <button
          onClick={() => setSubTab("5col")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "5col"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          5-Step Restructuring Studio
        </button>
        <button
          onClick={() => setSubTab("3col")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "3col"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Rapid 3-Column Buster
        </button>
        <button
          onClick={() => setSubTab("decat")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "decat"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Decatastrophizing Drill
        </button>
        <button
          onClick={() => setSubTab("wins")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "wins"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Positive Data Log (Wins)
        </button>
      </div>

      {subTab === "5col" && (
        <FiveStepStudio distortions={distortions} emotions={emotions} onSaved={onRecordSaved} />
      )}
      {subTab === "3col" && (
        <ThreeColumnStudio distortions={distortions} onSaved={onRecordSaved} />
      )}
      {subTab === "decat" && (
        <DecatastrophizingStudio onSaved={onRecordSaved} />
      )}
      {subTab === "wins" && (
        <WinsStudio onSaved={onRecordSaved} />
      )}
    </div>
  );
}

// 1. 5-Step Restructuring Studio with Real-time Thought Quality Evaluator
function FiveStepStudio({ distortions, emotions, onSaved }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    situation: "",
    initial_mood: 4,
    primary_emotion: "Anxious",
    emotion_intensity_initial: 75,
    automatic_thought: "",
    belief_initial: 85,
    distortions: [],
    evidence_for: "",
    evidence_against: "",
    alternative_thought: "",
    belief_final: 80,
    final_mood: 7,
    emotion_intensity_final: 25,
    action_plan: "",
  });

  const [qualityReport, setQualityReport] = useState(null);
  const [isEvaluating, setIsEvaluating] = useState(false);

  const toggleDistortion = (name) => {
    setForm((prev) => ({
      ...prev,
      distortions: prev.distortions.includes(name)
        ? prev.distortions.filter((d) => d !== name)
        : [...prev.distortions, name],
    }));
  };

  const handleEvaluate = async () => {
    if (!form.automatic_thought || !form.alternative_thought) return;
    setIsEvaluating(true);
    try {
      const rep = await evaluateThought({
        automatic_thought: form.automatic_thought,
        alternative_thought: form.alternative_thought,
        belief_final: form.belief_final,
        belief_initial: form.belief_initial,
        distortions: form.distortions,
      });
      setQualityReport(rep);
    } catch (err) {
      console.error(err);
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleSubmit = async () => {
    await createEntry({
      ...form,
      entry_type: "cbt_record",
    });
    onSaved("5-Step Thought Record completed & saved!");
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-xl">
      {/* Step Indicators */}
      <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-800">
        {[
          "1. Situation & Mood",
          "2. Negative Thought",
          "3. Cognitive Distortions",
          "4. Evidence Exam",
          "5. Rational Reframe",
        ].map((title, idx) => (
          <div
            key={idx}
            className={`text-xs font-semibold ${
              step === idx + 1
                ? "text-indigo-400 border-b-2 border-indigo-500 pb-1"
                : step > idx + 1
                ? "text-emerald-400"
                : "text-slate-600"
            }`}
          >
            {title}
          </div>
        ))}
      </div>

      {/* Step 1 */}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Situation (Where were you? What triggered distress?)
            </label>
            <textarea
              rows={3}
              value={form.situation}
              onChange={(e) => setForm({ ...form, situation: e.target.value })}
              placeholder="e.g., Preparing to send client presentation email..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Primary Emotion</label>
              <select
                value={form.primary_emotion}
                onChange={(e) => setForm({ ...form, primary_emotion: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {emotions.length > 0 ? (
                  emotions.map((em, i) => (
                    <option key={i} value={typeof em === "string" ? em : em.name}>
                      {typeof em === "string" ? em : em.name}
                    </option>
                  ))
                ) : (
                  <>
                    <option value="Anxious">Anxious</option>
                    <option value="Sad">Sad</option>
                    <option value="Frustrated">Frustrated</option>
                    <option value="Guilty">Guilty</option>
                    <option value="Hopeless">Hopeless</option>
                  </>
                )}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Initial Mood: <span className="font-bold text-indigo-400">{form.initial_mood}/10</span>
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={form.initial_mood}
                onChange={(e) => setForm({ ...form, initial_mood: Number(e.target.value) })}
                className="w-full accent-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Step 2 */}
      {step === 2 && (
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Automatic Negative Thought (What exact sentence went through your mind?)
            </label>
            <textarea
              rows={3}
              value={form.automatic_thought}
              onChange={(e) => setForm({ ...form, automatic_thought: e.target.value })}
              placeholder="e.g., I'm going to look incompetent and they'll regret hiring me."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              How strongly do you believe this thought right now? <span className="font-bold text-indigo-400">{form.belief_initial}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={form.belief_initial}
              onChange={(e) => setForm({ ...form, belief_initial: Number(e.target.value) })}
              className="w-full accent-indigo-500"
            />
          </div>
        </div>
      )}

      {/* Step 3 */}
      {step === 3 && (
        <div className="space-y-3">
          <label className="block text-xs font-medium text-slate-300 mb-1">
            Identify Cognitive Distortions (Select all that apply)
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-72 overflow-y-auto p-1">
            {distortions.map((d) => {
              const active = form.distortions.includes(d.name);
              return (
                <button
                  key={d.code}
                  type="button"
                  onClick={() => toggleDistortion(d.name)}
                  className={`p-2.5 rounded-xl text-left border text-xs transition ${
                    active
                      ? "bg-indigo-600/20 border-indigo-500 text-indigo-200 font-medium"
                      : "bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700"
                  }`}
                >
                  <div className="font-semibold text-[11px]">{d.name}</div>
                  <div className="text-[10px] text-slate-500 line-clamp-1">{d.description}</div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Step 4 */}
      {step === 4 && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Evidence FOR this thought (Objective facts only)
              </label>
              <textarea
                rows={4}
                value={form.evidence_for}
                onChange={(e) => setForm({ ...form, evidence_for: e.target.value })}
                placeholder="Facts that support the concern..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Evidence AGAINST this thought (Counter-facts & context)
              </label>
              <textarea
                rows={4}
                value={form.evidence_against}
                onChange={(e) => setForm({ ...form, evidence_against: e.target.value })}
                placeholder="Facts proving this thought is exaggerated..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Step 5 */}
      {step === 5 && (
        <div className="space-y-5">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-medium text-slate-300">
                Rational Reframe / Alternative Response (Realistic & convincing)
              </label>
              <button
                type="button"
                onClick={handleEvaluate}
                disabled={isEvaluating || !form.alternative_thought}
                className="text-[11px] font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
              >
                <Zap className="w-3 h-3 text-amber-400" />
                {isEvaluating ? "Checking Quality..." : "Run Burns Quality Check"}
              </button>
            </div>
            <textarea
              rows={3}
              value={form.alternative_thought}
              onChange={(e) => setForm({ ...form, alternative_thought: e.target.value })}
              placeholder="e.g., I've prepared carefully. Minor typos don't equal incompetence, and asking questions is part of the job."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Real-time Quality Checker Report */}
          {qualityReport && (
            <div className="p-4 rounded-xl bg-slate-950/80 border border-indigo-500/30 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  Burns Thought Quality Rating:
                </span>
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                  qualityReport.rating === "EXCELLENT"
                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                    : "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                }`}>
                  {qualityReport.rating} ({qualityReport.overall_score}/100)
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800 text-[11px]">
                {qualityReport.checks?.map((c, i) => (
                  <div key={i} className="flex items-center gap-1.5 text-slate-300">
                    {c.passed ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    ) : (
                      <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                    )}
                    <span>{c.criterion_name}: {c.passed ? "Passed" : "Needs work"}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Belief in Rational Reframe: <span className="font-bold text-emerald-400">{form.belief_final}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={form.belief_final}
                onChange={(e) => setForm({ ...form, belief_final: Number(e.target.value) })}
                className="w-full accent-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Final Mood: <span className="font-bold text-emerald-400">{form.final_mood}/10</span>
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={form.final_mood}
                onChange={(e) => setForm({ ...form, final_mood: Number(e.target.value) })}
                className="w-full accent-emerald-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between mt-8 pt-4 border-t border-slate-800">
        {step > 1 ? (
          <button
            type="button"
            onClick={() => setStep(step - 1)}
            className="px-4 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
          >
            Previous
          </button>
        ) : <div />}

        {step < 5 ? (
          <button
            type="button"
            onClick={() => setStep(step + 1)}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center gap-1.5"
          >
            Next Step <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            type="button"
            onClick={handleSubmit}
            className="px-6 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-lg shadow-emerald-600/30 flex items-center gap-1.5"
          >
            <CheckCircle2 className="w-4 h-4" /> Save Record
          </button>
        )}
      </div>
    </div>
  );
}

// 2. Rapid Burns 3-Column Buster
function ThreeColumnStudio({ distortions, onSaved }) {
  const [automaticThought, setAutomaticThought] = useState("");
  const [selectedDistortions, setSelectedDistortions] = useState([]);
  const [rationalResponse, setRationalResponse] = useState("");

  const toggleDist = (name) => {
    setSelectedDistortions((prev) =>
      prev.includes(name) ? prev.filter((d) => d !== name) : [...prev, name]
    );
  };

  const handleSave = async () => {
    if (!automaticThought || !rationalResponse) return;
    await createEntry({
      entry_type: "cbt_record",
      automatic_thought: automaticThought,
      distortions: selectedDistortions,
      alternative_thought: rationalResponse,
      initial_mood: 4,
      final_mood: 7,
      belief_initial: 85,
      belief_final: 85,
    });
    onSaved("Rapid 3-Column Buster saved!");
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
      <div>
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-400" />
          Burns Triple-Column Technique
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Rapid refutation protocol: Automatic Thought $\to$ Cognitive Distortions $\to$ Rational Response.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Column 1 */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <div className="text-xs font-bold text-rose-400 mb-1">Column 1: Automatic Thought</div>
            <p className="text-[11px] text-slate-500 mb-2">Write down the negative self-critical phrase.</p>
            <textarea
              rows={6}
              value={automaticThought}
              onChange={(e) => setAutomaticThought(e.target.value)}
              placeholder="e.g. I never do anything right, I ruined the whole weekend."
              className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
            />
          </div>
        </div>

        {/* Column 2 */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <div className="text-xs font-bold text-amber-400 mb-1">Column 2: Distortions</div>
            <p className="text-[11px] text-slate-500 mb-2">Select the thinking flaws present.</p>
            <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
              {distortions.map((d) => (
                <button
                  key={d.code}
                  type="button"
                  onClick={() => toggleDist(d.name)}
                  className={`w-full text-left px-2.5 py-1.5 rounded-lg text-[11px] border transition ${
                    selectedDistortions.includes(d.name)
                      ? "bg-amber-500/20 text-amber-300 border-amber-500/40 font-medium"
                      : "bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  {d.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Column 3 */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <div className="text-xs font-bold text-emerald-400 mb-1">Column 3: Rational Response</div>
            <p className="text-[11px] text-slate-500 mb-2">Formulate a fact-based, objective answer.</p>
            <textarea
              rows={6}
              value={rationalResponse}
              onChange={(e) => setRationalResponse(e.target.value)}
              placeholder="e.g. 'Never' is an overgeneralization. I handled chores and grocery shopping well; only one plan got postponed."
              className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-3">
        <button
          onClick={handleSave}
          disabled={!automaticThought || !rationalResponse}
          className="px-6 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition disabled:opacity-50"
        >
          Save 3-Column Buster
        </button>
      </div>
    </div>
  );
}

// 3. Decatastrophizing Drill-down (Burns' 4-Question Method)
function DecatastrophizingStudio({ onSaved }) {
  const [fear, setFear] = useState("");
  const [worstCase, setWorstCase] = useState("");
  const [bestCase, setBestCase] = useState("");
  const [likelyOutcome, setLikelyOutcome] = useState("");
  const [copingPlan, setCopingPlan] = useState("");

  const handleSave = async () => {
    if (!fear || !copingPlan) return;
    const reframe = `Worst Case: ${worstCase} | Best Case: ${bestCase} | Most Likely: ${likelyOutcome} | Coping Plan: ${copingPlan}`;
    await createEntry({
      entry_type: "cbt_record",
      situation: "Decatastrophizing Drill: " + fear,
      automatic_thought: "Catastrophic fear: " + fear,
      distortions: ["Catastrophizing", "Fortune Telling"],
      alternative_thought: reframe,
      initial_mood: 3,
      final_mood: 7,
      belief_initial: 90,
      belief_final: 85,
    });
    onSaved("Decatastrophizing protocol saved to clinical record!");
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
      <div>
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Flame className="w-4 h-4 text-orange-400" />
          Burns Decatastrophizing Protocol ("What If?")
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          De-escalate catastrophic anxiety by systematically breaking down worst, best, and realistic scenarios.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">
            1. What is the catastrophic fear?
          </label>
          <input
            type="text"
            value={fear}
            onChange={(e) => setFear(e.target.value)}
            placeholder="e.g., If I freeze during the interview, my entire career will be over."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-rose-400 mb-1">
              2. What is the absolute WORST that could happen?
            </label>
            <textarea
              rows={3}
              value={worstCase}
              onChange={(e) => setWorstCase(e.target.value)}
              placeholder="The absolute worst case scenario realistically..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-emerald-400 mb-1">
              3. What is the BEST possible outcome?
            </label>
            <textarea
              rows={3}
              value={bestCase}
              onChange={(e) => setBestCase(e.target.value)}
              placeholder="The ideal, optimistic outcome..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-amber-400 mb-1">
            4. What is the MOST LIKELY realistic outcome?
          </label>
          <textarea
            rows={2}
            value={likelyOutcome}
            onChange={(e) => setLikelyOutcome(e.target.value)}
            placeholder="Based on past evidence, what actually tends to happen?"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-indigo-400 mb-1">
            5. Concrete Coping Plan (If the worst happened, how would you survive and adapt?)
          </label>
          <textarea
            rows={3}
            value={copingPlan}
            onChange={(e) => setCopingPlan(e.target.value)}
            placeholder="I would take a breath, excuse myself for water, and remember there are dozens of other opportunities..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      <div className="flex justify-end pt-3">
        <button
          onClick={handleSave}
          disabled={!fear || !copingPlan}
          className="px-6 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition disabled:opacity-50"
        >
          Save Decatastrophizing Drill
        </button>
      </div>
    </div>
  );
}

// 4. Positive Data Log (Wins / Counter-Evidence)
function WinsStudio({ onSaved }) {
  const [winTitle, setWinTitle] = useState("");
  const [beliefSupported, setBeliefSupported] = useState("");

  const handleSave = async () => {
    if (!winTitle) return;
    await createEntry({
      entry_type: "quick",
      primary_emotion: "Accomplished",
      emotion_intensity_initial: 85,
      initial_mood: 8,
      situation: "Positive Data Log: " + winTitle,
      alternative_thought: "Counter-evidence: " + (beliefSupported || "Reinforces confidence and capability."),
    });
    onSaved("Positive Data Log entry recorded!");
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
      <div>
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Trophy className="w-4 h-4 text-amber-400" />
          Positive Data Log (Credit & Evidence)
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Depression filters out achievements. Record positive data and small wins to rebuild an objective self-schema.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">
            Accomplishment or Small Win
          </label>
          <input
            type="text"
            value={winTitle}
            onChange={(e) => setWinTitle(e.target.value)}
            placeholder="e.g., Finished the report draft, exercised for 20 minutes despite low motivation."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">
            What negative belief does this disprove?
          </label>
          <textarea
            rows={3}
            value={beliefSupported}
            onChange={(e) => setBeliefSupported(e.target.value)}
            placeholder="e.g. Disproves 'I am lazy and unable to focus'. Shows that taking small steps overcomes inertia."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      <div className="flex justify-end pt-3">
        <button
          onClick={handleSave}
          disabled={!winTitle}
          className="px-6 py-2 rounded-xl text-xs font-semibold bg-amber-600 hover:bg-amber-500 text-white transition disabled:opacity-50"
        >
          Log Positive Win
        </button>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// TAB 3: BEHAVIORAL ACTIVATION LAB
// -------------------------------------------------------------
function BehavioralLabView({
  subTab,
  setSubTab,
  experiments,
  tasks,
  ladders,
  actions,
  onRefresh,
  showNotification,
}) {
  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Sub Tabs */}
      <div className="flex border-b border-slate-800 pb-3 gap-2">
        <button
          onClick={() => setSubTab("experiments")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "experiments"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Behavioral Experiments ({experiments.length})
        </button>
        <button
          onClick={() => setSubTab("procrastination")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "procrastination"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Anti-Procrastination Sheet ({tasks.length})
        </button>
        <button
          onClick={() => setSubTab("ladders")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "ladders"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Exposure Ladders ({ladders.length})
        </button>
        <button
          onClick={() => setSubTab("actions")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "actions"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Action Items ({actions.length})
        </button>
      </div>

      {subTab === "experiments" && (
        <ExperimentsManager
          experiments={experiments}
          onRefresh={onRefresh}
          showNotification={showNotification}
        />
      )}
      {subTab === "procrastination" && (
        <ProcrastinationManager
          tasks={tasks}
          onRefresh={onRefresh}
          showNotification={showNotification}
        />
      )}
      {subTab === "ladders" && (
        <LaddersManager
          ladders={ladders}
          onRefresh={onRefresh}
          showNotification={showNotification}
        />
      )}
      {subTab === "actions" && (
        <ActionsManager
          actions={actions}
          onRefresh={onRefresh}
          showNotification={showNotification}
        />
      )}
    </div>
  );
}

// Behavioral Experiments Manager
function ExperimentsManager({ experiments, onRefresh, showNotification }) {
  const [creating, setCreating] = useState(false);
  const [completingId, setCompletingId] = useState(null);

  // New experiment form
  const [title, setTitle] = useState("");
  const [fearPrediction, setFearPrediction] = useState("");
  const [predictedBelief, setPredictedBelief] = useState(80);
  const [experimentPlan, setExperimentPlan] = useState("");

  // Complete form
  const [actualOutcome, setActualOutcome] = useState("");
  const [fearRealized, setFearRealized] = useState(false);
  const [conclusion, setConclusion] = useState("");

  const handleCreate = async () => {
    if (!title || !fearPrediction) return;
    await createExperiment({
      title,
      fear_prediction: fearPrediction,
      predicted_belief: predictedBelief,
      experiment_plan: experimentPlan,
    });
    setCreating(false);
    setTitle("");
    setFearPrediction("");
    setExperimentPlan("");
    showNotification("Behavioral experiment hypothesis created!");
    onRefresh();
  };

  const handleComplete = async (id) => {
    if (!actualOutcome) return;
    await completeExperiment(id, {
      actual_outcome: actualOutcome,
      actual_severity: fearRealized ? 50 : 10,
      fear_realized: fearRealized,
      conclusion,
    });
    setCompletingId(null);
    setActualOutcome("");
    setConclusion("");
    showNotification("Experiment completed and analyzed!");
    onRefresh();
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-sm font-semibold text-slate-200">
          Empirical Hypothesis Testing (Fear vs Reality)
        </h3>
        <button
          onClick={() => setCreating(!creating)}
          className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center gap-1.5"
        >
          <Plus className="w-3.5 h-3.5" />
          New Experiment
        </button>
      </div>

      {creating && (
        <div className="bg-slate-900/80 border border-indigo-500/30 rounded-2xl p-5 space-y-4">
          <div className="text-xs font-bold text-indigo-300">New Behavioral Experiment</div>
          <input
            type="text"
            placeholder="Experiment title (e.g. Asking for clarification in group meeting)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
          />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Negative Fear Prediction</label>
              <textarea
                rows={2}
                placeholder="What do you predict will go wrong?"
                value={fearPrediction}
                onChange={(e) => setFearPrediction(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">
                Predicted Belief: <span className="text-indigo-400 font-bold">{predictedBelief}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={predictedBelief}
                onChange={(e) => setPredictedBelief(Number(e.target.value))}
                className="w-full accent-indigo-500 mt-2"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Experiment Plan (What will you do?)</label>
            <input
              type="text"
              placeholder="e.g. Raise hand in Q&A and ask one question."
              value={experimentPlan}
              onChange={(e) => setExperimentPlan(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setCreating(false)}
              className="px-4 py-1.5 text-xs rounded-lg bg-slate-800 text-slate-400"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white"
            >
              Save Experiment
            </button>
          </div>
        </div>
      )}

      {/* Experiments List */}
      {experiments.length === 0 ? (
        <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
          No behavioral experiments yet. Create one to test catastrophic predictions against reality!
        </div>
      ) : (
        <div className="space-y-3">
          {experiments.map((exp) => (
            <div
              key={exp.id}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col gap-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${exp.is_completed ? "bg-emerald-500" : "bg-amber-500"}`} />
                  <span className="text-xs font-bold text-slate-200">{exp.title}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                    exp.is_completed ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                  }`}>
                    {exp.status.toUpperCase()}
                  </span>
                  <button
                    onClick={async () => {
                      if (confirm("Delete this experiment?")) {
                        await deleteExperiment(exp.id);
                        showNotification("Experiment deleted");
                        onRefresh();
                      }
                    }}
                    className="text-slate-500 hover:text-rose-400 p-1"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs bg-slate-950/40 p-3 rounded-lg border border-slate-800/40">
                <div>
                  <span className="text-slate-400">Prediction ({exp.predicted_belief}% belief):</span>
                  <p className="text-slate-300 font-medium mt-0.5">{exp.fear_prediction}</p>
                </div>
                <div>
                  <span className="text-slate-400">Plan:</span>
                  <p className="text-slate-300 font-medium mt-0.5">{exp.experiment_plan}</p>
                </div>
              </div>

              {exp.is_completed ? (
                <div className="bg-emerald-950/20 border border-emerald-500/20 p-3 rounded-lg text-xs space-y-1">
                  <div className="text-emerald-400 font-semibold">Actual Outcome:</div>
                  <p className="text-slate-200">{exp.actual_outcome}</p>
                  {exp.conclusion && (
                    <p className="text-slate-400 text-[11px] pt-1">
                      <span className="font-medium text-slate-300">Conclusion:</span> {exp.conclusion}
                    </p>
                  )}
                </div>
              ) : completingId === exp.id ? (
                <div className="bg-slate-950 p-4 rounded-xl border border-indigo-500/30 space-y-3">
                  <div className="text-xs font-semibold text-indigo-300">Record Experiment Outcome</div>
                  <textarea
                    rows={2}
                    placeholder="What actually occurred when you executed the experiment?"
                    value={actualOutcome}
                    onChange={(e) => setActualOutcome(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                  />
                  <div className="flex items-center gap-4 text-xs">
                    <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                      <input
                        type="checkbox"
                        checked={fearRealized}
                        onChange={(e) => setFearRealized(e.target.checked)}
                        className="rounded accent-rose-500"
                      />
                      Fear was realized
                    </label>
                  </div>
                  <input
                    type="text"
                    placeholder="Conclusion / Takeaway (What did you learn?)"
                    value={conclusion}
                    onChange={(e) => setConclusion(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                  />
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => setCompletingId(null)}
                      className="px-3 py-1 text-xs rounded bg-slate-800 text-slate-400"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleComplete(exp.id)}
                      className="px-3 py-1 text-xs font-semibold rounded bg-emerald-600 text-white"
                    >
                      Finish Experiment
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setCompletingId(exp.id)}
                  className="self-start px-3 py-1 text-xs rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition"
                >
                  Log Result & Outcome
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Anti-Procrastination Sheet Manager
function ProcrastinationManager({ tasks, onRefresh, showNotification }) {
  const [taskName, setTaskName] = useState("");
  const [predDiff, setPredDiff] = useState(70);
  const [predPlea, setPredPlea] = useState(30);

  const [completingId, setCompletingId] = useState(null);
  const [actDiff, setActDiff] = useState(40);
  const [actPlea, setActPlea] = useState(70);

  const handleCreate = async () => {
    if (!taskName) return;
    await createTask({
      task_name: taskName,
      predicted_difficulty: predDiff,
      predicted_pleasure: predPlea,
    });
    setTaskName("");
    showNotification("Task registered in Anti-Procrastination sheet!");
    onRefresh();
  };

  const handleComplete = async (id) => {
    await completeTask(id, {
      actual_difficulty: actDiff,
      actual_pleasure: actPlea,
    });
    setCompletingId(null);
    showNotification("Task completed and difficulty delta recorded!");
    onRefresh();
  };

  return (
    <div className="space-y-5">
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
        <div className="text-xs font-bold text-slate-200">Add Anti-Procrastination Task</div>
        <p className="text-[11px] text-slate-400">
          We procrastinate because we overestimate the pain/difficulty and underestimate the pleasure. Predict both before starting!
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            type="text"
            placeholder="Task description (e.g. Open tax folder and organize receipts)"
            value={taskName}
            onChange={(e) => setTaskName(e.target.value)}
            className="md:col-span-1 bg-slate-950 border border-slate-800 rounded-xl p-2 text-xs text-slate-200"
          />
          <div>
            <label className="text-[10px] text-slate-400">Predicted Difficulty: {predDiff}%</label>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={predDiff}
              onChange={(e) => setPredDiff(Number(e.target.value))}
              className="w-full accent-rose-500"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-400">Predicted Pleasure: {predPlea}%</label>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={predPlea}
              onChange={(e) => setPredPlea(Number(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>
        </div>
        <button
          onClick={handleCreate}
          disabled={!taskName}
          className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition disabled:opacity-50"
        >
          Add Task
        </button>
      </div>

      {tasks.length === 0 ? (
        <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
          No tasks logged yet. Add a task above to test your anticipation against reality!
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((t) => (
            <div
              key={t.id}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${t.status === "completed" ? "bg-emerald-500" : "bg-amber-500"}`} />
                  <span className="text-xs font-bold text-slate-200">{t.task_name}</span>
                </div>
                <div className="text-[11px] text-slate-400 flex gap-4">
                  <span>Pred. Diff: <b className="text-slate-300">{t.predicted_difficulty}%</b></span>
                  <span>Pred. Pleasure: <b className="text-slate-300">{t.predicted_pleasure}%</b></span>
                  {t.status === "completed" && (
                    <>
                      <span>Actual Diff: <b className="text-emerald-400">{t.actual_difficulty}%</b></span>
                      <span>Actual Pleasure: <b className="text-emerald-400">{t.actual_pleasure}%</b></span>
                    </>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 self-end md:self-auto">
                {t.status === "completed" ? (
                  <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    Done
                  </span>
                ) : completingId === t.id ? (
                  <div className="flex items-center gap-2 bg-slate-950 p-2 rounded-xl border border-indigo-500/30">
                    <div className="text-[10px]">
                      <span>Diff: {actDiff}%</span>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={actDiff}
                        onChange={(e) => setActDiff(Number(e.target.value))}
                        className="w-16 accent-rose-500 block"
                      />
                    </div>
                    <div className="text-[10px]">
                      <span>Plea: {actPlea}%</span>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={actPlea}
                        onChange={(e) => setActPlea(Number(e.target.value))}
                        className="w-16 accent-emerald-500 block"
                      />
                    </div>
                    <button
                      onClick={() => handleComplete(t.id)}
                      className="px-2 py-1 text-[11px] bg-emerald-600 rounded text-white font-semibold"
                    >
                      Save
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setCompletingId(t.id)}
                    className="px-3 py-1 text-xs rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
                  >
                    Log Completion
                  </button>
                )}

                <button
                  onClick={async () => {
                    if (confirm("Delete this task?")) {
                      await deleteTask(t.id);
                      showNotification("Task deleted");
                      onRefresh();
                    }
                  }}
                  className="text-slate-500 hover:text-rose-400 p-1"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Exposure Ladders & Steps Manager
function LaddersManager({ ladders, onRefresh, showNotification }) {
  const [fearTheme, setFearTheme] = useState("");
  const [addingStepLadderId, setAddingStepLadderId] = useState(null);
  const [stepDesc, setStepDesc] = useState("");
  const [stepSuds, setStepSuds] = useState(50);

  const [practicingStepId, setPracticingStepId] = useState(null);
  const [preSuds, setPreSuds] = useState(70);
  const [postSuds, setPostSuds] = useState(25);

  const handleCreateLadder = async () => {
    if (!fearTheme) return;
    await createLadder({ fear_theme: fearTheme });
    setFearTheme("");
    showNotification("Exposure ladder created!");
    onRefresh();
  };

  const handleAddStep = async (ladderId) => {
    if (!stepDesc) return;
    await addLadderStep(ladderId, {
      description: stepDesc,
      target_suds: stepSuds,
      step_order: 1,
    });
    setAddingStepLadderId(null);
    setStepDesc("");
    showNotification("Exposure step added to hierarchy!");
    onRefresh();
  };

  const handlePractice = async (stepId) => {
    await practiceLadderStep(stepId, {
      pre_suds: preSuds,
      post_suds: postSuds,
    });
    setPracticingStepId(null);
    showNotification("Exposure practice session recorded!");
    onRefresh();
  };

  return (
    <div className="space-y-5">
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
        <div className="text-xs font-bold text-slate-200">New Exposure Ladder (Desensitization Hierarchy)</div>
        <p className="text-[11px] text-slate-400">
          Break down overwhelming phobias and social anxieties into graduated steps ranked by SUDS (Subjective Units of Distress, 0-100).
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Fear theme (e.g. Social Phobia, Agoraphobia, Public Speaking)"
            value={fearTheme}
            onChange={(e) => setFearTheme(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl p-2 text-xs text-slate-200"
          />
          <button
            onClick={handleCreateLadder}
            disabled={!fearTheme}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white transition disabled:opacity-50"
          >
            Create Ladder
          </button>
        </div>
      </div>

      {ladders.length === 0 ? (
        <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
          No exposure ladders yet. Create a ladder above to begin systematic desensitization.
        </div>
      ) : (
        <div className="space-y-5">
          {ladders.map((ladder) => (
            <div key={ladder.id} className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white flex items-center gap-2">
                    <Layers className="w-4 h-4 text-indigo-400" />
                    {ladder.fear_theme}
                  </h4>
                  <span className="text-[11px] text-slate-500">{ladder.steps?.length || 0} hierarchical steps</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setAddingStepLadderId(ladder.id)}
                    className="px-3 py-1 text-xs rounded-lg bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600/30 font-medium"
                  >
                    + Add Step
                  </button>
                  <button
                    onClick={async () => {
                      if (confirm("Delete ladder and all steps?")) {
                        await deleteLadder(ladder.id);
                        showNotification("Ladder deleted");
                        onRefresh();
                      }
                    }}
                    className="text-slate-500 hover:text-rose-400 p-1"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Add Step Inline Form */}
              {addingStepLadderId === ladder.id && (
                <div className="bg-slate-950 p-4 rounded-xl border border-indigo-500/30 space-y-3">
                  <div className="text-xs font-semibold text-indigo-300">Add Hierarchical Exposure Step</div>
                  <input
                    type="text"
                    placeholder="Step description (e.g. Say hello to cashier at grocery store)"
                    value={stepDesc}
                    onChange={(e) => setStepDesc(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                  />
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">
                      Target SUDS Level: <span className="text-amber-400 font-bold">{stepSuds}</span>/100
                    </label>
                    <input
                      type="range"
                      min="10"
                      max="100"
                      step="5"
                      value={stepSuds}
                      onChange={(e) => setStepSuds(Number(e.target.value))}
                      className="w-full accent-amber-500"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => setAddingStepLadderId(null)}
                      className="px-3 py-1 text-xs rounded bg-slate-800 text-slate-400"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleAddStep(ladder.id)}
                      className="px-3 py-1 text-xs font-semibold rounded bg-indigo-600 text-white"
                    >
                      Save Step
                    </button>
                  </div>
                </div>
              )}

              {/* Steps List */}
              <div className="space-y-2">
                {ladder.steps?.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">No steps added yet. Click '+ Add Step' to build your fear ladder.</p>
                ) : (
                  ladder.steps?.map((step) => (
                    <div
                      key={step.id}
                      className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between gap-3 text-xs"
                    >
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                          SUDS {step.target_suds}
                        </span>
                        <div>
                          <div className={`font-medium ${step.is_mastered ? "line-through text-slate-500" : "text-slate-200"}`}>
                            {step.description}
                          </div>
                          <div className="text-[10px] text-slate-500">
                            Reps: {step.repetitions_done || 0}
                            {step.last_post_suds !== null && ` | Last Post-SUDS: ${step.last_post_suds}`}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {step.is_mastered ? (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-semibold">
                            Mastered
                          </span>
                        ) : practicingStepId === step.id ? (
                          <div className="flex items-center gap-2 bg-slate-900 p-2 rounded-xl border border-indigo-500/30">
                            <span className="text-[10px]">Pre: {preSuds}</span>
                            <input
                              type="range"
                              min="0"
                              max="100"
                              value={preSuds}
                              onChange={(e) => setPreSuds(Number(e.target.value))}
                              className="w-14 accent-rose-500"
                            />
                            <span className="text-[10px]">Post: {postSuds}</span>
                            <input
                              type="range"
                              min="0"
                              max="100"
                              value={postSuds}
                              onChange={(e) => setPostSuds(Number(e.target.value))}
                              className="w-14 accent-emerald-500"
                            />
                            <button
                              onClick={() => handlePractice(step.id)}
                              className="px-2 py-1 text-[10px] rounded bg-emerald-600 text-white font-semibold"
                            >
                              Log
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => {
                              setPracticingStepId(step.id);
                              setPreSuds(step.target_suds);
                            }}
                            className="px-2.5 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
                          >
                            Practice
                          </button>
                        )}

                        <button
                          onClick={async () => {
                            if (confirm("Delete step?")) {
                              await deleteExposureStep(step.id);
                              showNotification("Step deleted");
                              onRefresh();
                            }
                          }}
                          className="text-slate-500 hover:text-rose-400 p-1"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Action Items Tracker
function ActionsManager({ actions, onRefresh, showNotification }) {
  const [actionText, setActionText] = useState("");

  const handleCreate = async () => {
    if (!actionText) return;
    await createAction({ action_text: actionText });
    setActionText("");
    showNotification("Action item added!");
    onRefresh();
  };

  const handleToggle = async (id, currentDone) => {
    await toggleAction(id, !currentDone);
    onRefresh();
  };

  return (
    <div className="space-y-5">
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
        <div className="text-xs font-bold text-slate-200">Session Behavioral Action Items</div>
        <p className="text-[11px] text-slate-400">
          Cognitive therapy requires behavioral homework. Capture immediate action steps agreed upon during reframing.
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Action item (e.g. Schedule 15-minute phone call with supervisor)"
            value={actionText}
            onChange={(e) => setActionText(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl p-2 text-xs text-slate-200"
          />
          <button
            onClick={handleCreate}
            disabled={!actionText}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white transition disabled:opacity-50"
          >
            Add Action
          </button>
        </div>
      </div>

      {actions.length === 0 ? (
        <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
          No action items yet. Add concrete behavioral assignments above.
        </div>
      ) : (
        <div className="space-y-2">
          {actions.map((act) => (
            <div
              key={act.id}
              className={`p-3 rounded-xl border flex items-center justify-between text-xs transition ${
                act.is_done
                  ? "bg-slate-950/40 border-slate-800/40 text-slate-500"
                  : "bg-slate-900/60 border-slate-800 text-slate-200"
              }`}
            >
              <div
                onClick={() => handleToggle(act.id, act.is_done)}
                className="flex items-center gap-3 cursor-pointer select-none flex-1"
              >
                {act.is_done ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-500 hover:text-slate-300 shrink-0" />
                )}
                <span className={act.is_done ? "line-through text-slate-500" : "font-medium"}>
                  {act.action_text}
                </span>
              </div>

              <button
                onClick={async () => {
                  await deleteAction(act.id);
                  showNotification("Action removed");
                  onRefresh();
                }}
                className="text-slate-500 hover:text-rose-400 p-1"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// -------------------------------------------------------------
// TAB 4: DIAGNOSTICS & GROUNDING FIRST-AID
// -------------------------------------------------------------
function DiagnosticsAndAidView({ subTab, setSubTab, showNotification, onRefresh }) {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Sub Tabs */}
      <div className="flex border-b border-slate-800 pb-3 gap-2">
        <button
          onClick={() => setSubTab("grounding")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "grounding"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Grounding & Breathwork
        </button>
        <button
          onClick={() => setSubTab("das")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "das"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Burns DAS Assessment
        </button>
        <button
          onClick={() => setSubTab("methods")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "methods"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Burns 10 Restructuring Methods
        </button>
        <button
          onClick={() => setSubTab("audit")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            subTab === "audit"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "bg-slate-900/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Clinical Audit & Backup
        </button>
      </div>

      {subTab === "grounding" && <GroundingProtocolsStudio />}
      {subTab === "das" && <DasAssessmentStudio showNotification={showNotification} />}
      {subTab === "methods" && <BurnsMethodsLibrary />}
      {subTab === "audit" && (
        <ClinicalAuditStudio showNotification={showNotification} onRefresh={onRefresh} />
      )}
    </div>
  );
}

// Grounding Protocols (Box Breathing, 4-7-8, 5-4-3-2-1 Sensory)
function GroundingProtocolsStudio() {
  const [protocol, setProtocol] = useState("box"); // box | 478 | 54321
  const [active, setActive] = useState(false);
  const [phase, setPhase] = useState("Inhale");
  const [countdown, setCountdown] = useState(4);

  useEffect(() => {
    let timer;
    if (active && (protocol === "box" || protocol === "478")) {
      timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            if (protocol === "box") {
              if (phase === "Inhale") { setPhase("Hold"); return 4; }
              if (phase === "Hold") { setPhase("Exhale"); return 4; }
              if (phase === "Exhale") { setPhase("Rest"); return 4; }
              if (phase === "Rest") { setPhase("Inhale"); return 4; }
            } else {
              // 4-7-8
              if (phase === "Inhale") { setPhase("Hold"); return 7; }
              if (phase === "Hold") { setPhase("Exhale"); return 8; }
              if (phase === "Exhale") { setPhase("Inhale"); return 4; }
            }
            return 4;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [active, phase, protocol]);

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-6">
      <div className="flex gap-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => { setProtocol("box"); setActive(false); setPhase("Inhale"); setCountdown(4); }}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${protocol === "box" ? "bg-indigo-600 text-white" : "bg-slate-800 text-slate-400"}`}
        >
          Box Breathing (4-4-4-4)
        </button>
        <button
          onClick={() => { setProtocol("478"); setActive(false); setPhase("Inhale"); setCountdown(4); }}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${protocol === "478" ? "bg-indigo-600 text-white" : "bg-slate-800 text-slate-400"}`}
        >
          4-7-8 Relaxing Breath
        </button>
        <button
          onClick={() => { setProtocol("54321"); setActive(false); }}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${protocol === "54321" ? "bg-indigo-600 text-white" : "bg-slate-800 text-slate-400"}`}
        >
          5-4-3-2-1 Sensory Grounding
        </button>
      </div>

      {protocol !== "54321" ? (
        <div className="text-center py-10 space-y-6">
          <div className="relative w-48 h-48 mx-auto flex flex-col items-center justify-center rounded-full border-4 border-indigo-500/30 bg-indigo-950/20 shadow-2xl shadow-indigo-600/10">
            <div className={`text-4xl font-black ${active ? "text-indigo-400 animate-pulse" : "text-slate-400"}`}>
              {active ? countdown : "4"}
            </div>
            <div className="text-sm font-semibold uppercase tracking-wider text-slate-300 mt-1">
              {active ? phase : "Ready"}
            </div>
          </div>

          <div className="space-x-3">
            <button
              onClick={() => setActive(!active)}
              className="px-6 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg transition"
            >
              {active ? "Pause" : "Start Protocol"}
            </button>
            <button
              onClick={() => { setActive(false); setPhase("Inhale"); setCountdown(4); }}
              className="px-4 py-2 rounded-xl text-xs font-medium bg-slate-800 text-slate-400 hover:text-slate-200"
            >
              Reset
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4 text-xs">
          <h4 className="font-bold text-white text-sm">5-4-3-2-1 Somatic Sensory Grounding</h4>
          <p className="text-slate-400">
            Anchor your nervous system into physical reality and interrupt amygdala runaway loops:
          </p>
          <div className="space-y-3 pt-2">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-bold text-indigo-400">5 Things You Can SEE:</span> Look for 5 specific shapes, patterns, or colors in the room.
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-bold text-sky-400">4 Things You Can TOUCH:</span> Feel texture of your shirt, desktop, chair under you, or cold water.
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-bold text-emerald-400">3 Things You Can HEAR:</span> Listen for distant traffic, fan hum, keyboard clicks.
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-bold text-amber-400">2 Things You Can SMELL:</span> Coffee, fresh air, paper, soap.
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-bold text-rose-400">1 Thing You Can TASTE:</span> Mint, water, or acknowledge taste in your mouth.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Burns DAS (Dysfunctional Attitude Scale) Assessment
function DasAssessmentStudio({ showNotification }) {
  const [questions, setQuestions] = useState([]);
  const [history, setHistory] = useState([]);
  const [answers, setAnswers] = useState({});
  const [takingTest, setTakingTest] = useState(false);

  useEffect(() => {
    fetchDasQuestions().then(setQuestions).catch(() => {});
    fetchDasHistory().then(setHistory).catch(() => {});
  }, []);

  const handleScore = (qId, score) => {
    setAnswers((prev) => ({ ...prev, [qId]: score }));
  };

  const handleSubmit = async () => {
    const values = Object.values(answers);
    if (values.length < questions.length) {
      alert("Please answer all questions before submitting.");
      return;
    }
    const total = values.reduce((a, b) => a + b, 0);
    await submitDas({
      scores: answers,
      total_score: total,
      top_vulnerabilities: "Perfectionism, Need for Approval",
    });
    setTakingTest(false);
    showNotification("DAS Assessment recorded!");
    fetchDasHistory().then(setHistory);
  };

  return (
    <div className="space-y-5">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-sm font-bold text-white">Burns Dysfunctional Attitude Scale (DAS)</h3>
          <p className="text-xs text-slate-400 mt-0.5">Identifies silent cognitive vulnerability schemas.</p>
        </div>
        <button
          onClick={() => setTakingTest(!takingTest)}
          className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white"
        >
          {takingTest ? "Cancel Test" : "Take Assessment"}
        </button>
      </div>

      {takingTest ? (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-5">
          <div className="text-xs font-semibold text-slate-300">
            Rate each statement from 1 (Totally Disagree) to 5 (Totally Agree):
          </div>
          <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
            {questions.map((q, idx) => (
              <div key={q.id} className="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                <div className="text-xs text-slate-200">
                  <span className="text-slate-500 font-mono mr-2">{idx + 1}.</span>
                  {q.text}
                </div>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((val) => (
                    <button
                      key={val}
                      type="button"
                      onClick={() => handleScore(q.id, val)}
                      className={`flex-1 py-1 rounded text-xs border font-medium ${
                        answers[q.id] === val
                          ? "bg-indigo-600 text-white border-indigo-500"
                          : "bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      {val}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition"
          >
            Submit & Calculate Vulnerabilities
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {history.length === 0 ? (
            <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
              No DAS evaluations recorded. Take the assessment above to detect core cognitive vulnerabilities.
            </div>
          ) : (
            history.map((item) => (
              <div key={item.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex justify-between items-center text-xs">
                <div>
                  <div className="font-semibold text-slate-200">Total Vulnerability Score: {item.total_score}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">{item.timestamp?.slice(0, 16).replace("T", " ")}</div>
                </div>
                <span className="px-2.5 py-1 rounded-lg bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-medium">
                  {item.total_score > 45 ? "High Vulnerability" : "Resilient Core"}
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

// Burns 10 Restructuring Methods Guide
function BurnsMethodsLibrary() {
  const [methods, setMethods] = useState([]);

  useEffect(() => {
    fetchMethods().then(setMethods).catch(() => {});
  }, []);

  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <h3 className="text-sm font-bold text-white">David Burns' 10 Cognitive Restructuring Methods</h3>
        <p className="text-xs text-slate-400">
          Proven clinical techniques from "Feeling Good" & "When Panic Attacks" to answer automatic negative thoughts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {methods.map((m) => (
          <div key={m.code} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-indigo-300">{m.name}</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                {m.category}
              </span>
            </div>
            <p className="text-slate-300 text-[11px]">{m.summary || m.description}</p>
            {m.when_to_use && (
              <div className="text-[11px] text-amber-300/90 pt-1">
                <span className="font-semibold text-slate-400">When to use: </span>
                {m.when_to_use}
              </div>
            )}
            {m.example && (
              <div className="p-2 rounded bg-slate-950 text-[11px] text-slate-400 italic border border-slate-800/60">
                "{m.example}"
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Clinical Audit & Backup
function ClinicalAuditStudio({ showNotification, onRefresh }) {
  const [audit, setAudit] = useState(null);

  useEffect(() => {
    fetchVerifyAudit().then(setAudit).catch(() => {});
  }, []);

  const handleDownloadBackup = async () => {
    const data = await fetchBackup();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `leahe-backup-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    showNotification("Full JSON backup downloaded!");
  };

  const handleRestoreFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (ev) => {
      try {
        const json = JSON.parse(ev.target.result);
        await restoreBackup(json);
        showNotification("Database successfully restored from JSON backup!");
        onRefresh();
      } catch (err) {
        showNotification("Failed to restore: " + err.message);
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="space-y-6">
      {/* Pattern Audit Card */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
        <h4 className="text-xs font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Clinical Integrity & Unresolved Pattern Audit
        </h4>
        {audit ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-slate-400">Total Entries:</span>
              <div className="text-base font-bold text-white mt-1">{audit.total_entries}</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-slate-400">CBT Records:</span>
              <div className="text-base font-bold text-indigo-400 mt-1">{audit.cbt_count}</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-slate-400">Unresolved Mood:</span>
              <div className="text-base font-bold text-amber-400 mt-1">{audit.unresolved_count}</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-slate-400">Severe Episodes:</span>
              <div className="text-base font-bold text-rose-400 mt-1">{audit.severe_count}</div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-slate-500">Loading audit data...</p>
        )}
      </div>

      {/* Backup & Restore */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
        <h4 className="text-xs font-bold text-white flex items-center gap-2">
          <Download className="w-4 h-4 text-indigo-400" />
          Data Portability & Vault Backup
        </h4>
        <p className="text-xs text-slate-400">
          Leahe is strictly local and private. Export your entire cognitive database to an open JSON archive or restore anytime.
        </p>

        <div className="flex flex-wrap gap-3 pt-2">
          <button
            onClick={handleDownloadBackup}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center gap-2"
          >
            <Download className="w-3.5 h-3.5" />
            Download Full JSON Backup
          </button>

          <label className="px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center gap-2 cursor-pointer">
            <Upload className="w-3.5 h-3.5" />
            Restore from JSON File
            <input type="file" accept=".json" onChange={handleRestoreFile} className="hidden" />
          </label>
        </div>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// Quick Checkin Studio (Inline)
// -------------------------------------------------------------
function QuickCheckinStudio({ emotions, onSaved, onCancel }) {
  const [mood, setMood] = useState(6);
  const [emotion, setEmotion] = useState("Calm");
  const [situation, setSituation] = useState("");

  const handleSave = async () => {
    await createEntry({
      entry_type: "quick",
      initial_mood: mood,
      primary_emotion: emotion,
      emotion_intensity_initial: mood * 10,
      situation: situation || "Quick check-in",
    });
    onSaved();
  };

  return (
    <div className="p-5 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold text-indigo-300 flex items-center gap-2">
          <Heart className="w-4 h-4 text-rose-400" />
          Quick Emotional Check-in
        </h3>
        <button onClick={onCancel} className="text-slate-500 hover:text-slate-300 p-1">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-[11px] text-slate-400 mb-1">
            Current Mood: <span className="font-bold text-indigo-400">{mood}/10</span>
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={mood}
            onChange={(e) => setMood(Number(e.target.value))}
            className="w-full accent-indigo-500"
          />
        </div>

        <div>
          <label className="block text-[11px] text-slate-400 mb-1">Primary Emotion</label>
          <select
            value={emotion}
            onChange={(e) => setEmotion(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2 text-xs text-slate-200"
          >
            {emotions.length > 0 ? (
              emotions.map((em, i) => (
                <option key={i} value={typeof em === "string" ? em : em.name}>
                  {typeof em === "string" ? em : em.name}
                </option>
              ))
            ) : (
              <>
                <option value="Calm">Calm</option>
                <option value="Content">Content</option>
                <option value="Anxious">Anxious</option>
                <option value="Frustrated">Frustrated</option>
                <option value="Tired">Tired</option>
              </>
            )}
          </select>
        </div>

        <div>
          <label className="block text-[11px] text-slate-400 mb-1">Brief Note / Context</label>
          <input
            type="text"
            placeholder="e.g. Taking a short break after meeting"
            value={situation}
            onChange={(e) => setSituation(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2 text-xs text-slate-200"
          />
        </div>
      </div>

      <div className="flex justify-end gap-2 pt-1">
        <button
          onClick={onCancel}
          className="px-3 py-1.5 text-xs rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200"
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white"
        >
          Save Check-in
        </button>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// Slide-over Detail Drawer
// -------------------------------------------------------------
function EntryDetailDrawer({ entry, onClose, onDelete }) {
  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[480px] bg-slate-900 border-l border-slate-800 p-6 shadow-2xl z-40 overflow-y-auto animate-slide-left flex flex-col justify-between">
      <div className="space-y-5">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {entry.entry_type}
            </span>
            <div className="text-xs text-slate-400 mt-1 font-mono">
              {entry.timestamp?.slice(0, 16).replace("T", " ")}
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {entry.situation && (
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">Situation</div>
            <p className="text-xs text-slate-200 bg-slate-950 p-3 rounded-xl border border-slate-800/80">
              {entry.situation}
            </p>
          </div>
        )}

        {entry.automatic_thought && (
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-rose-400 mb-1">
              Automatic Negative Thought
            </div>
            <p className="text-xs text-slate-200 bg-rose-950/20 border border-rose-500/30 p-3 rounded-xl font-medium">
              "{entry.automatic_thought}"
            </p>
          </div>
        )}

        {entry.distortions?.length > 0 && (
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-amber-400 mb-1.5">
              Cognitive Distortions
            </div>
            <div className="flex flex-wrap gap-1.5">
              {entry.distortions.map((d, i) => (
                <span
                  key={i}
                  className="text-xs px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium"
                >
                  {d}
                </span>
              ))}
            </div>
          </div>
        )}

        {entry.alternative_thought && (
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 mb-1">
              Rational Reframe
            </div>
            <p className="text-xs text-slate-200 bg-emerald-950/20 border border-emerald-500/30 p-3 rounded-xl">
              {entry.alternative_thought}
            </p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-3 pt-2">
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs">
            <span className="text-slate-400">Initial Mood:</span>
            <div className="text-base font-bold text-slate-200 mt-0.5">{entry.initial_mood}/10</div>
          </div>
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs">
            <span className="text-slate-400">Final Mood:</span>
            <div className="text-base font-bold text-emerald-400 mt-0.5">
              {entry.final_mood !== null && entry.final_mood !== undefined ? `${entry.final_mood}/10` : "N/A"}
            </div>
          </div>
        </div>
      </div>

      <div className="pt-6 border-t border-slate-800 flex justify-between">
        <button
          onClick={() => {
            if (confirm("Delete this entry permanently?")) onDelete();
          }}
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-rose-600/20 text-rose-300 hover:bg-rose-600/30 border border-rose-500/30 transition flex items-center gap-1.5"
        >
          <Trash2 className="w-3.5 h-3.5" /> Delete Entry
        </button>
        <button
          onClick={onClose}
          className="px-4 py-2 rounded-xl text-xs font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition"
        >
          Close
        </button>
      </div>
    </div>
  );
}
