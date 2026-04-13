import { io } from "socket.io-client";

// Connect to backend server
const socket = io("http://localhost:4000");

export default socket;