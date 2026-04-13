import fs from "fs";

let allData = [];
let currentIndex = 0;

export const loadCSV = () => {
  const raw = fs.readFileSync("./data/raw_data.csv", "utf-8");

  const lines = raw.trim().split("\n");

  // remove header
  const dataLines = lines.slice(1);

  allData = dataLines.map((line) => {
    const row = line.split(",");

    return {
      timestamp: row[0],
      flow1: Number(row[1]),
      flow2: Number(row[2]),
      flow3: Number(row[3]),
      pressure: Number(row[4]),
      diff12: Number(row[5]),
      diff23: Number(row[6]),
      flow_ratio_12: Number(row[7]),
      flow_ratio_23: Number(row[8]),
      flag: row[9],
      zone: row[10],
      risk: row[11],
      reason: row[12],
    };
  });

  console.log("✅ CSV Loaded:", allData.length, "rows");
};

// 🚀 Stream like real-time
export const startStreaming = (io) => {
  setInterval(() => {
    if (allData.length === 0) return;

    const data = allData[currentIndex];

    io.emit("liveData", data);

    // console.log("📡 Sent:", data.flow1, data.flow2, data.flow3);

    currentIndex++;

    // loop again (continuous)
    if (currentIndex >= allData.length) {
      currentIndex = 0;
    }
  }, 1000);
};