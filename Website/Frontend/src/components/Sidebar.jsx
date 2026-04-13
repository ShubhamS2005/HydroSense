function Sidebar() {
  return (
    <div className="w-64 bg-[#0f172a] p-5 hidden md:block">
      
      <h2 className="text-xl font-bold text-blue-400 mb-8">
        💧 Hydro Sense
      </h2>

      <ul className="space-y-4 text-gray-300">
        <li className="hover:text-white cursor-pointer">Dashboard</li>
        <li className="hover:text-white cursor-pointer">Analytics</li>
        <li className="hover:text-white cursor-pointer">Alerts</li>
        <li className="hover:text-white cursor-pointer">Settings</li>
      </ul>

    </div>
  );
}

export default Sidebar;