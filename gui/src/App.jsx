import React, { useState, useEffect } from "react";
import {
  Activity,
  Brain,
  CheckCircle2,
  ChevronRight,
  Clock,
  Compass,
  FileText,
  Filter,
  Flame,
  HelpCircle,
  Layers,
  LineChart,
  Plus,
  RefreshCw,
  Search,
  ShieldAlert,
  Sparkles,
  Target,
  Trash2,
  Wind,
  X,
} from "lucide-react";
import * as api from "./api";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [status, setStatus] = useState(null);
  const [entries, setEntries] = useState([]);
  const [stats, setStats] = useState(null);
  const [distortions, setDistortions] = useState([]);
  const [experiments, setExperiments] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modals
  const [showCheckinModal, setShowCheckinModal] = useState(false);
  const [showCbtModal, setShowCbtModal] = useState(false);
  const [showSosModal, setShowSosModal] = useState(false);
  const [showExpModal, setShowExpModal] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);

  // Search & Filter
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDistortionFilter, setSelectedDistortionFilter] = useState("");

  const loadData = async () => {
    try {
      const [st, ent, stt, dist, exp, tsk] = await Promise.all([
        api.fetchStatus().catch(() => null),
        api.fetchEntries({ limit: 50, q: searchQuery, distortion: selectedDistortionFilter }),
        api.fetchStats().catch(() => null),
        api.fetchDistortions().catch(() => []),
        api.fetchExperiments().catch(() => []),
        api.fetchTasks().catch(() => []),
      ]);
      setStatus(st);
      if (ent && ent.entries) setEntries(ent.entries);
      setStats(stt);
      setDistortions(dist || []);
      setExperiments(exp || []);
      setTasks(tsk || []);
    } catch (e) {
      console.error("Error loading data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [searchQuery, selectedDistortionFilter]);

  return (
    <div className="flex h-screen w-full bg-zinc-950 text-zinc-100 font-sans overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-zinc-800 bg-zinc-900/60 flex flex-col justify-between p-4 shrink-0">
        <div>
          {/* Logo & Status */}
          <div className="flex items-center gap-3 px-2 py-3 mb-6">
            <div className="w-8 h-8 rounded bg-zinc-800 border border-zinc-700 flex items-center justify-center font-mono font-bold text-sm text-zinc-300">
              &gt;_
            </div>
            <div>
              <div className="font-mono font-bold tracking-wider text-sm flex items-center gap-2">
                LEAHE
                <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-normal">CBT Lab</span>
              </div>
              <div className="text-[11px] text-zinc-400 font-mono">
                {status ? `[${status.entries_count} entries]` : "[Offline]"}
              </div>
            </div>
          </div>

          {/* Quick Action Buttons */}
          <div className="space-y-2 mb-6">
            <button
              onClick={() => setShowCbtModal(true)}
              className="w-full flex items-center justify-center gap-2 bg-zinc-100 hover:bg-white text-zinc-900 font-medium py-2 px-3 rounded text-xs transition duration-150"
            >
              <Plus className="w-4 h-4" />
              CBT Thought Journal
            </button>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setShowCheckinModal(true)}
                className="flex items-center justify-center gap-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700/60 py-1.5 px-2 rounded text-xs transition"
              >
                <Activity className="w-3.5 h-3.5 text-zinc-400" />
                Check-in
              </button>
              <button
                onClick={() => setShowSosModal(true)}
                className="flex items-center justify-center gap-1.5 bg-zinc-800 hover:bg-zinc-700 text-amber-300 border border-amber-900/40 py-1.5 px-2 rounded text-xs transition"
              >
                <Wind className="w-3.5 h-3.5" />
                SOS Breathing
              </button>
            </div>
          </div>

          {/* Menu Items */}
          <nav className="space-y-1 font-mono text-xs">
            <NavItem
              active={activeTab === "dashboard"}
              icon={<Layers className="w-4 h-4" />}
              label="Dashboard & Overview"
              onClick={() => setActiveTab("dashboard")}
            />
            <NavItem
              active={activeTab === "records"}
              icon={<Brain className="w-4 h-4" />}
              label="Thought Journal"
              count={entries.length}
              onClick={() => setActiveTab("records")}
            />
            <NavItem
              active={activeTab === "experiments"}
              icon={<Target className="w-4 h-4" />}
              label="Experiments"
              count={experiments.length}
              onClick={() => setActiveTab("experiments")}
            />
            <NavItem
              active={activeTab === "procrastination"}
              icon={<Clock className="w-4 h-4" />}
              label="Anti-Procrastination"
              count={tasks.length}
              onClick={() => setActiveTab("procrastination")}
            />
            <NavItem
              active={activeTab === "stats"}
              icon={<LineChart className="w-4 h-4" />}
              label="CBT Analytics"
              onClick={() => setActiveTab("stats")}
            />
            <NavItem
              active={activeTab === "distortions"}
              icon={<HelpCircle className="w-4 h-4" />}
              label="Cognitive Distortions"
              count={distortions.length}
              onClick={() => setActiveTab("distortions")}
            />
          </nav>
        </div>

        {/* Sync Footer */}
        <div className="border-t border-zinc-800/80 pt-3">
          <button
            onClick={async () => {
              await api.triggerSync();
              await loadData();
            }}
            className="w-full flex items-center justify-between text-[11px] font-mono text-zinc-400 hover:text-zinc-200 py-1.5 px-2 rounded hover:bg-zinc-800/60 transition"
          >
            <span className="flex items-center gap-2">
              <RefreshCw className="w-3.5 h-3.5" />
              Sync ~/Notes
            </span>
            <span className="text-[10px] text-zinc-500">.md / .yaml</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Header Bar */}
        <header className="h-14 border-b border-zinc-800 flex items-center justify-between px-6 bg-zinc-900/30 shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="font-mono text-sm uppercase tracking-wider text-zinc-300 font-semibold">
              {activeTab === "dashboard" && "Dashboard & Overview"}
              {activeTab === "records" && "CBT Thought Journal"}
              {activeTab === "experiments" && "Behavioral Experiments Lab"}
              {activeTab === "procrastination" && "Anti-Procrastination & Pleasure Sheet"}
              {activeTab === "stats" && "Clinical Analytics & Progress"}
              {activeTab === "distortions" && "Cognitive Distortions Classifier"}
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-zinc-500" />
              <input
                type="text"
                placeholder="Search thoughts and situations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-zinc-900 border border-zinc-800 text-xs rounded pl-8 pr-3 py-1.5 text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-700 w-64 font-mono"
              />
            </div>
          </div>
        </header>

        {/* View Routing */}
        <div className="p-6">
          {activeTab === "dashboard" && (
            <DashboardView
              stats={stats}
              entries={entries}
              experiments={experiments}
              onOpenCbt={() => setShowCbtModal(true)}
              onOpenCheckin={() => setShowCheckinModal(true)}
              onOpenSos={() => setShowSosModal(true)}
              onSelectEntry={setSelectedEntry}
            />
          )}

          {activeTab === "records" && (
            <RecordsView
              entries={entries}
              distortions={distortions}
              selectedFilter={selectedDistortionFilter}
              onSelectFilter={setSelectedDistortionFilter}
              onSelectEntry={setSelectedEntry}
              onDelete={async (id) => {
                await api.deleteEntry(id);
                loadData();
              }}
            />
          )}

          {activeTab === "experiments" && (
            <ExperimentsView
              experiments={experiments}
              onNewExp={() => setShowExpModal(true)}
              onRefresh={loadData}
            />
          )}

          {activeTab === "procrastination" && (
            <ProcrastinationView tasks={tasks} onRefresh={loadData} />
          )}

          {activeTab === "stats" && <StatsView stats={stats} />}

          {activeTab === "distortions" && <DistortionsView distortions={distortions} />}
        </div>
      </main>

      {/* MODALS */}
      {showCheckinModal && (
        <QuickCheckinModal
          onClose={() => setShowCheckinModal(false)}
          onSuccess={() => {
            setShowCheckinModal(false);
            loadData();
          }}
        />
      )}

      {showCbtModal && (
        <CbtThoughtRecordModal
          distortions={distortions}
          onClose={() => setShowCbtModal(false)}
          onSuccess={() => {
            setShowCbtModal(false);
            loadData();
          }}
        />
      )}

      {showSosModal && <SosGroundingModal onClose={() => setShowSosModal(false)} />}

      {showExpModal && (
        <NewExperimentModal
          onClose={() => setShowExpModal(false)}
          onSuccess={() => {
            setShowExpModal(false);
            loadData();
          }}
        />
      )}

      {selectedEntry && (
        <EntryDetailModal entry={selectedEntry} onClose={() => setSelectedEntry(null)} />
      )}
    </div>
  );
}

function NavItem({ active, icon, label, count, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center justify-between px-3 py-2 rounded text-left transition ${
        active
          ? "bg-zinc-800 text-zinc-100 font-semibold"
          : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
      }`}
    >
      <div className="flex items-center gap-2.5 truncate">
        {icon}
        <span className="truncate">{label}</span>
      </div>
      {count !== undefined && count > 0 && (
        <span className="text-[10px] bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded border border-zinc-700/50">
          {count}
        </span>
      )}
    </button>
  );
}

// ======================== DASHBOARD VIEW ========================
function DashboardView({ stats, entries, experiments, onOpenCbt, onOpenCheckin, onOpenSos, onSelectEntry }) {
  const recentEntries = entries.slice(0, 5);
  const activeExps = experiments.filter((e) => !e.is_completed).slice(0, 3);

  return (
    <div className="space-y-6">
      {/* Metric Cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          label="Total Sessions"
          value={stats?.total_entries || 0}
          sub={`CBT: ${stats?.cbt_entries || 0} | Check-ins: ${(stats?.total_entries || 0) - (stats?.cbt_entries || 0)}`}
          icon={<Brain className="w-5 h-5 text-zinc-400" />}
        />
        <StatCard
          label="Average Mood"
          value={stats?.avg_mood ? stats.avg_mood.toFixed(1) : "-"}
          sub="Scale 1-10"
          icon={<Activity className="w-5 h-5 text-zinc-400" />}
        />
        <StatCard
          label="Anxiety Relief"
          value={stats?.avg_relief_percent ? `-${stats.avg_relief_percent.toFixed(0)}%` : "-"}
          sub={stats?.improvement_rate ? `${stats.improvement_rate.toFixed(0)}% improved` : "After CBT work"}
          icon={<Sparkles className="w-5 h-5 text-emerald-400" />}
        />
        <StatCard
          label="Current Streak"
          value={stats?.current_streak ? `${stats.current_streak} d` : "0 d"}
          sub={`Record: ${stats?.longest_streak || 0} d`}
          icon={<Flame className="w-5 h-5 text-amber-400" />}
        />
      </div>

      {/* Emergency & Action banner */}
      <div className="border border-zinc-800 rounded-lg p-5 bg-zinc-900/40 flex items-center justify-between">
        <div>
          <h3 className="font-mono text-sm font-semibold text-zinc-200 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            Acute anxiety or thought rumination?
          </h3>
          <p className="text-xs text-zinc-400 mt-1 max-w-xl">
            Use the Box Breathing protocol (4-4-4-4) to regulate the parasympathetic nervous system before cognitive restructuring.
          </p>
        </div>
        <button
          onClick={onOpenSos}
          className="flex items-center gap-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-mono font-medium py-2 px-4 rounded transition"
        >
          <Wind className="w-4 h-4" />
          Start Breathing (4-4-4-4)
        </button>
      </div>

      {/* 2-Column Section */}
      <div className="grid grid-cols-3 gap-6">
        {/* Recent entries */}
        <div className="col-span-2 border border-zinc-800 rounded-lg bg-zinc-900/30 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/50">
            <h3 className="font-mono text-xs font-semibold uppercase text-zinc-300">
              Recent Sessions
            </h3>
            <span className="text-[11px] font-mono text-zinc-500">Latest {recentEntries.length}</span>
          </div>

          <div className="divide-y divide-zinc-800/60">
            {recentEntries.length === 0 ? (
              <div className="p-8 text-center text-xs text-zinc-500 font-mono">
                No entries yet. Click "CBT Thought Journal" or "Check-in" to log your first record.
              </div>
            ) : (
              recentEntries.map((e) => (
                <div
                  key={e.id}
                  onClick={() => onSelectEntry(e)}
                  className="p-3.5 hover:bg-zinc-800/40 cursor-pointer transition flex items-center justify-between"
                >
                  <div className="space-y-1 min-w-0 pr-4">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded border border-zinc-700/40">
                        {e.entry_type === "cbt_record" ? "CBT JOURNAL" : "CHECK-IN"}
                      </span>
                      <span className="text-xs font-medium text-zinc-200 truncate">
                        {e.automatic_thought || e.situation || e.primary_emotion}
                      </span>
                    </div>
                    <div className="text-[11px] text-zinc-500 font-mono truncate">
                      {e.timestamp ? new Date(e.timestamp).toLocaleString("en-US") : ""} • {e.primary_emotion} ({e.emotion_intensity_initial}%)
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <div className="text-right">
                      <div className="font-mono text-xs font-bold text-zinc-300">
                        {e.initial_mood}
                        {e.final_mood !== null && e.final_mood !== undefined && (
                          <span className="text-emerald-400"> → {e.final_mood}</span>
                        )}
                      </div>
                      <div className="text-[10px] font-mono text-zinc-500">mood</div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-zinc-600" />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Active Behavioral Experiments */}
        <div className="border border-zinc-800 rounded-lg bg-zinc-900/30 overflow-hidden flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/50">
              <h3 className="font-mono text-xs font-semibold uppercase text-zinc-300">
                Active Experiments
              </h3>
              <span className="text-[10px] font-mono text-zinc-500">{activeExps.length} in progress</span>
            </div>

            <div className="p-3 space-y-2.5">
              {activeExps.length === 0 ? (
                <div className="p-6 text-center text-xs text-zinc-500 font-mono">
                  No active behavioral experiments.
                </div>
              ) : (
                activeExps.map((exp) => (
                  <div key={exp.id} className="p-2.5 rounded bg-zinc-900 border border-zinc-800 text-xs space-y-1">
                    <div className="font-semibold text-zinc-200">{exp.title}</div>
                    <div className="text-[11px] text-zinc-400 italic">"{exp.fear_prediction}"</div>
                    <div className="text-[10px] font-mono text-amber-400">
                      Belief in catastrophe: {exp.predicted_belief}%
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, icon }) {
  return (
    <div className="border border-zinc-800 bg-zinc-900/40 rounded-lg p-4">
      <div className="flex items-center justify-between text-zinc-400 mb-2">
        <span className="text-xs font-mono uppercase text-zinc-400">{label}</span>
        {icon}
      </div>
      <div className="text-2xl font-mono font-bold text-zinc-100">{value}</div>
      <div className="text-[11px] text-zinc-500 font-mono mt-1">{sub}</div>
    </div>
  );
}

// ======================== RECORDS VIEW ========================
function RecordsView({ entries, distortions, selectedFilter, onSelectFilter, onSelectEntry, onDelete }) {
  return (
    <div className="space-y-4">
      {/* Filter Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <button
          onClick={() => onSelectFilter("")}
          className={`text-xs font-mono px-2.5 py-1 rounded transition shrink-0 ${
            selectedFilter === ""
              ? "bg-zinc-200 text-zinc-900 font-semibold"
              : "bg-zinc-900 text-zinc-400 border border-zinc-800 hover:text-zinc-200"
          }`}
        >
          All ({entries.length})
        </button>
        {distortions.map((d) => (
          <button
            key={d.code}
            onClick={() => onSelectFilter(d.code)}
            className={`text-xs font-mono px-2.5 py-1 rounded transition shrink-0 ${
              selectedFilter === d.code
                ? "bg-zinc-200 text-zinc-900 font-semibold"
                : "bg-zinc-900 text-zinc-400 border border-zinc-800 hover:text-zinc-200"
            }`}
          >
            {d.name}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="border border-zinc-800 rounded-lg bg-zinc-900/30 overflow-hidden">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-zinc-900/70 border-b border-zinc-800 text-zinc-400 uppercase text-[10px]">
            <tr>
              <th className="py-2.5 px-4">Date / Type</th>
              <th className="py-2.5 px-4">Situation & Automatic Thought</th>
              <th className="py-2.5 px-4">Distortions</th>
              <th className="py-2.5 px-4 text-center">Mood</th>
              <th className="py-2.5 px-4 text-center">Intensity</th>
              <th className="py-2.5 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {entries.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center py-10 text-zinc-500">
                  No entries found.
                </td>
              </tr>
            ) : (
              entries.map((e) => (
                <tr
                  key={e.id}
                  onClick={() => onSelectEntry(e)}
                  className="hover:bg-zinc-800/30 cursor-pointer transition"
                >
                  <td className="py-3 px-4 whitespace-nowrap">
                    <div className="text-zinc-300">{new Date(e.timestamp).toLocaleDateString("en-US")}</div>
                    <div className="text-[10px] text-zinc-500">
                      {e.entry_type === "cbt_record" ? "CBT" : "CHECK-IN"}
                    </div>
                  </td>
                  <td className="py-3 px-4 max-w-md">
                    <div className="text-zinc-200 truncate font-sans font-medium">
                      {e.automatic_thought || e.situation || "No description"}
                    </div>
                    {e.alternative_thought && (
                      <div className="text-[11px] text-emerald-400/90 truncate font-sans italic">
                        ↳ {e.alternative_thought}
                      </div>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1">
                      {e.distortions?.map((d, i) => (
                        <span
                          key={i}
                          className="text-[10px] bg-zinc-800 text-zinc-300 border border-zinc-700/60 px-1.5 py-0.5 rounded"
                        >
                          {d}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="font-bold text-zinc-300">{e.initial_mood}</span>
                    {e.final_mood !== null && e.final_mood !== undefined && (
                      <span className="text-emerald-400"> → {e.final_mood}</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span>{e.emotion_intensity_initial}%</span>
                    {e.emotion_intensity_final !== null && e.emotion_intensity_final !== undefined && (
                      <span className="text-emerald-400"> → {e.emotion_intensity_final}%</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={(evt) => {
                        evt.stopPropagation();
                        if (confirm("Delete this entry?")) {
                          onDelete(e.id);
                        }
                      }}
                      className="text-zinc-500 hover:text-red-400 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ======================== EXPERIMENTS VIEW ========================
function ExperimentsView({ experiments, onNewExp, onRefresh }) {
  const [completeId, setCompleteId] = useState(null);
  const [outcome, setOutcome] = useState("");
  const [severity, setSeverity] = useState(0);
  const [fearRealized, setFearRealized] = useState(false);
  const [conclusion, setConclusion] = useState("");

  const handleComplete = async (e) => {
    e.preventDefault();
    await api.completeExperiment(completeId, {
      actual_outcome: outcome,
      actual_severity: Number(severity),
      fear_realized: Boolean(fearRealized),
      conclusion,
    });
    setCompleteId(null);
    onRefresh();
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs text-zinc-400 max-w-xl">
          Test catastrophic predictions in the real world. Compare predicted dread against empirical outcome.
        </p>
        <button
          onClick={onNewExp}
          className="flex items-center gap-1.5 bg-zinc-100 hover:bg-white text-zinc-900 font-mono text-xs font-semibold py-1.5 px-3 rounded transition"
        >
          <Plus className="w-3.5 h-3.5" />
          New Experiment
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {experiments.map((exp) => (
          <div
            key={exp.id}
            className={`border rounded-lg p-4 font-mono text-xs space-y-3 ${
              exp.is_completed ? "border-zinc-800 bg-zinc-900/20" : "border-zinc-700 bg-zinc-900/60"
            }`}
          >
            <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
              <span className="font-bold text-zinc-200">{exp.title}</span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded border ${
                  exp.is_completed
                    ? "bg-emerald-950/40 text-emerald-400 border-emerald-800/50"
                    : "bg-amber-950/40 text-amber-400 border-amber-800/50"
                }`}
              >
                {exp.is_completed ? "COMPLETED" : "IN PROGRESS"}
              </span>
            </div>

            <div className="space-y-1">
              <div className="text-[10px] text-zinc-500 uppercase">Catastrophic Prediction</div>
              <div className="text-zinc-200 font-sans italic">"{exp.fear_prediction}"</div>
              <div className="text-amber-400 text-[11px]">Belief in fear: {exp.predicted_belief}%</div>
            </div>

            <div className="space-y-1">
              <div className="text-[10px] text-zinc-500 uppercase">Action Plan</div>
              <div className="text-zinc-300 font-sans">{exp.experiment_plan}</div>
            </div>

            {exp.is_completed ? (
              <div className="border-t border-zinc-800/80 pt-2 space-y-1 text-zinc-400">
                <div>Actual outcome: <span className="text-zinc-200 font-sans">{exp.actual_outcome}</span></div>
                <div>Actual severity: <span className="text-emerald-400">{exp.actual_severity}%</span></div>
                <div>
                  Prediction error:{" "}
                  <span className="text-emerald-400 font-bold">
                    {exp.fear_prediction_error !== null ? `-${exp.fear_prediction_error}%` : "-"}
                  </span>
                </div>
                {exp.conclusion && (
                  <div className="text-[11px] text-zinc-300 italic pt-1">
                    Conclusion: {exp.conclusion}
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={() => setCompleteId(exp.id)}
                className="w-full bg-zinc-800 hover:bg-zinc-700 text-zinc-200 py-1.5 rounded transition text-center"
              >
                Record Actual Outcome
              </button>
            )}
          </div>
        ))}
      </div>

      {completeId && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form
            onSubmit={handleComplete}
            className="bg-zinc-900 border border-zinc-800 rounded-lg max-w-md w-full p-5 space-y-4 font-mono text-xs"
          >
            <h3 className="font-bold text-sm text-zinc-200">Complete Experiment #{completeId}</h3>
            <div>
              <label className="block text-zinc-400 mb-1">What actually happened?</label>
              <textarea
                required
                rows={3}
                value={outcome}
                onChange={(e) => setOutcome(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 focus:outline-none focus:border-zinc-700 font-sans text-xs"
              />
            </div>
            <div>
              <label className="block text-zinc-400 mb-1">Actual severity of consequences (0-100%): {severity}%</label>
              <input
                type="range"
                min="0"
                max="100"
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full accent-zinc-200"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="realized"
                checked={fearRealized}
                onChange={(e) => setFearRealized(e.target.checked)}
                className="accent-zinc-200"
              />
              <label htmlFor="realized" className="text-zinc-300">Did the feared catastrophe occur?</label>
            </div>
            <div>
              <label className="block text-zinc-400 mb-1">Therapeutic Conclusion</label>
              <input
                type="text"
                placeholder="What does this experience say about the accuracy of my anxious thoughts?"
                value={conclusion}
                onChange={(e) => setConclusion(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 focus:outline-none focus:border-zinc-700 font-sans text-xs"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setCompleteId(null)}
                className="px-3 py-1.5 rounded bg-zinc-800 text-zinc-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-3 py-1.5 rounded bg-zinc-100 text-zinc-900 font-bold"
              >
                Save
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

// ======================== PROCRASTINATION VIEW ========================
function ProcrastinationView({ tasks, onRefresh }) {
  const [showNew, setShowNew] = useState(false);
  const [taskName, setTaskName] = useState("");
  const [predDiff, setPredDiff] = useState(50);
  const [predPleas, setPredPleas] = useState(50);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.createTask({
      task_name: taskName,
      predicted_difficulty: Number(predDiff),
      predicted_pleasure: Number(predPleas),
    });
    setTaskName("");
    setShowNew(false);
    onRefresh();
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs text-zinc-400 max-w-xl">
          Burns Pleasure & Anti-Procrastination Sheet. Disproves the illusion of cognitive resistance before starting activities.
        </p>
        <button
          onClick={() => setShowNew(true)}
          className="flex items-center gap-1.5 bg-zinc-100 hover:bg-white text-zinc-900 font-mono text-xs font-semibold py-1.5 px-3 rounded transition"
        >
          <Plus className="w-3.5 h-3.5" />
          New Task
        </button>
      </div>

      <div className="border border-zinc-800 rounded-lg bg-zinc-900/30 overflow-hidden font-mono text-xs">
        <table className="w-full text-left">
          <thead className="bg-zinc-900/70 border-b border-zinc-800 text-zinc-400 text-[10px] uppercase">
            <tr>
              <th className="py-2.5 px-4">Task</th>
              <th className="py-2.5 px-4 text-center">Pred. Difficulty</th>
              <th className="py-2.5 px-4 text-center">Pred. Pleasure</th>
              <th className="py-2.5 px-4 text-center">Actual Difficulty</th>
              <th className="py-2.5 px-4 text-center">Actual Pleasure</th>
              <th className="py-2.5 px-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {tasks.map((t) => (
              <tr key={t.id}>
                <td className="py-3 px-4 font-sans font-medium text-zinc-200">{t.task_name}</td>
                <td className="py-3 px-4 text-center text-zinc-400">{t.predicted_difficulty}%</td>
                <td className="py-3 px-4 text-center text-zinc-400">{t.predicted_pleasure}%</td>
                <td className="py-3 px-4 text-center">
                  {t.actual_difficulty !== null ? (
                    <span className="text-emerald-400 font-bold">{t.actual_difficulty}%</span>
                  ) : "-"}
                </td>
                <td className="py-3 px-4 text-center">
                  {t.actual_pleasure !== null ? (
                    <span className="text-emerald-400 font-bold">{t.actual_pleasure}%</span>
                  ) : "-"}
                </td>
                <td className="py-3 px-4 text-right">
                  {t.status === "completed" ? (
                    <span className="text-[10px] text-emerald-400 bg-emerald-950/40 border border-emerald-800/50 px-2 py-0.5 rounded">
                      COMPLETED
                    </span>
                  ) : (
                    <span className="text-[10px] text-amber-400 bg-amber-950/40 border border-amber-800/50 px-2 py-0.5 rounded">
                      PENDING
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showNew && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form
            onSubmit={handleCreate}
            className="bg-zinc-900 border border-zinc-800 rounded-lg max-w-md w-full p-5 space-y-4 font-mono text-xs"
          >
            <h3 className="font-bold text-sm text-zinc-200">Add Task</h3>
            <div>
              <label className="block text-zinc-400 mb-1">Task description</label>
              <input
                required
                type="text"
                value={taskName}
                onChange={(e) => setTaskName(e.target.value)}
                placeholder="e.g. Write report outline"
                className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-sans text-xs focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-zinc-400 mb-1">Predicted difficulty (0-100%): {predDiff}%</label>
              <input
                type="range"
                min="0"
                max="100"
                value={predDiff}
                onChange={(e) => setPredDiff(e.target.value)}
                className="w-full accent-zinc-200"
              />
            </div>
            <div>
              <label className="block text-zinc-400 mb-1">Predicted pleasure (0-100%): {predPleas}%</label>
              <input
                type="range"
                min="0"
                max="100"
                value={predPleas}
                onChange={(e) => setPredPleas(e.target.value)}
                className="w-full accent-zinc-200"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowNew(false)}
                className="px-3 py-1.5 rounded bg-zinc-800 text-zinc-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-3 py-1.5 rounded bg-zinc-100 text-zinc-900 font-bold"
              >
                Create
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

// ======================== STATS VIEW ========================
function StatsView({ stats }) {
  if (!stats) return <div className="text-xs text-zinc-500 font-mono">No statistics available.</div>;

  return (
    <div className="space-y-6 font-mono text-xs">
      <div className="grid grid-cols-3 gap-4">
        <div className="border border-zinc-800 bg-zinc-900/40 rounded-lg p-4 space-y-2">
          <div className="text-zinc-400 uppercase text-[10px]">Cognitive Relief</div>
          <div className="text-2xl font-bold text-emerald-400">
            {stats.avg_relief_percent ? `-${stats.avg_relief_percent.toFixed(1)}%` : "0%"}
          </div>
          <div className="text-zinc-500 text-[11px]">Average reduction in emotional distress</div>
        </div>

        <div className="border border-zinc-800 bg-zinc-900/40 rounded-lg p-4 space-y-2">
          <div className="text-zinc-400 uppercase text-[10px]">Session Improvement Rate</div>
          <div className="text-2xl font-bold text-zinc-100">
            {stats.improvement_rate ? `${stats.improvement_rate.toFixed(1)}%` : "0%"}
          </div>
          <div className="text-zinc-500 text-[11px]">Sessions with improved mood</div>
        </div>

        <div className="border border-zinc-800 bg-zinc-900/40 rounded-lg p-4 space-y-2">
          <div className="text-zinc-400 uppercase text-[10px]">Disconfirmed Fears</div>
          <div className="text-2xl font-bold text-amber-400">
            {stats.disconfirmation_rate ? `${stats.disconfirmation_rate.toFixed(0)}%` : "-"}
          </div>
          <div className="text-zinc-500 text-[11px]">False alarm rate in behavioral experiments</div>
        </div>
      </div>

      {/* Top Distortions list */}
      <div className="border border-zinc-800 bg-zinc-900/30 rounded-lg p-4">
        <h3 className="font-semibold text-zinc-300 uppercase text-[11px] mb-3">
          Cognitive Distortion Frequency
        </h3>
        <div className="space-y-2">
          {stats.distortion_stats?.map((d) => (
            <div key={d.code} className="space-y-1">
              <div className="flex justify-between text-zinc-300 text-[11px]">
                <span>{d.name}</span>
                <span className="text-zinc-500">{d.count} times ({d.percentage.toFixed(0)}%)</span>
              </div>
              <div className="w-full bg-zinc-800 h-2 rounded overflow-hidden">
                <div
                  className="bg-zinc-300 h-full rounded"
                  style={{ width: `${Math.min(d.percentage, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ======================== DISTORTIONS CATALOG ========================
function DistortionsView({ distortions }) {
  return (
    <div className="grid grid-cols-2 gap-4">
      {distortions.map((d) => (
        <div key={d.code} className="border border-zinc-800 bg-zinc-900/40 rounded-lg p-4 space-y-2 font-mono text-xs">
          <div className="font-bold text-sm text-zinc-200">{d.name}</div>
          <div className="text-zinc-400 font-sans text-xs">{d.description}</div>
          <div className="p-2 bg-zinc-950/70 border border-zinc-800/80 rounded text-zinc-300 font-sans italic text-[11px]">
            {d.example}
          </div>
          <div className="pt-2 border-t border-zinc-800/60">
            <div className="text-[10px] text-zinc-500 uppercase mb-1">Socratic Challenge Questions:</div>
            <ul className="list-disc pl-4 space-y-1 text-zinc-400 text-[11px] font-sans">
              {d.challenge_questions?.map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          </div>
        </div>
      ))}
    </div>
  );
}

// ======================== QUICK CHECK-IN MODAL ========================
function QuickCheckinModal({ onClose, onSuccess }) {
  const [mood, setMood] = useState(6);
  const [emotion, setEmotion] = useState("Calm");
  const [intensity, setIntensity] = useState(50);
  const [energy, setEnergy] = useState(5);
  const [notes, setNotes] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await api.createEntry({
      entry_type: "quick",
      initial_mood: Number(mood),
      primary_emotion: emotion,
      emotion_intensity_initial: Number(intensity),
      energy_level: Number(energy),
      notes,
    });
    onSuccess();
  };

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <form
        onSubmit={handleSubmit}
        className="bg-zinc-900 border border-zinc-800 rounded-lg max-w-md w-full p-5 space-y-4 font-mono text-xs"
      >
        <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
          <h3 className="font-bold text-sm text-zinc-200">Quick Mood Check-in</h3>
          <button type="button" onClick={onClose} className="text-zinc-500 hover:text-zinc-300">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div>
          <label className="block text-zinc-400 mb-1">Overall Mood (1-10): <span className="font-bold text-zinc-100">{mood}</span></label>
          <input
            type="range"
            min="1"
            max="10"
            value={mood}
            onChange={(e) => setMood(e.target.value)}
            className="w-full accent-zinc-200"
          />
        </div>

        <div>
          <label className="block text-zinc-400 mb-1">Primary Emotion</label>
          <select
            value={emotion}
            onChange={(e) => setEmotion(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 focus:outline-none"
          >
            <option value="Calm">Calm</option>
            <option value="Neutral">Neutral</option>
            <option value="Anxious">Anxious</option>
            <option value="Worried">Worried</option>
            <option value="Sad">Sad</option>
            <option value="Angry">Angry</option>
            <option value="Grateful">Grateful</option>
            <option value="Determined">Determined</option>
          </select>
        </div>

        <div>
          <label className="block text-zinc-400 mb-1">Emotion Intensity: <span className="font-bold text-zinc-100">{intensity}%</span></label>
          <input
            type="range"
            min="0"
            max="100"
            value={intensity}
            onChange={(e) => setIntensity(e.target.value)}
            className="w-full accent-zinc-200"
          />
        </div>

        <div>
          <label className="block text-zinc-400 mb-1">Energy Level (1-10): {energy}</label>
          <input
            type="range"
            min="1"
            max="10"
            value={energy}
            onChange={(e) => setEnergy(e.target.value)}
            className="w-full accent-zinc-200"
          />
        </div>

        <div>
          <label className="block text-zinc-400 mb-1">Context / Notes</label>
          <input
            type="text"
            placeholder="Brief note or context..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-sans focus:outline-none"
          />
        </div>

        <div className="flex justify-end gap-2 pt-2 border-t border-zinc-800">
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1.5 rounded bg-zinc-800 text-zinc-300"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-1.5 rounded bg-zinc-100 text-zinc-900 font-bold"
          >
            Save Check-in
          </button>
        </div>
      </form>
    </div>
  );
}

// ======================== CBT 7-STEP THOUGHT RECORD MODAL ========================
function CbtThoughtRecordModal({ distortions, onClose, onSuccess }) {
  const [step, setStep] = useState(1);
  const [situation, setSituation] = useState("");
  const [initialMood, setInitialMood] = useState(4);
  const [primaryEmotion, setPrimaryEmotion] = useState("Anxious");
  const [initialIntensity, setInitialIntensity] = useState(80);
  const [nat, setNat] = useState("");
  const [natBelief, setNatBelief] = useState(85);
  const [selectedDistortions, setSelectedDistortions] = useState([]);
  const [evidenceFor, setEvidenceFor] = useState("");
  const [evidenceAgainst, setEvidenceAgainst] = useState("");
  const [alternative, setAlternative] = useState("");
  const [alternativeBelief, setAlternativeBelief] = useState(75);
  const [finalMood, setFinalMood] = useState(7);
  const [finalIntensity, setFinalIntensity] = useState(30);
  const [actionPlan, setActionPlan] = useState("");

  const toggleDistortion = (code) => {
    if (selectedDistortions.includes(code)) {
      setSelectedDistortions(selectedDistortions.filter((c) => c !== code));
    } else {
      setSelectedDistortions([...selectedDistortions, code]);
    }
  };

  const handleFinish = async () => {
    await api.createEntry({
      entry_type: "cbt_record",
      situation,
      initial_mood: Number(initialMood),
      primary_emotion: primaryEmotion,
      emotion_intensity_initial: Number(initialIntensity),
      automatic_thought: nat,
      belief_initial: Number(natBelief),
      distortions: selectedDistortions,
      evidence_for: evidenceFor,
      evidence_against: evidenceAgainst,
      alternative_thought: alternative,
      belief_final: Number(alternativeBelief),
      final_mood: Number(finalMood),
      emotion_intensity_final: Number(finalIntensity),
      action_plan: actionPlan,
    });
    onSuccess();
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg max-w-2xl w-full p-6 font-mono text-xs flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div>
            <h2 className="font-bold text-sm text-zinc-100 flex items-center gap-2">
              <Brain className="w-4 h-4 text-zinc-400" />
              Cognitive Restructuring (7-Step CBT Thought Record)
            </h2>
            <div className="text-[11px] text-zinc-500 mt-0.5">Step {step} of 5</div>
          </div>
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-300">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="py-4 flex-1 overflow-y-auto space-y-4">
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <label className="block text-zinc-300 font-bold mb-1">
                  1. Triggering Situation
                </label>
                <p className="text-[11px] text-zinc-500 mb-2">
                  Describe objective facts: who, where, when, what happened (without subjective evaluations).
                </p>
                <textarea
                  rows={3}
                  value={situation}
                  onChange={(e) => setSituation(e.target.value)}
                  placeholder="e.g. Sent report to manager and did not receive a reply for two hours."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200 font-sans text-xs focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-zinc-300 mb-1">Primary Emotion</label>
                  <input
                    type="text"
                    value={primaryEmotion}
                    onChange={(e) => setPrimaryEmotion(e.target.value)}
                    placeholder="Anxious, Ashamed, Frustrated..."
                    className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-sans text-xs"
                  />
                </div>
                <div>
                  <label className="block text-zinc-300 mb-1">
                    Distress Intensity: {initialIntensity}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={initialIntensity}
                    onChange={(e) => setInitialIntensity(e.target.value)}
                    className="w-full accent-zinc-200"
                  />
                </div>
              </div>

              <div>
                <label className="block text-zinc-300 mb-1">
                  Initial Mood (1-10): {initialMood}
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={initialMood}
                  onChange={(e) => setInitialMood(e.target.value)}
                  className="w-full accent-zinc-200"
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div>
                <label className="block text-zinc-300 font-bold mb-1">
                  2. Automatic Negative Thought (NAT)
                </label>
                <p className="text-[11px] text-zinc-500 mb-2">
                  What exact thought crossed your mind? ("I failed", "They think I'm incompetent", etc.)
                </p>
                <textarea
                  rows={3}
                  value={nat}
                  onChange={(e) => setNat(e.target.value)}
                  placeholder="Write down the thought verbatim..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200 font-sans text-xs focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-zinc-300 mb-1">
                  Degree of Belief (0-100%): {natBelief}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={natBelief}
                  onChange={(e) => setNatBelief(e.target.value)}
                  className="w-full accent-zinc-200"
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-3">
              <label className="block text-zinc-300 font-bold">
                3. Identifying Cognitive Distortions
              </label>
              <p className="text-[11px] text-zinc-500">
                Which thinking traps is this thought caught in? Check all that apply:
              </p>

              <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto pr-1">
                {distortions.map((d) => {
                  const selected = selectedDistortions.includes(d.code);
                  return (
                    <button
                      key={d.code}
                      type="button"
                      onClick={() => toggleDistortion(d.code)}
                      className={`p-2.5 rounded border text-left transition ${
                        selected
                          ? "bg-zinc-800 border-zinc-500 text-zinc-100 font-bold"
                          : "bg-zinc-950 border-zinc-800 text-zinc-400 hover:text-zinc-200"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs">{d.name}</span>
                        {selected && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                      </div>
                      <div className="text-[10px] text-zinc-500 font-normal font-sans line-clamp-1 mt-0.5">
                        {d.summary}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-4">
              <label className="block text-zinc-300 font-bold">
                4. Socratic Examination of Evidence
              </label>

              <div>
                <label className="block text-zinc-400 text-[11px] mb-1">
                  Evidence FOR the thought (Objective verifiable facts only, not feelings):
                </label>
                <textarea
                  rows={2}
                  value={evidenceFor}
                  onChange={(e) => setEvidenceFor(e.target.value)}
                  placeholder="What objective evidence supports this thought?"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-sans text-xs focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-emerald-400 text-[11px] mb-1 font-bold">
                  Evidence AGAINST the thought (Contradictions, exceptions, alternative hypotheses):
                </label>
                <textarea
                  rows={3}
                  value={evidenceAgainst}
                  onChange={(e) => setEvidenceAgainst(e.target.value)}
                  placeholder="What contradicts this thought? What would you tell a friend in this exact situation?"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-sans text-xs focus:outline-none"
                />
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-4">
              <div>
                <label className="block text-zinc-300 font-bold mb-1">
                  5. Adaptive Rational Response (Reframe)
                </label>
                <p className="text-[11px] text-zinc-500 mb-2">
                  Formulate a balanced, fact-based response: "Even if..., in reality..., therefore I can..."
                </p>
                <textarea
                  rows={3}
                  value={alternative}
                  onChange={(e) => setAlternative(e.target.value)}
                  placeholder="Rational, realistic alternative thought..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200 font-sans text-xs focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-zinc-300 mb-1">
                    Final Mood (1-10): <span className="font-bold text-emerald-400">{finalMood}</span>
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={finalMood}
                    onChange={(e) => setFinalMood(e.target.value)}
                    className="w-full accent-emerald-400"
                  />
                </div>
                <div>
                  <label className="block text-zinc-300 mb-1">
                    Residual Distress: <span className="font-bold text-emerald-400">{finalIntensity}%</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={finalIntensity}
                    onChange={(e) => setFinalIntensity(e.target.value)}
                    className="w-full accent-emerald-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-zinc-300 mb-1">Micro-action (Behavioral Activation)</label>
                <input
                  type="text"
                  value={actionPlan}
                  onChange={(e) => setActionPlan(e.target.value)}
                  placeholder="One small concrete constructive step right now..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-sans text-xs"
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer Navigation */}
        <div className="flex items-center justify-between border-t border-zinc-800 pt-3">
          <button
            type="button"
            disabled={step === 1}
            onClick={() => setStep(step - 1)}
            className="px-3 py-1.5 rounded bg-zinc-800 text-zinc-300 disabled:opacity-40"
          >
            Back
          </button>

          {step < 5 ? (
            <button
              type="button"
              onClick={() => setStep(step + 1)}
              className="px-4 py-1.5 rounded bg-zinc-100 text-zinc-900 font-bold"
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              onClick={handleFinish}
              className="px-4 py-1.5 rounded bg-emerald-400 text-zinc-950 font-bold"
            >
              Complete & Save
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ======================== SOS BOX BREATHING MODAL ========================
function SosGroundingModal({ onClose }) {
  const [phase, setPhase] = useState("Inhale");
  const [secondsLeft, setSecondsLeft] = useState(4);
  const [cycle, setCycle] = useState(1);

  useEffect(() => {
    const phases = ["Inhale", "Hold", "Exhale", "Hold"];
    let currentPhaseIndex = 0;
    let sec = 4;

    const interval = setInterval(() => {
      sec -= 1;
      if (sec <= 0) {
        currentPhaseIndex = (currentPhaseIndex + 1) % 4;
        sec = 4;
        setPhase(phases[currentPhaseIndex]);
        if (currentPhaseIndex === 0) {
          setCycle((c) => c + 1);
        }
      }
      setSecondsLeft(sec);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl max-w-sm w-full p-8 text-center font-mono space-y-6">
        <div className="flex justify-between items-center text-zinc-500 text-xs">
          <span>BOX BREATHING 4-4-4-4</span>
          <button onClick={onClose} className="hover:text-zinc-200">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Pulsing Visual */}
        <div className="relative w-40 h-40 mx-auto flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border border-zinc-700/60 animate-ping opacity-25" />
          <div className="w-32 h-32 rounded-full border-2 border-emerald-500/70 flex flex-col items-center justify-center bg-zinc-950/60 shadow-lg shadow-emerald-950/40">
            <div className="text-3xl font-bold text-zinc-100">{secondsLeft}</div>
            <div className="text-[10px] text-zinc-400 uppercase mt-1">seconds</div>
          </div>
        </div>

        <div>
          <div className="text-lg font-bold text-emerald-400">{phase}</div>
          <p className="text-xs text-zinc-400 font-sans mt-1">
            Breathe with your diaphragm. Focus on physical sensations in your body. Cycle: {cycle}
          </p>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded text-xs transition"
        >
          End Practice
        </button>
      </div>
    </div>
  );
}

// ======================== NEW EXPERIMENT MODAL ========================
function NewExperimentModal({ onClose, onSuccess }) {
  const [title, setTitle] = useState("");
  const [fear, setFear] = useState("");
  const [belief, setBelief] = useState(85);
  const [plan, setPlan] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await api.createExperiment({
      title,
      fear_prediction: fear,
      predicted_belief: Number(belief),
      experiment_plan: plan,
    });
    onSuccess();
  };

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <form
        onSubmit={handleSubmit}
        className="bg-zinc-900 border border-zinc-800 rounded-lg max-w-md w-full p-5 space-y-4 font-mono text-xs"
      >
        <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
          <h3 className="font-bold text-sm text-zinc-200">New Behavioral Experiment</h3>
          <button type="button" onClick={onClose} className="text-zinc-500 hover:text-zinc-300">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div>
          <label className="block text-zinc-400 mb-1">Experiment Title / Scenario</label>
          <input
            required
            type="text"
            placeholder="e.g. Ask a clarifying question in the team meeting"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-sans focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-zinc-400 mb-1">Catastrophic Prediction (What do you fear will happen?)</label>
          <textarea
            required
            rows={2}
            placeholder="e.g. Everyone will think I am incompetent and an awkward silence will fall."
            value={fear}
            onChange={(e) => setFear(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-sans focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-zinc-400 mb-1">Belief in Prediction (0-100%): {belief}%</label>
          <input
            type="range"
            min="0"
            max="100"
            value={belief}
            onChange={(e) => setBelief(e.target.value)}
            className="w-full accent-zinc-200"
          />
        </div>

        <div>
          <label className="block text-zinc-400 mb-1">Empirical Test Plan</label>
          <textarea
            required
            rows={2}
            placeholder="What specific action will you take to test this prediction?"
            value={plan}
            onChange={(e) => setPlan(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-sans focus:outline-none"
          />
        </div>

        <div className="flex justify-end gap-2 pt-2 border-t border-zinc-800">
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1.5 rounded bg-zinc-800 text-zinc-300"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-1.5 rounded bg-zinc-100 text-zinc-900 font-bold"
          >
            Create Experiment
          </button>
        </div>
      </form>
    </div>
  );
}

// ======================== ENTRY DETAIL MODAL ========================
function EntryDetailModal({ entry, onClose }) {
  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg max-w-lg w-full p-5 space-y-4 font-mono text-xs max-h-[85vh] overflow-y-auto">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
          <div>
            <span className="text-[10px] bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded border border-zinc-700/50">
              {entry.entry_type === "cbt_record" ? "CBT JOURNAL" : "CHECK-IN"}
            </span>
            <span className="text-zinc-500 text-[11px] ml-2">
              {new Date(entry.timestamp).toLocaleString("en-US")}
            </span>
          </div>
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-300">
            <X className="w-4 h-4" />
          </button>
        </div>

        {entry.situation && (
          <div>
            <div className="text-[10px] text-zinc-500 uppercase">Situation / Trigger</div>
            <div className="text-zinc-200 font-sans mt-0.5">{entry.situation}</div>
          </div>
        )}

        {entry.automatic_thought && (
          <div>
            <div className="text-[10px] text-zinc-500 uppercase">Automatic Negative Thought</div>
            <div className="text-zinc-200 font-sans mt-0.5 font-medium">"{entry.automatic_thought}"</div>
            {entry.belief_initial !== null && (
              <div className="text-zinc-500 text-[10px] mt-0.5">Belief: {entry.belief_initial}%</div>
            )}
          </div>
        )}

        {entry.distortions?.length > 0 && (
          <div>
            <div className="text-[10px] text-zinc-500 uppercase mb-1">Cognitive Distortions</div>
            <div className="flex flex-wrap gap-1">
              {entry.distortions.map((d, i) => (
                <span key={i} className="text-[10px] bg-zinc-800 border border-zinc-700 px-1.5 py-0.5 rounded text-zinc-300">
                  {d}
                </span>
              ))}
            </div>
          </div>
        )}

        {entry.evidence_for && (
          <div>
            <div className="text-[10px] text-zinc-500 uppercase">Evidence FOR</div>
            <div className="text-zinc-300 font-sans mt-0.5">{entry.evidence_for}</div>
          </div>
        )}

        {entry.evidence_against && (
          <div>
            <div className="text-[10px] text-emerald-400 uppercase">Evidence AGAINST</div>
            <div className="text-zinc-200 font-sans mt-0.5">{entry.evidence_against}</div>
          </div>
        )}

        {entry.alternative_thought && (
          <div className="p-3 bg-zinc-950 border border-zinc-800 rounded">
            <div className="text-[10px] text-emerald-400 uppercase font-bold">Rational Response (Reframe)</div>
            <div className="text-zinc-100 font-sans mt-1 font-medium">{entry.alternative_thought}</div>
          </div>
        )}

        <div className="grid grid-cols-2 gap-2 border-t border-zinc-800/80 pt-2 text-zinc-400">
          <div>
            Mood: <span className="text-zinc-200">{entry.initial_mood}</span>
            {entry.final_mood !== null && <span className="text-emerald-400"> → {entry.final_mood}</span>}
          </div>
          <div>
            Distress: <span className="text-zinc-200">{entry.emotion_intensity_initial}%</span>
            {entry.emotion_intensity_final !== null && <span className="text-emerald-400"> → {entry.emotion_intensity_final}%</span>}
          </div>
        </div>

        {entry.action_plan && (
          <div>
            <div className="text-[10px] text-zinc-500 uppercase">Micro-Action</div>
            <div className="text-zinc-300 font-sans mt-0.5">{entry.action_plan}</div>
          </div>
        )}

        <div className="flex justify-end pt-2">
          <button onClick={onClose} className="px-4 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
