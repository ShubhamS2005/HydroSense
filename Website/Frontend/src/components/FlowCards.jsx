function FlowCards({ data }) {
  if (!data) return null;

  const { flow1, flow2, flow3, diff12, diff23 } = data;

  const getBorderColor = (diff) => {
    if (diff < 0.2) return "border-green-400";
    if (diff < 0.5) return "border-yellow-400";
    return "border-red-500";
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
      
      {/* Flow 1 */}
      <div className="bg-[#1e293b] p-6 rounded-2xl shadow border-t-4 border-blue-400 transition-all duration-500 transform hover:scale-105">
        <h2 className="text-gray-400">Flow 1 (Inlet)</h2>
        <p className="text-3xl font-bold">
          {flow1} <span className="text-xl text-gray-400">L/min</span>
        </p>
      </div>

      {/* Flow 2 */}
      <div className={`bg-[#1e293b] p-6 rounded-2xl shadow border-t-4 ${getBorderColor(diff12)} transition-all duration-500 transform hover:scale-105`}>
        <h2 className="text-gray-400">Flow 2 (Mid)</h2>
        <p className="text-3xl font-bold">
          {flow2} <span className="text-xl text-gray-400">L/min</span>
        </p>
      </div>

      {/* Flow 3 */}
      <div className={`bg-[#1e293b] p-6 rounded-2xl shadow border-t-4 ${getBorderColor(diff23)} transition-all duration-500 transform hover:scale-105`}>
        <h2 className="text-gray-400">Flow 3 (Outlet)</h2>
        <p className="text-3xl font-bold">
          {flow3} <span className="text-xl text-gray-400">L/min</span>
        </p>
      </div>

    </div>
  );
}

export default FlowCards