import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:math';
import 'package:simple_timer/simple_timer.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
          primarySwatch: Colors.purple,
          accentColor: Colors.amber,
          fontFamily: 'Quicksand',
          textTheme: ThemeData.light().textTheme.copyWith(
              headline6: TextStyle(
                  fontFamily: 'OpenSans',
                  fontSize: 18,
                  fontWeight: FontWeight.bold)),
          appBarTheme: AppBarTheme(
            textTheme: ThemeData.light().textTheme.copyWith(
                    headline6: TextStyle(
                  fontFamily: 'OpenSans',
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                )),
          )),
      home: MyHomePage(
        title: 'Servo-blik',
      ),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);
  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage>
    with SingleTickerProviderStateMixin {
  String _code = 'None';
  late TimerController _timerController;
  var client = http.Client();

  @override
  void initState() {
    super.initState();
    // initialize controller
    _timerController = TimerController(this);
    _timerController.duration = Duration(seconds: 50);
  }

  @override
  void dispose() {
    super.dispose();
    // dispose controller
    _timerController.dispose();
  }

  Future<void> sendCode(String code) async {
    var url = Uri.parse('http://192.168.1.16:8080');
    var response = await http.post(url, body: this._code.toString());
    print('Response status: ${response.statusCode}');
    print('Response body: ${response.body}');
  }

  void generateNewCode() async {
    String tmpCode = '';
    Random rng = new Random();
    for (int i = 6; i > 0; i--) {
      tmpCode += rng.nextInt(10).toString();
    }
    setState(() {
      this._code = tmpCode;
      _timerController.start();
      sendCode(this._code);
    });
  }

  void resetCode() {
    setState(() {
      this._code = 'Time';
      _timerController.reset();
      sendCode(this._code);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: this._code != 'None' && this._code != 'Time'
            ? Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: EdgeInsets.all(15),
                    child: SimpleTimer(
                      controller: _timerController,
                      duration: Duration(seconds: 20),
                      progressIndicatorColor: Colors.purple,
                      onEnd: resetCode,
                    ),
                  ),
                  Text(
                    "Code: ${this._code}",
                    style: TextStyle(fontSize: 45, fontWeight: FontWeight.bold),
                  ),
                ],
              )
            : Container(
                child: ElevatedButton(
                  onPressed: () => generateNewCode(),
                  child: Text('Generate new Code!'),
                ),
              ),
      ),
    ); // This trailing comma makes auto-formatting nicer for build methods.
  }
}
