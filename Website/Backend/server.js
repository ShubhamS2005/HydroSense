import express from "express";
import http from "http";
import cors from "cors";


import { initSocket } from "./config/socket.js";


const app = express();

app.use(cors());
app.use(express.json());



// Create server
const server = http.createServer(app);

// Init socket
initSocket(server);


const PORT = 4000;

server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});