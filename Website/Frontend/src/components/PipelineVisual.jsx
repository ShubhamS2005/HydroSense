function PipelineVisual({ data }) {
  if (!data) return null;

  const { flow1, flow2, flow3, zone, risk } = data;
//   console.log("ZONE:", zone, "RISK:", risk);

  const isLeak12 = zone === "1-2" && risk === "HIGH";
  const isLeak23 = zone === "2-3" && risk === "HIGH";

  const getPipeColor = (pipe) => {
    if (pipe === "1-2") {
      if (data.diff12 > 0.5) return "bg-red-500 animate-pulse";
      if (data.diff12 > 0.2) return "bg-yellow-400";
      return "bg-green-500";
    }

    if (pipe === "2-3") {
      if (data.diff23 > 0.5) return "bg-red-500 animate-pulse";
      if (data.diff23 > 0.2) return "bg-yellow-400";
      return "bg-green-500";
    }
  };

  return (
    <div className="bg-[#1e293b] p-6 rounded-2xl shadow mt-6">
      <h2 className="text-lg font-semibold mb-6 text-blue-400">
        Pipeline Flow Visualization
      </h2>

      <div className="flex items-center justify-between">
        {/* Sensor 1 */}
        <div className="text-center">
          <div className="bg-blue-500 w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold">
            1
          </div>
          <p className="mt-2 w-20 text-center font-mono">
            {flow1.toFixed(2)} L/min
          </p>
        </div>

        {/* Pipe 1-2 */}
        <div className="flex-1 mx-2 relative">
          <div
            className={`h-2 mr-5 transition-all duration-500 mb-12 rounded-full ${getPipeColor("1-2")}`}
          />
        </div>

        {/* Sensor 2 */}
        <div className="text-center">
          <div className="bg-green-500 w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold">
            2
          </div>
          <p className="mt-2 w-20 text-center font-mono">
            {flow2.toFixed(2)} L/min
          </p>
        </div>

        {/* Pipe 2-3 */}
        <div className="flex-1 mx-2 relative">
          <div
            className={`h-2 mr-5 transition-all duration-500 mb-12 rounded-full ${getPipeColor("1-2")}`}
          />
        </div>

        {/* Sensor 3 */}
        <div className="text-center">
          <div className="bg-yellow-400 w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold text-black">
            3
          </div>
          <p className="mt-2 w-20 text-center font-mono">
            {flow3.toFixed(2)} L/min
          </p>
        </div>
      </div>

      {/* Leak Label */}
      {(isLeak12 || isLeak23) && (
        <div className="mt-4 text-center text-red-400 font-semibold animate-pulse">
          🚨 Leak detected in zone {zone}
        </div>
      )}
    </div>
  );
}

export default PipelineVisual;
