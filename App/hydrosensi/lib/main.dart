import 'package:flutter/material.dart';
import 'dart:async';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:csv/csv.dart';

void main() {
  runApp(const MyApp());
}

final FlutterTts tts = FlutterTts();

class AppColors {
  static const Color bg = Color(0xFF020617);
  static const Color panel = Color(0xFF0F172A);
  static const Color card = Color(0xFF1E293B);
  static const Color border = Color(0xFF334155);

  static const Color primary = Color(0xFF38BDF8);
  static const Color green = Color(0xFF22C55E);
  static const Color yellow = Color(0xFFFACC15);
  static const Color orange = Color(0xFFF59E0B);
  static const Color red = Color(0xFFEF4444);

  static const Color textPrimary = Colors.white;
  static const Color textSecondary = Color(0xFF94A3B8);
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Hydro Sense Demo",
      theme: ThemeData.dark(),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<Map<String, dynamic>> allData = [];
  int currentIndex = 0;
  Timer? timer;
  bool alertShown = false;

  String leak = "NO";
  String severity = "LOW";
  String zone = "NORMAL";
  String status = "Normal";
  String reason = "Waiting for demo data...";

  double probability = 0.0;
  double flow1 = 0.0;
  double flow2 = 0.0;
  double flow3 = 0.0;
  double diff12 = 0.0;
  double diff23 = 0.0;

  List<double> flowHistory = [];

  @override
  void initState() {
    super.initState();
    loadCSVAndStartDemo();
  }

  Future<void> loadCSVAndStartDemo() async {
    final raw = await rootBundle.loadString('assets/data/raw_data.csv');
    final rows = const CsvToListConverter(eol: '\n').convert(raw);

    if (rows.length <= 1) return;

    allData = rows.skip(1).map((row) {
      double parseNum(dynamic v) {
        if (v == null) return 0.0;
        return double.tryParse(v.toString()) ?? 0.0;
      }

      final f1 = parseNum(row[15]);
      final f2 = parseNum(row[16]);
      final f3 = parseNum(row[17]);

      final d12 = parseNum(row[18]);
      final d23 = parseNum(row[19]);

      final zoneNew = row.length > 22 ? row[22].toString() : "NORMAL";
      final severityNew = row.length > 23 ? row[23].toString() : "LOW";

      String finalStatus = "Normal";
      String finalLeak = "NO";

      if ((f1 + f2 + f3) / 3 < 0.1) {
        finalStatus = "No Flow";
        finalLeak = "NO";
      } else if (zoneNew != "NORMAL") {
        finalStatus = severityNew == "HIGH" ? "Leak Detected" : "Flow Imbalance";
        finalLeak = "YES";
      }

      String finalReason = zoneNew == "NORMAL"
          ? "Stable flow pattern"
          : "$severityNew issue detected at $zoneNew";

      return {
        "timestamp": row[0].toString(),
        "flow1": f1,
        "flow2": f2,
        "flow3": f3,
        "diff12": d12,
        "diff23": d23,
        "zone": zoneNew,
        "severity": severityNew,
        "status": finalStatus,
        "reason": finalReason,
        "leak": finalLeak,
        "leak_probability": zoneNew == "NORMAL" ? 0.10 : 0.85,
      };
    }).toList();

    if (allData.isNotEmpty) {
      updateUIFromRow(allData.first);
      startLocalStreaming();
    }
  }

  void startLocalStreaming() {
    timer?.cancel();
    timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (allData.isEmpty) return;

      updateUIFromRow(allData[currentIndex]);

      currentIndex++;
      if (currentIndex >= allData.length) {
        currentIndex = 0;
      }
    });
  }

  void updateUIFromRow(Map<String, dynamic> data) {
    setState(() {
      leak = data["leak"];
      severity = data["severity"];
      zone = data["zone"];
      status = data["status"];
      reason = data["reason"];
      probability = (data["leak_probability"] as num).toDouble();

      flow1 = (data["flow1"] as num).toDouble();
      flow2 = (data["flow2"] as num).toDouble();
      flow3 = (data["flow3"] as num).toDouble();
      diff12 = (data["diff12"] as num).toDouble();
      diff23 = (data["diff23"] as num).toDouble();

      final avgFlow = (flow1 + flow2 + flow3) / 3;
      flowHistory.add(avgFlow);
      if (flowHistory.length > 15) {
        flowHistory.removeAt(0);
      }
    });

    if ((severity == "HIGH" || severity == "MEDIUM") && zone != "NORMAL") {
      if (!alertShown) {
        alertShown = true;
      }
    } else {
      alertShown = false;
    }
  }

  Color getRiskColor() {
    if (severity == "HIGH" || leak == "YES") return AppColors.red;
    if (severity == "MEDIUM") return AppColors.orange;
    return AppColors.green;
  }

  Widget buildChart() {
    if (flowHistory.isEmpty) {
      return const SizedBox(
        height: 180,
        child: Center(
          child: Text(
            "Waiting for chart data...",
            style: TextStyle(color: AppColors.textSecondary),
          ),
        ),
      );
    }

    return SizedBox(
      height: 180,
      child: LineChart(
        LineChartData(
          minY: 0,
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            getDrawingHorizontalLine: (value) => FlLine(
              color: Colors.white.withOpacity(0.06),
              strokeWidth: 1,
            ),
          ),
          borderData: FlBorderData(show: false),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                getTitlesWidget: (value, meta) => Text(
                  value.toStringAsFixed(0),
                  style: const TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 10,
                  ),
                ),
              ),
            ),
            rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          lineBarsData: [
            LineChartBarData(
              isCurved: true,
              color: AppColors.primary,
              barWidth: 3,
              dotData: FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: AppColors.primary.withOpacity(0.15),
              ),
              spots: List.generate(
                flowHistory.length,
                    (index) => FlSpot(index.toDouble(), flowHistory[index]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget statCard(String title, String value) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.card,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(color: AppColors.textSecondary)),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget flowCard(String title, double value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.card,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: TextStyle(color: color)),
            const SizedBox(height: 8),
            Text(
              value.toStringAsFixed(2),
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 24,
              ),
            ),
            const Text("L/min", style: TextStyle(color: AppColors.textSecondary)),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    timer?.cancel();
    tts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.card,
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: getRiskColor().withOpacity(0.5)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Hydro Sense Demo",
                      style: TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      leak == "YES" ? "Leak Detected" : "System Normal",
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(reason, style: const TextStyle(color: AppColors.textSecondary)),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              Row(
                children: [
                  statCard("Severity", severity),
                  const SizedBox(width: 12),
                  statCard("Zone", zone),
                ],
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  statCard("Status", status),
                  const SizedBox(width: 12),
                  statCard("Probability", probability.toStringAsFixed(2)),
                ],
              ),
              const SizedBox(height: 18),

              Row(
                children: [
                  flowCard("Flow 1", flow1, AppColors.primary),
                  const SizedBox(width: 12),
                  flowCard("Flow 2", flow2, AppColors.green),
                  const SizedBox(width: 12),
                  flowCard("Flow 3", flow3, AppColors.yellow),
                ],
              ),
              const SizedBox(height: 18),

              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.card,
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: AppColors.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Live Flow Trend",
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 17,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    buildChart(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}