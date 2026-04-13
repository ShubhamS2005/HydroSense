function StatusPanel({ data }) {
  if (!data) return null;

  const { flag, zone, risk, reason } = data;

  // 🎨 Color logic
  const getBgColor = () => {
    if (risk === "HIGH") return "bg-red-500/20 border-red-500";
    if (risk === "MEDIUM") return "bg-yellow-400/20 border-yellow-400";
    return "bg-green-500/20 border-green-500";
  };

  const getTextColor = () => {
    if (risk === "HIGH") return "text-red-400";
    if (risk === "MEDIUM") return "text-yellow-300";
    return "text-green-400";
  };

  return (
    <div className={`mt-6 p-6 rounded-2xl border-2 ${getBgColor()} shadow-lg`}>
      
      <h2 className="text-xl font-semibold mb-4">
        Leak Detection Status
      </h2>

      <div className="flex flex-col md:flex-row md:justify-between gap-4">

        {/* Status */}
        <div>
          <p className="text-gray-400">Status</p>
          <p className={`text-3xl font-bold ${getTextColor()}`}>
            {flag}
          </p>
        </div>

        {/* Zone */}
        <div>
          <p className="text-gray-400">Zone</p>
          <p className="text-2xl font-semibold">
            {zone}
          </p>
        </div>

        {/* Risk */}
        <div>
          <p className="text-gray-400">Risk Level</p>
          <p className={`text-2xl font-semibold ${getTextColor()}`}>
            {risk}
          </p>
        </div>

      </div>

      {/* Reason */}
      <div className="mt-4">
        <p className="text-gray-400">Reason</p>
        <p className="text-lg">{reason}</p>
      </div>

    </div>
  );
}

export default StatusPanel;