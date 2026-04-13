import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import FlowCards from "./components/FlowCards";
import FlowChart from "./components/FlowChart";
import { useEffect, useState } from "react";
import socket from "./services/socket";
import StatusPanel from "./components/StatusPanel";
import PipelineVisual from "./components/PipelineVisual";
import AlertsPanel from "./components/AlertsPanel";
import SystemHealth from "./components/SystemHealth";

function App() {

  const [data, setData] = useState(null);

  useEffect(() => {
    socket.on("liveData", (newData) => {
      setData(newData);
    });

    return () => socket.off("liveData");
  }, []);


  return (
    <div className="flex h-screen bg-black text-white">
      
      {/* Sidebar */}
      {/* <Sidebar /> */}

      {/* Right Section */}
      <div className="flex-1 flex flex-col">
        
        {/* Navbar */}
        <Navbar />

        {/* Main Content */}
        <div className="p-6 overflow-y-auto flex-1">
          <h1 className="text-2xl font-bold text-blue-400">
            Dashboard Overview
          </h1>

           {/* <FlowCards data={dummyData} /> */}

           <FlowCards data={data} />
           <FlowChart data={data} />
           <StatusPanel data={data} />
           <PipelineVisual data={data} />
           <AlertsPanel data={data} />
           <SystemHealth data={data} />
        </div>

      </div>
    </div>
  );
}

export default App;