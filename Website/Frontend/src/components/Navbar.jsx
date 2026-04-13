function Navbar() {
  return (
    <div className="bg-[#1e293b] p-4 flex justify-between items-center shadow">
      
      <h1 className="text-lg font-semibold">
        <strong>💧 Hydro Sense</strong>
      </h1>

      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-300">
          Live Status
        </span>
        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
      </div>

    </div>
  );
}

export default Navbar;