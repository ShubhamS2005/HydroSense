import { useEffect, useState, useRef } from "react";

function SystemHealth({ data }) {
  const lastUpdateRef = useRef(null);
const [dataRate, setDataRate] = useState(0);

useEffect(() => {
  if (!data) return;

  const now = Date.now();

  if (lastUpdateRef.current) {
    const diff = (now - lastUpdateRef.current) / 1000;
    const rate = (1 / diff).toFixed(2);
    setDataRate(rate);
  }

  lastUpdateRef.current = now;

}, [data]);

  // 🟢 Sensor Status
  const isSensorActive =
    data &&
    (data.flow1 !== 0 || data.flow2 !== 0 || data.flow3 !== 0);

  // 🟢 Connection Status
  const isConnected = !!data;

  return (
    <div className="bg-[#1e293b] p-6 rounded-2xl shadow mt-6">
      <h2 className="text-lg font-semibold mb-4 text-blue-400">
        System Health
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {/* Sensor Status */}
        <div className="bg-[#0f172a] p-4 rounded-xl">
          <p className="text-gray-400">Sensors</p>
          <p className={`text-xl font-semibold ${isSensorActive ? "text-green-400" : "text-red-400"}`}>
            {isSensorActive ? "Active" : "No Signal"}
          </p>
        </div>

        {/* Connection */}
        <div className="bg-[#0f172a] p-4 rounded-xl">
          <p className="text-gray-400">Connection</p>
          <p className={`text-xl font-semibold ${isConnected ? "text-green-400" : "text-red-400"}`}>
            {isConnected ? "Connected" : "Disconnected"}
          </p>
        </div>

        {/* Data Rate */}
        <div className="bg-[#0f172a] p-4 rounded-xl">
          <p className="text-gray-400">Data Rate</p>
          <p className="text-xl font-semibold text-blue-400">
            {dataRate || 0} /sec
          </p>
        </div>

      </div>
    </div>
  );
}

export default SystemHealth;