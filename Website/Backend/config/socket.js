import { Server } from "socket.io";
import { loadCSV, startStreaming } from "../services/dataService.js";

export const initSocket = (server) => {
  const io = new Server(server, {
    cors: { origin: "*" },
  });

  io.on("connection", (socket) => {
    console.log("🟢 Client connected");
  });

  // ✅ Load once
  loadCSV();

  // 🚀 Start stream
  startStreaming(io);
};