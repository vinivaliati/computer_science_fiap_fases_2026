// SIFSM - Aurora Siger | Fase 7 - circuito para o Tinkercad (Arduino Uno)
// RISCO = (B E) OU (C T) | ALERTA = B OU C OU T | NORMAL = NÃO ALERTA

const int PIN_BATERIA = A0;      // potenciômetro: nível da bateria (0-100 %)
const int PIN_TEMP = A1;         // sensor TMP36: temperatura
const int PIN_CONSUMO = A2;      // potenciômetro: consumo em % da média (0-200 %)
const int PIN_ESSENCIAL = 2;     // chave: 1 = módulo essencial
const int LED_VERMELHO = 8;      // RISCO
const int LED_AMARELO = 9;       // ALERTA
const int LED_VERDE = 10;        // NORMAL
const int BUZZER = 11;           // RISCO

const float LIMITE_BATERIA = 25.0;   // %
const float LIMITE_TEMP = 26.0;      // graus Celsius
const float LIMITE_CONSUMO = 120.0;  // % da média do módulo

void setup() {
  pinMode(PIN_ESSENCIAL, INPUT);
  pinMode(LED_VERMELHO, OUTPUT);
  pinMode(LED_AMARELO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // 1) Ler sensores e converter para unidades reais
  float bateria = analogRead(PIN_BATERIA) * 100.0 / 1023.0;
  float consumo = analogRead(PIN_CONSUMO) * 200.0 / 1023.0;
  float tensao = analogRead(PIN_TEMP) * 5.0 / 1024.0;
  float temperatura = (tensao - 0.5) * 100.0;      // TMP36: 10 mV por grau, 0,5 V a 0 C

  // 2) Variáveis booleanas
  bool B = bateria < LIMITE_BATERIA;
  bool E = digitalRead(PIN_ESSENCIAL) == HIGH;
  bool C = consumo > LIMITE_CONSUMO;
  bool T = temperatura > LIMITE_TEMP;

  // 3) Expressões lógicas
  bool risco = (B && E) || (C && T);
  bool alerta = B || C || T;

  // 4) Atuadores
  digitalWrite(LED_VERMELHO, risco);
  digitalWrite(LED_AMARELO, alerta);
  digitalWrite(LED_VERDE, !alerta);
  if (risco) tone(BUZZER, 1000); else noTone(BUZZER);

  // 5) Monitor serial 
  Serial.print("Bat "); Serial.print(bateria);
  Serial.print("% | Temp "); Serial.print(temperatura);
  Serial.print("C | Cons "); Serial.print(consumo);
  Serial.print("% | B"); Serial.print(B); Serial.print(" E"); Serial.print(E);
  Serial.print(" C"); Serial.print(C); Serial.print(" T"); Serial.print(T);
  Serial.println(risco ? " -> RISCO" : (alerta ? " -> ALERTA" : " -> NORMAL"));
  delay(500);
}
