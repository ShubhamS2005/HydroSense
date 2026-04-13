import { useEffect, useState } from "react";

function AlertsPanel({ data }) {
  const [alerts, setAlerts] = useState(() => {
    // ✅ load from localStorage (for refresh fix)
    const saved = localStorage.getItem("alerts");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    if (!data) return;

    // 👉 Ignore low risk
    if (data.risk === "LOW") return;

    const newAlert = {
      time: new Date().toLocaleTimeString(),
      message: `${data.risk} ${data.flag} (${data.zone})`,
    };

    setAlerts((prev) => {
      // ✅ prevent duplicate alerts
      if (prev.length > 0 && prev[0].message === newAlert.message) {
        return prev;
      }

      const updated = [newAlert, ...prev].slice(0, 10);

      // ✅ persist in localStorage
      localStorage.setItem("alerts", JSON.stringify(updated));

      return updated;
    });

  }, [data]);

  return (
    <div className="bg-[#1e293b] p-6 rounded-2xl shadow mt-6">
      <h2 className="text-lg font-semibold mb-4 text-red-400">
        Alerts & Logs
      </h2>

      <div className="max-h-60 overflow-y-auto space-y-2 pr-2">
        {alerts.length === 0 ? (
          <p className="text-gray-400">No alerts yet</p>
        ) : (
          alerts.map((alert, index) => (
            <div
              key={index}
              className="bg-[#0f172a] p-3 rounded-lg border border-gray-700"
            >
              <p className="text-sm text-gray-400">{alert.time}</p>
              <p className="font-semibold text-red-400">
                {alert.message}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default AlertsPanel;